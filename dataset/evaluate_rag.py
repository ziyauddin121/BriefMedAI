import os
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

DATASET_PATH = os.path.join(os.path.dirname(__file__), "eval_dataset.json")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "eval_results.json")
SUMMARY_PATH = os.path.join(os.path.dirname(__file__), "eval_summary.md")

BACKEND_GENERATE_URL = "http://127.0.0.1:5000/stream_generate"
BACKEND_CHAT_URL = "http://127.0.0.1:5000/stream_chat"

def get_gemini_api_key():
    """Retrieve Gemini API Key from environment or prompt the user."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("\n[!] GEMINI_API_KEY not found in environment or .env file.")
        key = input("Enter your Gemini API Key: ").strip()
    return key

def get_active_gemini_model(api_key: str) -> str:
    """Finds the best high-quota model available (500 RPD tier)."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            models_data = res.json().get("models", [])
            supported = [
                m["name"].replace("models/", "") 
                for m in models_data 
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            # Prioritize high-quota models (500 Requests/Day)
            for candidate in ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-flash-latest"]:
                if candidate in supported:
                    return candidate
            if supported:
                return supported[0]
    except Exception:
        pass
    return "gemini-3.1-flash-lite"


def call_gemini_judge(api_key: str, doc_context: str, question: str, ground_truth: str, generated_answer: str, model_name: str = "gemini-3.1-flash-lite", retries: int = 3) -> dict:
    """
    Sends Source Document, Ground Truth, and Generated Answer to Gemini to act as a Context-Aware LLM Judge.
    Uses standard REST API call (no external SDK dependency required).
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    judge_prompt = f"""You are an expert medical AI evaluation judge assessing a RAG system's clinical answer.

[Source Medical Document]
{doc_context}

[Question Asked]
{question}

[Reference Ground Truth]
{ground_truth}

[Model Estimated Answer]
{generated_answer}

[Evaluation Rules]
1. PASS (Score 1): If the Model's Estimated Answer is factually accurate, answers the question, and is fully grounded in the Source Medical Document.
2. Note on Extra Details: If the Model Answer includes additional true facts from the Source Document (e.g., additional true vital signs like RR or Temp that are in the Source Document), this is ACCURATE and must be PASSED. Do not penalize for true information grounded in the source text.
3. Note on Formatting: Ignore AI disclaimers, Markdown formatting, and entity tags like [[MED|...]] or [[DIAG|...]].
4. FAIL (Score 0): Only fail if the model hallucinates numbers/dosages NOT in the source text, makes false claims, contradicts the source report, or fails to answer the question.

[Output Format]
You MUST respond with a valid JSON object ONLY (no markdown formatting, no backticks, no extra text):
{{
  "score": 1,
  "verdict": "PASS",
  "reason": "Brief one-sentence explanation of why it passed or failed"
}}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": judge_prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.0,
            "responseMimeType": "application/json"
        }
    }

    headers = {"Content-Type": "application/json"}

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                res_json = response.json()
                raw_text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
                # Clean up if any codeblock markdown is returned
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                return json.loads(raw_text)
            elif response.status_code == 429:
                print(" [Rate Limited, waiting 5s...]")
                time.sleep(5)
            elif response.status_code == 404 and model_name != "gemini-flash-latest":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
                time.sleep(1)
            else:
                print(f" [Gemini API Error {response.status_code}: {response.text}]")
                time.sleep(2)
        except Exception as e:
            print(f" [Attempt {attempt+1} failed: {e}]")
            time.sleep(2)

    return {"score": 0, "verdict": "FAIL", "reason": "Judge evaluation failed or timed out"}


def ingest_document_to_briefmed(doc_text: str) -> bool:
    """Simulates uploading the medical report to BriefMed AI (/stream_generate)."""
    try:
        response = requests.post(
            BACKEND_GENERATE_URL,
            data={"report_text": doc_text},
            stream=True,
            timeout=120
        )
        if response.status_code == 200:
            # Consume stream to ensure vectorstore and active_retriever are built
            for line in response.iter_lines():
                pass
            return True
        return False
    except Exception as e:
        print(f" [Error connecting to Flask backend: {e}]")
        return False


def query_briefmed_chat(question: str) -> str:
    """Asks a question to BriefMed AI (/stream_chat) and collects the streaming response."""
    try:
        response = requests.post(
            BACKEND_CHAT_URL,
            json={"question": question, "history": []},
            stream=True,
            timeout=120
        )
        answer = ""
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if data.get('type') == 'result':
                            answer = data.get('content', '')
                        elif data.get('type') == 'content':
                            answer += data.get('text', '')
                        elif data.get('type') == 'error':
                            return f"ERROR: {data.get('message')}"
                    except Exception:
                        pass
            return answer.strip()
        return "ERROR: HTTP Request Failed"
    except Exception as e:
        return f"ERROR: {e}"


def run_evaluation():
    print("=" * 70)
    print(" 🏥 BRIEFMED AI - AUTOMATED RAG ACCURACY EVALUATION PIPELINE")
    print("=" * 70)

    gemini_key = get_gemini_api_key()
    if not gemini_key:
        print("[-] Evaluation aborted: No Gemini API Key provided.")
        return

    active_model = get_active_gemini_model(gemini_key)
    print(f"[+] Detected active Gemini judge model: {active_model}")

    if not os.path.exists(DATASET_PATH):
        print(f"[-] Dataset file not found at {DATASET_PATH}")
        return

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    total_docs = len(dataset)
    print(f"\n[+] Loaded {total_docs} medical reports from dataset.")
    
    user_choice = input(f"How many reports do you want to evaluate? (1-{total_docs}, default 5 for quick test): ").strip()
    num_to_eval = int(user_choice) if user_choice.isdigit() and 1 <= int(user_choice) <= total_docs else 5

    print(f"\n[*] Starting evaluation on {num_to_eval} reports ({num_to_eval * 5} questions)...")
    print("[*] Please ensure `python app.py` is running in another terminal!\n")

    results = []
    total_passed = 0
    total_questions = 0
    category_stats = {}

    for doc_idx, doc in enumerate(dataset[:num_to_eval], start=1):
        doc_id = doc.get("document_id", f"DOC-{doc_idx}")
        category = doc.get("category", "General")
        doc_text = doc.get("document_text", "")
        evaluations = doc.get("evaluations", [])

        if category not in category_stats:
            category_stats[category] = {"total": 0, "passed": 0}

        print(f"\n[{doc_idx}/{num_to_eval}] Ingesting {doc_id} ({category})...")
        ingested = ingest_document_to_briefmed(doc_text)
        if not ingested:
            print(f"  [!] Failed to ingest {doc_id}. Is Flask app running on port 5000?")
            continue

        doc_result = {
            "document_id": doc_id,
            "category": category,
            "questions": []
        }

        for q in evaluations:
            total_questions += 1
            category_stats[category]["total"] += 1

            question_text = q["question"]
            ground_truth = q["ground_truth"]

            print(f"  -> Q{q['q_id']}: {question_text[:50]}...")
            
            generated_answer = query_briefmed_chat(question_text)
            
            # 2. Score via Context-Aware Gemini Judge
            judge_res = call_gemini_judge(gemini_key, doc_text, question_text, ground_truth, generated_answer, model_name=active_model)
            score = judge_res.get("score", 0)
            verdict = judge_res.get("verdict", "FAIL")
            reason = judge_res.get("reason", "")

            if score == 1:
                total_passed += 1
                category_stats[category]["passed"] += 1
                print(f"     ✅ {verdict}: {reason}")
            else:
                print(f"     ❌ {verdict}: {reason}")

            doc_result["questions"].append({
                "q_id": q["q_id"],
                "question": question_text,
                "ground_truth": ground_truth,
                "generated_answer": generated_answer,
                "score": score,
                "verdict": verdict,
                "reason": reason
            })

            # Small pause to respect Gemini rate limits
            time.sleep(1)

        results.append(doc_result)

    # Calculate overall metrics
    overall_accuracy = (total_passed / total_questions * 100) if total_questions > 0 else 0.0

    print("\n" + "=" * 70)
    print(" 📊 EVALUATION SUMMARY RESULTS")
    print("=" * 70)
    print(f"Total Questions Evaluated: {total_questions}")
    print(f"Passed: {total_passed} | Failed: {total_questions - total_passed}")
    print(f"Overall RAG Accuracy: {overall_accuracy:.2f}%")
    print("\nAccuracy by Specialty:")
    for cat, stats in category_stats.items():
        cat_acc = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
        print(f" - {cat:20}: {stats['passed']}/{stats['total']} ({cat_acc:.1f}%)")

    # Save detailed JSON output
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "overall_accuracy_percentage": round(overall_accuracy, 2),
            "total_questions": total_questions,
            "total_passed": total_passed,
            "category_breakdown": category_stats,
            "detailed_reports": results
        }, f, indent=2, ensure_ascii=False)

    # Collect passed and failed questions for the summary
    failed_cases = []
    passed_cases = []

    for doc in results:
        for q in doc["questions"]:
            case_info = {
                "doc_id": doc["document_id"],
                "category": doc["category"],
                "q_id": q["q_id"],
                "question": q["question"],
                "ground_truth": q["ground_truth"],
                "generated_answer": q["generated_answer"],
                "verdict": q["verdict"],
                "reason": q["reason"]
            }
            if q["score"] == 1:
                passed_cases.append(case_info)
            else:
                failed_cases.append(case_info)

    # Save Markdown Summary
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write("# 🏥 BriefMed AI - RAG Accuracy & Evaluation Report\n\n")
        f.write(f"**Date Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 📊 Executive Summary\n\n")
        f.write(f"- **Overall Accuracy:** `{overall_accuracy:.2f}%`\n")
        f.write(f"- **Total Questions Evaluated:** `{total_questions}`\n")
        f.write(f"- **Passed (Faithful & Accurate):** `{total_passed}`\n")
        f.write(f"- **Failed (Hallucinated / Inaccurate):** `{total_questions - total_passed}`\n\n")
        
        f.write("## 🩺 Specialty Breakdown\n\n")
        f.write("| Medical Specialty | Passed | Total | Accuracy (%) |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for cat, stats in category_stats.items():
            cat_acc = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
            f.write(f"| **{cat}** | {stats['passed']} | {stats['total']} | **{cat_acc:.1f}%** |\n")
        
        if failed_cases:
            f.write("\n\n## ❌ Error Analysis & Failed Cases\n")
            f.write("Below are the specific questions where the model failed due to missing facts or numerical discrepancy:\n\n")
            for idx, fc in enumerate(failed_cases, start=1):
                f.write(f"### {idx}. [{fc['doc_id']} - {fc['category']}] Q{fc['q_id']}: {fc['question']}\n\n")
                f.write(f"- **🎯 Ground Truth (Actual):**\n  > {fc['ground_truth']}\n\n")
                f.write(f"- **🤖 BriefMed AI Output (Estimated):**\n  > {fc['generated_answer']}\n\n")
                f.write(f"- **⚖️ Judge Verdict & Reason:**\n  > ❌ **{fc['verdict']}**: {fc['reason']}\n\n")
                f.write("---\n\n")
        else:
            f.write("\n\n## 🎉 Zero Errors Detected!\nAll evaluated questions achieved 100% faithfulness and clinical accuracy against the ground truth.\n\n")

        if passed_cases:
            f.write("## ✅ Sample Verified Answers (Actual vs. Estimated)\n\n")
            for idx, pc in enumerate(passed_cases[:3], start=1):
                f.write(f"### Example {idx}: [{pc['doc_id']} - {pc['category']}] {pc['question']}\n\n")
                f.write(f"- **🎯 Ground Truth (Actual):**\n  > {pc['ground_truth']}\n\n")
                f.write(f"- **🤖 BriefMed AI Output (Estimated):**\n  > {pc['generated_answer']}\n\n")
                f.write(f"- **⚖️ Judge Reason:**\n  > ✅ **{pc['verdict']}**: {pc['reason']}\n\n")
                f.write("---\n\n")

    print(f"\n[+] Detailed results saved to: {RESULTS_PATH}")
    print(f"[+] Rich Markdown summary saved to: {SUMMARY_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    run_evaluation()

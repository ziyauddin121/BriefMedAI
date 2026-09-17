import os
import requests
import json
import time
from dotenv import load_dotenv

# Load environment variables (.env)
load_dotenv()

def test_gemini():
    print("=" * 60)
    print(" 🧪 TESTING GOOGLE GEMINI API CONNECTION")
    print("=" * 60)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = input("Enter your Gemini API Key: ").strip()

    if not api_key:
        print("[-] Error: No API key provided.")
        return

    print(f"\n[1] Checking available models for your API key...")
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        res = requests.get(list_url, timeout=15)
        if res.status_code == 200:
            models = res.json().get("models", [])
            print(f"    Found {len(models)} models available:")
            valid_models = []
            for m in models:
                name = m.get("name", "")
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    clean_name = name.replace("models/", "")
                    valid_models.append(clean_name)
                    print(f"     * {clean_name}")
        else:
            print(f"    [-] Failed to list models. Status: {res.status_code}, Body: {res.text}")
            valid_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]
    except Exception as e:
        print(f"    [-] Error listing models: {e}")
        valid_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]

    candidates_to_test = ["gemini-flash-latest", "gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-3.6-flash", "gemini-3.7-flash"]
    
    prompt = "Reply in 1 short sentence: Confirm you are working."
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    headers = {"Content-Type": "application/json"}

    print("\n[2] Testing candidate models for fastest response...")
    working_model = None

    for model_name in candidates_to_test:
        if model_name not in valid_models and valid_models:
            continue
        print(f"    -> Testing '{model_name}'...", end=" ", flush=True)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            start_t = time.time()
            response = requests.post(url, headers=headers, json=payload, timeout=40)
            elapsed = time.time() - start_t
            if response.status_code == 200:
                data = response.json()
                reply = data['candidates'][0]['content']['parts'][0]['text'].strip()
                print(f"✅ SUCCESS ({elapsed:.2f}s) -> \"{reply}\"")
                working_model = model_name
                break
            else:
                print(f"❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Error/Timeout ({e})")

    if working_model:
        print("\n" + "=" * 60)
        print(f" 🎉 Recommended Working Model: '{working_model}'")
        print("=" * 60)
    else:
        print("\n[-] All candidates timed out. Please check your internet connection or firewall.")


if __name__ == "__main__":
    test_gemini()

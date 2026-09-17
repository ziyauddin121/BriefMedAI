from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

from pypdf import PdfReader
import os
import json
import re
import time
from datetime import datetime


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever, ParentDocumentRetriever, ContextualCompressionRetriever
# EnsembeleRetriever -> combines the results of multiple retrievers into one set of documents.
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.storage import InMemoryStore
import logging
from dotenv import load_dotenv
from langchain_text_splitters import TextSplitter

class SemanticChunkerWrapper(TextSplitter):
    def __init__(self, chunker):
        super().__init__(chunk_size=1, chunk_overlap=0) 
        self.chunker = chunker

    def split_text(self, text: str):#handles raw strings
        if not text or not text.strip():
            return []
        try:
            chunks = self.chunker.split_text(text)
            chunks = [c for c in chunks if c.strip()]
            if not chunks:
                return [text]
            return chunks
        except Exception:
            return [text]

    def split_documents(self, documents):#handles langchain document objects
        if not documents:
            return []
        try:
            chunks = self.chunker.split_documents(documents)
            chunks = [c for c in chunks if c.page_content and c.page_content.strip()]
            if not chunks:
                return documents
            return chunks
        except Exception:
            return documents


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret')
CORS(app) # Enable CORS for all routes


# Define the prompt templates
medical_prompt_template = """
You are a medical report summarization assistant.

Your task is to generate a structured summary using ONLY the information provided in the Context.

IMPORTANT RULES:
1. Use only information explicitly present in the Context.
2. Do not invent, assume, infer, or hallucinate patient information.
3. Do not provide a diagnosis that is not explicitly supported by the Context.
4. Do not introduce medications, procedures, symptoms, test results, or recommendations that are not present in the Context.
5. Do not repeat these instructions in your response.
6. Do not output HTML.
7. Use plain text and Markdown only.
8. Use the following shortcodes for medical entities:
   - Medication: [[MED|name]]
   - Diagnosis: [[DIAG|name]]
   - Procedure: [[PROC|name]]
9. If a section is not mentioned in the Context, write "Not mentioned in the report."
10. Preserve important numerical values, dates, units, medication doses, and test results exactly as stated in the Context.
11. Do not change the meaning of the medical report.
12. Keep the summary concise but complete.
13. This is a summarization task, not a medical decision-making task.

Use EXACTLY this structure:

**Urgency Level:** [Routine / Urgent / Critical]

**Patient Details:**
[Name, age, gender, and other relevant identifying information if available]

**Medical History:**
- Relevant past illnesses:
- Chronic conditions:
- Previous relevant procedures:

**Symptoms and Diagnosis:**
- Symptoms:
- Diagnosis:

**Investigations and Findings:**
- Relevant laboratory results:
- Imaging findings:
- Other important findings:

**Treatment and Recommendations:**
- Medications:
- Procedures:
- Recommendations:

**Current Status:**
[Brief summary of the patient's current condition based only on the Context]

Context:
{context}

Report:
"""


# Initialize embeddings and cross-encoder globally to avoid reloading on each request
try:
    embeddings = HuggingFaceEmbeddings(model_name="NeuML/pubmedbert-base-embeddings")
except Exception as e:
    logging.error(f"Error initializing embeddings: {e}")
    embeddings = None

try:
    cross_encoder = HuggingFaceCrossEncoder(model_name="ncbi/MedCPT-Cross-Encoder")
except Exception as e:
    logging.error(f"Error initializing cross_encoder: {e}")
    cross_encoder = None

active_retriever = None

@app.route('/stream_generate', methods=['POST'])
def stream_generate():
    text_input = request.form.get('report_text')
    uploaded_file = request.files.get('file')

    # Handle file upload if present
    if uploaded_file and uploaded_file.filename != '':
        try:
            if uploaded_file.filename.endswith('.pdf'):
                pdf_reader = PdfReader(uploaded_file)
                text_input = ""
                for page in pdf_reader.pages:
                    text_input += page.extract_text() + "\n"
            elif uploaded_file.filename.endswith('.txt'):
                text_input = uploaded_file.read().decode('utf-8')
        except Exception as e:
             return jsonify({'error': f"Error reading file: {e}"})
    
    if not text_input or not text_input.strip():
        return jsonify({'error': "No text provided or text is empty"})

    def generate():
        yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] INITIALIZING SYSTEM PROTOCOLS..."}) + "\n"
        time.sleep(0.5)
        
        if not embeddings:
            yield json.dumps({'type': 'error', 'message': "Embeddings model not initialized."}) + "\n"
            return
            
        try:

            # Clear previous collection if re-ingesting
            try:
                Chroma(collection_name="temp_collection", embedding_function=embeddings).delete_collection()
            except Exception:
                pass

            global active_retriever
            if active_retriever:
                active_retriever = None

            # Step 1: Document Processing
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] INGESTING DOCUMENT DATASHEET..."}) + "\n"
            documents = [Document(page_content=text_input)]
            time.sleep(0.3)
            
            # Step 2: Semantic Chunking & Parent Documents
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] PARTITIONING DATA STREAMS (SEMANTIC CHUNKING)..."}) + "\n"
            parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
            child_splitter = SemanticChunkerWrapper(SemanticChunker(embeddings))
            store = InMemoryStore()
            
            vectorstore = Chroma(
                collection_name="temp_collection",
                embedding_function=embeddings
            )
            
            parent_retriever = ParentDocumentRetriever(
                vectorstore=vectorstore,
                docstore=store,
                child_splitter=child_splitter,
                parent_splitter=parent_splitter
            )
            
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] GENERATING VECTOR EMBEDDINGS (HuggingFace)..."}) + "\n"
            parent_retriever.add_documents(documents)
            time.sleep(0.5)

            # Step 3: Hybrid Search Setup
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] INITIALIZING BM25 HYBRID SEARCH ENSEMBLE..."}) + "\n"
            bm25_docs = parent_splitter.split_documents(documents)
            bm25_retriever = BM25Retriever.from_documents(bm25_docs)
            bm25_retriever.k = 3
            
            ensemble_retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, parent_retriever], weights=[0.5, 0.5]
            )

            # Step 3.5: Post-Retrieval Re-ranking
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] PREPARING MEDCPT RE-RANKER..."}) + "\n"
            ce_model = cross_encoder if cross_encoder is not None else HuggingFaceCrossEncoder(model_name="ncbi/MedCPT-Cross-Encoder")
            compressor = CrossEncoderReranker(model=ce_model, top_n=3)
            active_retriever = ContextualCompressionRetriever(
                base_compressor=compressor, base_retriever=ensemble_retriever
            )
            time.sleep(0.5)

            # Step 4: Model Connection
            model_name = "qwen2.5:3b"
            
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] CONNECTING TO LOCAL OLLAMA NODE (127.0.0.1)..."}) + "\n"
            
            selected_url = os.getenv('OLLAMA_BASE_URL', "http://127.0.0.1:11434")
            
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] ESTABLISHING SECURE UPLINK..."}) + "\n"
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] MODEL SELECTED: {model_name}"}) + "\n"
            
            llm = Ollama(
                base_url=selected_url,
                model=model_name,
                temperature=0.0
            )


            prompt = PromptTemplate(
                template=medical_prompt_template,
                input_variables=["context"]
            )

            rag_chain = (
                {"context": active_retriever | format_docs}
                | prompt
                | llm
                | StrOutputParser()
            )

            # Step 5: Inference
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] RUNNING INFERENCE SEQUENCE..."}) + "\n"
            result_text = rag_chain.invoke("Create a full medical summary")
            
            # Extract Urgency Level
            urgency_match = re.search(r'\*\*Urgency Level:\*\*\s*(Routine|Urgent|Critical)', result_text, re.IGNORECASE)
            urgency_level = urgency_match.group(1).capitalize() if urgency_match else "Routine"
            
            # Cleanup
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] SAVING CONTEXT FOR CHAT SESSION..."}) + "\n"
            
            # Final Result
            yield json.dumps({'type': 'result', 'content': result_text, 'urgency': urgency_level}) + "\n"
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] TASK COMPLETED SUCCESSFULLY."}) + "\n"

        except Exception as e:
            logging.error(f"Error generating summary: {e}")
            yield json.dumps({'type': 'error', 'message': f"CRITICAL FAILURE: {str(e)}"}) + "\n"

    return Response(stream_with_context(generate()), mimetype='application/json')

chat_prompt_template = """
You are a medical document assistant.

Answer the user's question using ONLY the information contained in the Context.

RULES:

1. Answer only what the user asked.
2. Use only information present in the Context.
3. Do not guess, speculate, or infer information that cannot be directly determined from the Context.
4. You may make a direct, medically established conclusion when the Context contains the specific value or finding required to determine it. For example, if BMI is provided, you may determine whether the person is underweight, normal weight, overweight, or obese according to standard BMI categories.
5. Do not make broader conclusions from the Context unless they are directly supported by a stated finding or an appropriate value. For example, do not infer general health, fitness, disease risk, or other conditions merely from BMI.
6. If the answer is not present in the Context and cannot be directly determined from information explicitly present in the Context, respond EXACTLY:
   "I don't have enough information from the report to answer that."
7. Keep answers concise and direct.
8. For simple factual questions such as name, age, gender, marital status, medications, or diagnosis, answer in 1–2 sentences.
9. Do not provide additional lab values, assessments, recommendations, or treatment advice unless explicitly requested.
10. Preserve medical values, units, medication doses, and dates exactly as they appear in the Context.
11. Do not contradict information in the Context.
12. Do not output HTML.
13. Use these shortcodes for medical entities:
    - Medication: [[MED|name]]
    - Diagnosis: [[DIAG|name]]
    - Procedure: [[PROC|name]]
14. End every response with:
    "Disclaimer: I am an AI. Always consult a qualified doctor."

EXAMPLES:

Question:
What medications is the patient taking?

Answer:
The patient is taking [[MED|Amlodipine]] 5 mg once daily and [[MED|Losartan]] 50 mg once daily.
Disclaimer: I am an AI. Always consult a qualified doctor.

Question:
Is the patient married?

Answer:
The report does not mention the patient's marital status.
Disclaimer: I am an AI. Always consult a qualified doctor.

Question:
What is the patient's HbA1c?

Answer:
The patient's HbA1c is 7.8%.
Disclaimer: I am an AI. Always consult a qualified doctor.

Question:
What is the patient's blood pressure?

Answer:
The report does not mention the patient's blood pressure.
Disclaimer: I am an AI. Always consult a qualified doctor.

Context:
{context}

Question:
{question}

Answer:
"""
@app.route('/stream_chat', methods=['POST'])
def stream_chat():
    global active_retriever
    
    data = request.json
    question = data.get('question')
    history = data.get('history', [])
    
    def generate():
        if not active_retriever:
            yield json.dumps({'type': 'error', 'message': "No medical report loaded. Please configure the summary protocol first."}) + "\n"
            return
            
        try:
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] ANALYZING DOCUMENT CONTEXT..."}) + "\n"
            
            model_name = "qwen2.5:3b"
            selected_url = os.getenv('OLLAMA_BASE_URL', "http://127.0.0.1:11434")
            llm = Ollama(base_url=selected_url, model=model_name, temperature=0.0)
            
            formatted_history = ""
            for msg in history:
                role = "Human" if msg['role'] == 'user' else "AI"
                formatted_history += f"{role}: {msg['content']}\n"
                
            prompt = PromptTemplate(
                template=chat_prompt_template,
                input_variables=["context", "question"]
            )
            
            rag_chain = (
                {"context": active_retriever | format_docs, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            
            custom_question = ""
            if formatted_history:
                custom_question = f"Previous Conversation History:\n{formatted_history}\n\n"
            custom_question += f"{question}"
            
            result_text = rag_chain.invoke(custom_question)
            
            if "disclaimer" not in result_text.lower() and "consult a" not in result_text.lower():
                result_text += "\n\n**Disclaimer:** I am an AI medical assistant. This tool may make mistakes. Always consult a qualified medical professional for final advice."
            
            yield json.dumps({'type': 'result', 'content': result_text}) + "\n"
            
        except Exception as e:
            logging.error(f"Error generating chat: {e}")
            yield json.dumps({'type': 'error', 'message': f"CRITICAL FAILURE: {str(e)}"}) + "\n"

    return Response(stream_with_context(generate()), mimetype='application/json')

translate_prompt_template = """
You are a medical terminology explanation assistant.

Explain the following medical term in very simple language that a 10-year-old could understand.

RULES:
1. Use only 2–3 sentences.
2. Use simple everyday language.
3. Avoid unnecessary medical jargon.
4. Do not provide treatment or medical advice.
5. Explain what the term means and, when useful, what it generally relates to.
6. If the term has multiple common meanings, give the medical meaning relevant to healthcare.
7. Do not mention these instructions in your response.

Medical Term:
{term}

Explanation:
"""

@app.route('/explain_term', methods=['POST'])
def explain_term():
    data = request.json
    term = data.get('term')
    
    if not term:
        return jsonify({'error': "No term provided"}), 400
        
    def generate():
        try:
            yield json.dumps({'type': 'log', 'message': f"[{datetime.now().strftime('%H:%M:%S')}] TRANSLATING JARGON: {term}..."}) + "\n"
            
            model_name = "qwen2.5:3b"
            selected_url = os.getenv('OLLAMA_BASE_URL', "http://127.0.0.1:11434")
            llm = Ollama(base_url=selected_url, model=model_name, temperature=0.0)
            
            prompt = PromptTemplate(
                template=translate_prompt_template,
                input_variables=["term"]
            )
            chain = prompt | llm | StrOutputParser()
            result_text = chain.invoke({"term": term})
            
            yield json.dumps({'type': 'result', 'content': result_text}) + "\n"
        except Exception as e:
            logging.error(f"Error explaining term: {e}")
            yield json.dumps({'type': 'error', 'message': f"Failed to translate: {str(e)}"}) + "\n"

    return Response(stream_with_context(generate()), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5000)
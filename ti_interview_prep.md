# 🎯 BriefMed AI — Texas Instruments Interview Preparation Guide

> **Interview Date:** September 16, 2026
> **Company:** Texas Instruments (TI)
> **Project:** BriefMed AI — Medical Report Summarization & Q&A using Advanced RAG

---

## 📋 Table of Contents

1. [30-Second Elevator Pitch](#1-elevator-pitch)
2. [Full Architecture Walkthrough](#2-architecture)
3. [Code Deep-Dive (Line-by-Line)](#3-code-deep-dive)
4. [TI-Specific Interview Angles](#4-ti-specific-angles)
5. [Tough Questions TI Will Ask (+ Answers)](#5-tough-questions)
6. [Evaluation Pipeline (Your Secret Weapon)](#6-evaluation)
7. [Known Limitations & How You'd Fix Them](#7-limitations)
8. [Key Numbers to Memorize](#8-key-numbers)
9. [Quick Revision Cheatsheet](#9-cheatsheet)

---

## 1. 🗣️ Elevator Pitch (Memorize This) {#1-elevator-pitch}

> "BriefMed AI is a **privacy-first medical report summarization platform** that uses **Advanced RAG** (Retrieval-Augmented Generation) to convert complex medical documents into structured, readable summaries. What makes it special is that the entire pipeline — from embedding to inference — runs **100% locally** using Ollama with a Qwen2.5-3B model, so no patient data ever leaves the machine. I implemented a **3-stage retrieval pipeline**: Semantic Chunking with Parent-Child retrieval, Hybrid Search combining BM25 keyword matching with dense vector search, and a MedCPT Cross-Encoder Re-ranker for clinical accuracy. The system achieved **90% accuracy** across 250 questions spanning 15 medical specialties in automated evaluation using a Gemini-based LLM judge."

---

## 2. 🏗️ Full Architecture Walkthrough {#2-architecture}

### System Architecture Diagram (Know This Cold)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE (React/Vite)                       │
│  ┌─────────────────┐  ┌────────────────┐  ┌──────────────────────────────┐  │
│  │ Upload PDF/Text  │  │  Summary View  │  │ Chat Interface + Term Dialog │  │
│  └────────┬────────┘  └───────▲────────┘  └──────────────▲───────────────┘  │
│           │ HTTP POST         │ SSE Stream               │ HTTP POST        │
└───────────┼───────────────────┼──────────────────────────┼──────────────────┘
            │                   │                          │
    ┌───────▼───────┐   ┌──────┴──────┐           ┌───────┴───────┐
    │/stream_generate│   │/stream_chat │           │ /explain_term │
    └───────┬───────┘   └──────┬──────┘           └───────┬───────┘
            │                  │                          │
  ┌─────────▼──────────────────▼─────────┐        ┌──────▼──────────┐
  │       3-STAGE RAG RETRIEVAL          │        │ Direct LLM Call │
  │                                      │        │ (No RAG needed) │
  │  Stage 1: Parent-Child Retrieval     │        └──────┬──────────┘
  │    ├── SemanticChunker (child)       │               │
  │    ├── RecursiveTextSplitter(parent) │               │
  │    ├── ChromaDB (vector store)       │               │
  │    └── InMemoryStore (parent docs)   │               │
  │                                      │               │
  │  Stage 2: Hybrid Ensemble Search     │               │
  │    ├── BM25 (keyword/sparse) [50%]   │               │
  │    └── Vector Search (dense)  [50%]  │               │
  │                                      │               │
  │  Stage 3: Cross-Encoder Re-ranking   │               │
  │    └── MedCPT (top-3 selection)      │               │
  └─────────────┬────────────────────────┘               │
                │                                        │
        ┌───────▼────────────────────────────────────────▼───┐
        │            Ollama (Qwen2.5:3b)                     │
        │     Local LLM @ 127.0.0.1:11434                   │
        │     temperature=0.0 (deterministic)                │
        └────────────────────────────────────────────────────┘
```

### Data Flow for `/stream_generate`

| Step | What Happens | Code Location | Key Tech |
|------|-------------|---------------|----------|
| 1 | PDF/Text uploaded via FormData | [app.py L148-165](file:///c:/Learning/BriefMedAi/app.py#L148-L165) | PyPDF, Flask |
| 2 | Text wrapped as LangChain `Document` | [app.py L189](file:///c:/Learning/BriefMedAi/app.py#L189) | LangChain |
| 3 | Parent chunks (2000 chars) + Semantic child chunks created | [app.py L194-208](file:///c:/Learning/BriefMedAi/app.py#L194-L208) | `RecursiveCharacterTextSplitter`, `SemanticChunker` |
| 4 | Child chunks → PubMedBERT embeddings → ChromaDB | [app.py L198-211](file:///c:/Learning/BriefMedAi/app.py#L198-L211) | `HuggingFaceEmbeddings`, ChromaDB |
| 5 | Parent docs stored in `InMemoryStore` | [app.py L196](file:///c:/Learning/BriefMedAi/app.py#L196) | LangChain Storage |
| 6 | BM25 index created from parent-split docs | [app.py L216-218](file:///c:/Learning/BriefMedAi/app.py#L216-L218) | `rank_bm25` |
| 7 | `EnsembleRetriever` combines BM25 + Vector (50:50) | [app.py L220-222](file:///c:/Learning/BriefMedAi/app.py#L220-L222) | `EnsembleRetriever` |
| 8 | MedCPT Cross-Encoder re-ranks → top-3 | [app.py L226-230](file:///c:/Learning/BriefMedAi/app.py#L226-L230) | `CrossEncoderReranker` |
| 9 | Top-3 chunks → Prompt Template → Qwen2.5:3b | [app.py L250-264](file:///c:/Learning/BriefMedAi/app.py#L250-L264) | Ollama, LangChain LCEL |
| 10 | Regex extracts urgency, entities tagged `[[MED\|..]]` | [app.py L267-268](file:///c:/Learning/BriefMedAi/app.py#L267-L268) | Python `re` |
| 11 | Result streamed as JSON-Lines via `yield` | [app.py L274](file:///c:/Learning/BriefMedAi/app.py#L274) | Flask `stream_with_context` |

### Data Flow for `/stream_chat`

| Step | What Happens | Code Location |
|------|-------------|---------------|
| 1 | Question + chat history received as JSON | [app.py L352-354](file:///c:/Learning/BriefMedAi/app.py#L352-L354) |
| 2 | History formatted as "Human: ... AI: ..." string | [app.py L368-371](file:///c:/Learning/BriefMedAi/app.py#L368-L371) |
| 3 | Same `active_retriever` (from generate) used for context | [app.py L379](file:///c:/Learning/BriefMedAi/app.py#L379) |
| 4 | RAG chain invoked with history prepended to question | [app.py L385-390](file:///c:/Learning/BriefMedAi/app.py#L385-L390) |
| 5 | Disclaimer enforcement: if LLM forgot it, code appends it | [app.py L392-393](file:///c:/Learning/BriefMedAi/app.py#L392-L393) |

### Data Flow for `/explain_term`

| Step | What Happens | Code Location |
|------|-------------|---------------|
| 1 | Medical term received | [app.py L426](file:///c:/Learning/BriefMedAi/app.py#L426) |
| 2 | Direct LLM call — **NO RAG** (uses model's parametric knowledge) | [app.py L443-444](file:///c:/Learning/BriefMedAi/app.py#L443-L444) |
| 3 | Explains in "10-year-old language" | Prompt template L403-421 |

---

## 3. 🔬 Code Deep-Dive {#3-code-deep-dive}

### 3.1 The `SemanticChunkerWrapper` — Why It Exists

```python
class SemanticChunkerWrapper(TextSplitter):    # Line 34
    def __init__(self, chunker):
        super().__init__(chunk_size=1, chunk_overlap=0)  # ← Pydantic bypass
        self.chunker = chunker
```

**Why?** LangChain's `ParentDocumentRetriever` requires a `TextSplitter` subclass. But `SemanticChunker` is from `langchain_experimental` and doesn't conform to the Pydantic v2 validation that `TextSplitter` enforces. The wrapper:
1. Inherits from `TextSplitter` (satisfying the type check)
2. Sets `chunk_size=1, chunk_overlap=0` (dummy values — semantic chunking doesn't use fixed sizes)
3. Delegates actual splitting to the real `SemanticChunker`
4. Has fallback: if chunking fails, returns the original text unchanged

> **TI Interview Point:** This shows debugging ability. You hit a compatibility issue, understood the root cause (Pydantic validation), and solved it with the Adapter/Wrapper design pattern.

### 3.2 The LCEL (LangChain Expression Language) Chain

```python
rag_chain = (
    {"context": active_retriever | format_docs}  # Retriever → format
    | prompt                                       # Inject into template
    | llm                                          # Send to Qwen
    | StrOutputParser()                            # Parse output string
)
```

**How this works internally:**
1. `active_retriever | format_docs` → calls the retriever, pipes the docs through `format_docs` which joins them with `\n\n`
2. The dict `{"context": ...}` creates a `RunnableParallel` — the key `context` maps to the template's `{context}` variable
3. `| prompt` injects the context into the prompt template
4. `| llm` sends the formatted prompt to Ollama
5. `| StrOutputParser()` extracts the raw string from the LLM response

### 3.3 Streaming Architecture

```python
def generate():                                    # Generator function
    yield json.dumps({...}) + "\n"                 # JSON-Lines format
    # ... processing ...
    yield json.dumps({'type': 'result', ...}) + "\n"

return Response(stream_with_context(generate()),   # Flask streaming
                mimetype='application/json')
```

**Why `yield` not `return`?**
- `return` = blocks until everything is done → user sees loading screen for 30+ seconds
- `yield` = sends data as soon as it's ready → user sees live terminal logs, feels responsive
- `stream_with_context()` = preserves Flask's request context inside the generator

**Frontend consumption:**
```typescript
const reader = response.body.getReader();          // ReadableStream API
const decoder = new TextDecoder();
while (true) {
    const { done, value } = await reader.read();   // Read chunk by chunk
    if (done) break;
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');               // Parse JSON-Lines
    for (const line of lines) {
        const data = JSON.parse(line);             // Each line is one event
    }
}
```

### 3.4 Entity Tagging (Prompt Engineering as NER)

Instead of running a separate Named Entity Recognition model, you instruct the LLM to output tags:
```
Medication: [[MED|Paracetamol]]
Diagnosis: [[DIAG|Hypertension]]  
Procedure: [[PROC|Angioplasty]]
```

The frontend regex-replaces these into colored badges:
```typescript
// In MarkdownOutput.tsx
processedText.replace(/\[\[MED\|(.*?)\]\]/gi, "<span class='ner-badge ner-med ...'>$1</span>");
processedText.replace(/\[\[DIAG\|(.*?)\]\]/gi, "<span class='ner-badge ner-diag ...'>$1</span>");
processedText.replace(/\[\[PROC\|(.*?)\]\]/gi, "<span class='ner-badge ner-proc ...'>$1</span>");
```

Clicking any badge triggers `/explain_term` → opens a dialog with a layman's explanation.

> **TI Interview Point:** You're using **prompt engineering as a zero-cost alternative to NER**, which saves compute and avoids loading a separate model.

---

## 4. 🏢 TI-Specific Interview Angles {#4-ti-specific-angles}

Texas Instruments is a **hardware/embedded systems** company. They'll likely evaluate you on:

### What TI Cares About → How Your Project Maps

| TI Focus Area | Your Project Connection |
|:---|:---|
| **Embedded / Edge Computing** | Your entire system runs locally (Ollama + Qwen 3B). This IS edge AI. Explain how this could run on a TI edge device (e.g., TDA4VM) |
| **Optimization & Resource Constraints** | You chose Qwen2.5-3B specifically because it's lightweight (fits in ~4GB RAM). Discuss model quantization (GGUF), memory optimization |
| **Signal Processing / Data Pipelines** | Your 3-stage retrieval pipeline IS a data processing pipeline. BM25=frequency analysis (like signal processing), Embeddings=feature extraction |
| **Testing & Verification** | You built an automated evaluation pipeline with 250 test questions and Gemini as judge → 90% accuracy. This is systematic verification |
| **System Design** | Decoupled architecture (Flask backend + React frontend), streaming protocols, clear API contracts |
| **C/Python Programming** | All backend in Python, understanding of generators, OOP (wrapper pattern), design patterns |

### How to Pitch This to TI

> "While this project is in healthcare NLP, the core engineering principles directly translate to TI's work: I designed a **resource-efficient AI pipeline** that runs on constrained hardware (local machine, no GPU needed for the 3B model). The 3-stage retrieval pipeline demonstrates my understanding of **signal processing concepts** — BM25 is essentially term-frequency analysis, and embeddings are high-dimensional feature extraction. The automated evaluation system shows my commitment to **rigorous testing**, which I know is critical in TI's semiconductor validation workflows."

---

## 5. 🔥 Tough Questions TI Will Ask {#5-tough-questions}

### Q1: "Walk me through your system architecture in 2 minutes"

**Answer:** "The system has 3 layers:
1. **Frontend** (React/Vite/TypeScript) — A single-page app with document upload, real-time terminal logs via streaming, markdown summary rendering with clickable NER badges, and a chat interface.
2. **Backend** (Flask/Python) — 3 API endpoints: `/stream_generate` builds the RAG pipeline and generates summaries, `/stream_chat` answers follow-up questions using the same vector store, and `/explain_term` explains medical jargon without RAG.
3. **AI Layer** — PubMedBERT for medical embeddings, ChromaDB for vector storage, BM25 for keyword search, MedCPT Cross-Encoder for re-ranking, and Qwen2.5-3B via Ollama for generation. Everything runs locally."

### Q2: "Why not just use ChatGPT API?"

**Answer:** "Three reasons:
1. **Privacy**: Medical data is regulated (HIPAA). Sending patient reports to OpenAI's servers violates compliance. My system processes everything locally — data never leaves the machine.
2. **Cost**: OpenAI APIs cost per token. For a hospital processing thousands of reports daily, that's expensive. Local inference = zero marginal cost.
3. **Reliability**: No internet dependency. Works in air-gapped environments (military hospitals, secure facilities). No rate limits, no downtime."

### Q3: "What's the difference between your RAG and a basic one?"

**Answer:**
| Feature | Basic/Naive RAG | My Advanced RAG |
|:---|:---|:---|
| Chunking | Fixed 500-char splits | Semantic chunking (splits on meaning change) |
| Retrieval | Single vector search | Parent-Child + BM25 hybrid + Cross-Encoder re-ranking |
| Embeddings | Generic sentence-transformers | PubMedBERT (medical domain-specific) |
| Re-ranking | None | MedCPT Cross-Encoder (NCBI's medical model) |
| Search | Dense only | Dense (50%) + Sparse/BM25 (50%) |

### Q4: "Explain Parent-Child Retrieval in simple terms"

**Answer:** "It's solving a paradox. Vector search works best with small chunks (more precise matching), but LLMs generate better answers with large chunks (more context). So I split documents into small 'child' chunks for searching, but store the corresponding large 'parent' chunks separately. When a small child chunk matches the query, I fetch its parent and send that to the LLM. Best of both worlds."

### Q5: "What is BM25 and why combine it with vector search?"

**Answer:** "BM25 is an evolution of TF-IDF (Term Frequency × Inverse Document Frequency). It finds documents based on exact keyword matching — 'Paracetamol 500mg' will match literally. Vector search (dense retrieval) understands meaning — 'pain reliever' can match 'analgesic'. In medical documents, you need BOTH: exact drug names AND conceptual understanding. The EnsembleRetriever combines them 50:50."

### Q6: "What's a Cross-Encoder and why is it more accurate but slower?"

**Answer:** "A Bi-Encoder (like PubMedBERT) encodes the query and documents separately into vectors, then compares distances. This is fast because document vectors are pre-computed. A Cross-Encoder takes the query AND each candidate document together, feeds the pair through a transformer, and outputs a direct relevance score. It's more accurate because it sees the interaction between query and document tokens, but it's O(n) per candidate — too expensive for initial retrieval, perfect for re-ranking a small set (I use it on the top candidates to select the final 3)."

### Q7: "Your evaluation shows 90% accuracy. Where did the 10% fail?"

**Answer:** "All 25 failures were on **Question 2** ('What vital signs were recorded?') across different specialties. The pattern: the retrieval pipeline correctly indexed the vital signs data, but the LLM (Qwen2.5-3B being a small 3B model) would sometimes respond 'not mentioned' for vital sign details that were buried deep in the context. This is the **'Lost in the Middle' problem** — small LLMs struggle with information located in the middle of long contexts. Solutions:
1. Move to a larger model (7B+) for better long-context understanding
2. Use **Extractive QA** (extract exact spans) instead of generative for factual questions
3. Add a dedicated vital-signs extraction step using regex or NER before LLM generation"

### Q8: "How would you deploy this to production?"

**Answer:**
1. **Replace InMemoryStore** → PostgreSQL or Redis for session-based vector persistence
2. **Replace global `active_retriever`** → Session-based state with Redis + Celery task queues
3. **Deploy Ollama on GPU instances** → AWS g4dn.xlarge (NVIDIA T4) or equivalent
4. **Add WSGI server** → Gunicorn with multiple workers behind an Nginx load balancer
5. **Add authentication** → JWT tokens for API access
6. **Add OCR** → Tesseract for scanned PDFs
7. **Add persistent ChromaDB** → File-backed SQLite on S3-mounted volumes

### Q9: "What design patterns did you use?"

**Answer:**
1. **Adapter Pattern** — `SemanticChunkerWrapper` adapts `SemanticChunker` to `TextSplitter` interface
2. **Chain of Responsibility** — LCEL pipeline (retriever → prompt → llm → parser)
3. **Strategy Pattern** — Swappable retrievers (BM25, Vector, Ensemble)
4. **Observer Pattern** — Streaming logs (generator → consumer)
5. **Singleton-ish** — Global `embeddings` and `cross_encoder` initialized once

### Q10: "What's the time complexity of your retrieval pipeline?"

**Answer:**
1. **ChromaDB vector search**: O(log n) with HNSW approximate nearest neighbor
2. **BM25**: O(n × m) where n=documents, m=query terms (but with inverted index → effectively O(m × k))
3. **Cross-Encoder re-ranking**: O(k) where k = number of candidate docs (I limit to top results)
4. **Overall**: Dominated by the Cross-Encoder inference time (transformer forward pass per candidate)

### Q11: "What is Cosine Similarity?"

**Answer:** "It's the cosine of the angle between two vectors in high-dimensional space. Value ranges from -1 (opposite) to 1 (identical). It measures directional similarity, not magnitude — so two vectors pointing the same way but with different lengths still get cosine=1. In NLP, this means sentences with the same meaning but different lengths score high. Formula: cos(θ) = (A·B) / (||A|| × ||B||)"

### Q12: "Explain the Transformer architecture briefly"

**Answer:** "The Transformer has two key innovations: **Self-Attention** (lets each token attend to every other token in the sequence, capturing long-range dependencies) and **Positional Encoding** (since there's no recurrence, position info is added explicitly). It consists of an encoder stack (for understanding) and decoder stack (for generation). BERT uses only the encoder, GPT uses only the decoder, and the original Transformer uses both. Self-attention computes Q(Query), K(Key), V(Value) matrices and outputs Attention(Q,K,V) = softmax(QK^T / √d_k) × V."

### Q13: "What's the difference between your project's architecture and a microservices architecture?"

**Answer:** "Currently it's a **monolithic** Flask app — all 3 endpoints in one process sharing state (global `active_retriever`). For microservices, I'd split into:
- **Ingestion Service**: Handles PDF parsing and chunking
- **Retrieval Service**: Manages vector DB and search
- **Inference Service**: Wraps the LLM
- **API Gateway**: Routes requests
- **Message Queue** (RabbitMQ/Kafka): Async communication between services
The tradeoff: microservices add complexity but enable independent scaling (scale inference GPU separately from retrieval)."

---

## 6. 📊 Evaluation Pipeline — Your Secret Weapon {#6-evaluation}

> **This is IMPRESSIVE for an interview. Very few candidates build automated evaluation.**

### How It Works ([evaluate_rag.py](file:///c:/Learning/BriefMedAi/dataset/evaluate_rag.py))

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│ eval_dataset  │────▶│  BriefMed AI  │────▶│ Gemini LLM Judge │
│  (50 reports, │     │  (local app) │     │ (scores PASS/FAIL│
│  250 Q&A pairs│     │              │     │  with reasoning) │
│  across 15    │     └──────────────┘     └────────┬─────────┘
│  specialties) │                                   │
└──────────────┘                          ┌─────────▼─────────┐
                                          │  eval_summary.md  │
                                          │  90% Accuracy     │
                                          │  225/250 Passed   │
                                          └───────────────────┘
```

### Key Results

| Metric | Value |
|:---|:---|
| **Overall Accuracy** | 90.00% |
| **Total Questions** | 250 (5 per report × 50 reports) |
| **Passed** | 225 |
| **Failed** | 25 |
| **Best Specialties** | Orthopedics (100%), Urology (100%), Endocrinology (96%) |
| **Weakest Specialties** | Psychiatry (80%), Ophthalmology (80%), Allergy (80%) |
| **Common Failure Pattern** | "Vital signs not mentioned" when they were — Lost in the Middle problem |

### Why This Matters for TI

TI is a verification-heavy company (chip design requires rigorous testing). By explaining:
- "I didn't just build the system — I built a **testing harness** that automatically evaluates accuracy"
- "I used **LLM-as-Judge** methodology (a current research approach) with Gemini as an independent evaluator"
- "I identified a **systematic failure pattern** (vital signs retrieval) and can explain exactly why it fails and how to fix it"

---

## 7. ⚠️ Known Limitations & Fixes {#7-limitations}

| Limitation | Root Cause | How You'd Fix It |
|:---|:---|:---|
| No multi-user support | Global `active_retriever` variable | Session-based state with Redis/DB |
| Can't read scanned PDFs | PyPDF only handles text-embedded PDFs | Add Tesseract OCR |
| 10% failure rate on vital signs | Small 3B model loses middle context | Larger model (7B+) or extractive QA |
| No persistent storage | `InMemoryStore` + `temp_collection` | File-backed ChromaDB + PostgreSQL |
| No authentication | POC stage | JWT tokens + role-based access |
| Frontend hardcoded API URL | `http://127.0.0.1:5000` in components | Environment variables via `.env` |
| No image/table extraction | Text-only pipeline | Add table parsers + image retrieval |
| Single model dependency | Only Qwen2.5-3B | Model router to switch between models |

---

## 8. 🔢 Key Numbers to Memorize {#8-key-numbers}

| What | Value | Why It Matters |
|:---|:---|:---|
| Model size | Qwen2.5 **3B** parameters | Small enough for local CPU/low-VRAM GPU |
| PubMedBERT embedding dimension | **768** | Standard BERT-base dimension |
| Parent chunk size | **2000** characters | Large enough for full clinical context |
| Parent chunk overlap | **200** characters | Prevents boundary information loss |
| BM25 top-k | **3** | Number of keyword search results |
| Cross-Encoder top-n | **3** | Final re-ranked results sent to LLM |
| Ensemble weights | **0.5 / 0.5** | Equal weight to keyword vs semantic search |
| Temperature | **0.0** | Deterministic output (critical for medical) |
| Ollama port | **11434** | Local model server |
| Flask port | **5000** | Backend API |
| Vite port | **5173** | Frontend dev server |
| Eval accuracy | **90%** | 225/250 questions passed |
| Medical specialties tested | **15** | Cardiology through Ophthalmology |
| Total eval questions | **250** | 5 per report × 50 reports |

---

## 9. 📝 Quick Revision Cheatsheet {#9-cheatsheet}

### Tech Stack at a Glance

| Layer | Technology | Purpose |
|:---|:---|:---|
| Frontend | React + Vite + TypeScript + Tailwind | Pitch-black cyber UI, streaming terminal, chat |
| Backend | Flask + Python | REST APIs, streaming, RAG orchestration |
| PDF Parser | PyPDF | Extract text from PDFs |
| Embedding Model | PubMedBERT (`NeuML/pubmedbert-base-embeddings`) | Medical-domain vector embeddings (768-dim) |
| Vector Store | ChromaDB (in-memory) | Store + search embeddings via HNSW |
| Keyword Search | BM25 (`rank_bm25`) | TF-IDF based sparse retrieval |
| Re-ranker | MedCPT Cross-Encoder (`ncbi/MedCPT-Cross-Encoder`) | Re-score candidates for clinical accuracy |
| LLM | Qwen2.5-3B via Ollama | Local text generation |
| Orchestration | LangChain (LCEL) | Chain retrieval → prompt → LLM → parse |
| Evaluation | Gemini API (LLM-as-Judge) | Automated accuracy testing |

### The 3 API Endpoints

| Endpoint | Method | Input | Output | Uses RAG? |
|:---|:---|:---|:---|:---|
| `/stream_generate` | POST (FormData) | PDF file or raw text | Streaming JSON-Lines: logs + structured summary | ✅ Full pipeline |
| `/stream_chat` | POST (JSON) | Question + history | Streaming JSON-Lines: log + answer | ✅ Reuses vector store |
| `/explain_term` | POST (JSON) | Medical term | Streaming JSON-Lines: log + explanation | ❌ Direct LLM call |

### Key Concepts Flashcards

| Term | One-Line Definition |
|:---|:---|
| **RAG** | Retrieve external knowledge → augment the prompt → generate answer |
| **Semantic Chunking** | Split text where meaning changes (using embedding similarity), not at fixed character counts |
| **Parent-Child Retrieval** | Search on small precise chunks, but feed large contextual chunks to LLM |
| **Hybrid Search** | Combine keyword (BM25) + semantic (vector) retrieval |
| **Cross-Encoder** | Takes query+document pair together through transformer for accurate relevance scoring |
| **Bi-Encoder** | Encodes query and document separately → fast but less accurate |
| **LCEL** | LangChain Expression Language — pipe operators to chain components |
| **BM25** | Advanced TF-IDF: ranks documents by term frequency and document rarity |
| **HNSW** | Hierarchical Navigable Small World — fast approximate nearest neighbor algorithm used by ChromaDB |
| **Cosine Similarity** | cos(θ) between two vectors. 1=same, 0=unrelated, -1=opposite |
| **Prompt Engineering as NER** | Using `[[MED\|name]]` tags in prompts to get structured entity output without a separate NER model |
| **Temperature** | Controls randomness. 0=deterministic (medical needs this), 1=creative |
| **GGUF** | File format for quantized LLM weights (used by Ollama) |
| **SSE** | Server-Sent Events — unidirectional streaming from server to client |
| **Hallucination** | LLM confidently generating false information not in the source |
| **Lost in the Middle** | LLMs pay more attention to beginning/end of context, miss the middle |

### Frontend Components Quick Reference

| Component | What It Does |
|:---|:---|
| [DemoSection.tsx](file:///c:/Learning/BriefMedAi/frontend/src/components/DemoSection.tsx) | Core: file upload, text input, streaming consumer, terminal logs, chat interface |
| [MarkdownOutput.tsx](file:///c:/Learning/BriefMedAi/frontend/src/components/MarkdownOutput.tsx) | Renders markdown, replaces `[[MED\|..]]` tags with colored badges, opens explain-term dialog on click |
| [HeroSection.tsx](file:///c:/Learning/BriefMedAi/frontend/src/components/HeroSection.tsx) | Landing hero with scanning animation |
| [TechStack.tsx](file:///c:/Learning/BriefMedAi/frontend/src/components/TechStack.tsx) | Displays tech stack, architecture steps, privacy points |
| [HowItWorks.tsx](file:///c:/Learning/BriefMedAi/frontend/src/components/HowItWorks.tsx) | 3-step visual: Upload → Process → Results |
| [RoadmapSection.tsx](file:///c:/Learning/BriefMedAi/frontend/src/components/RoadmapSection.tsx) | 20 planned features in 4 phases (accordion UI) |

---

> [!TIP]
> ## 🎯 Final Interview Tips for TI
> 
> 1. **Lead with the engineering**, not the AI. TI cares about system design, optimization, and testing rigor.
> 2. **Connect to edge computing**: "My system already runs on constrained hardware — this is exactly the kind of edge AI deployment TI enables with its processors."
> 3. **Mention your evaluation pipeline early** — it shows engineering maturity that most candidates lack.
> 4. **Know the failure modes**: Being able to explain WHERE your system fails and WHY (the 10% vital signs issue) shows deep understanding.
> 5. **Use analogies from signal processing**: BM25 ≈ frequency analysis, Embeddings ≈ feature extraction, Cross-Encoder ≈ matched filter.
> 6. **Don't oversell**: If asked "Can this replace a doctor?", say "Absolutely not. The disclaimer is programmatically enforced for a reason."

---

**Best of luck tomorrow! 🔥 You've got a strong project — own it confidently.**

# Enterprise Knowledge Assistant with Advanced RAG

A production-grade Retrieval-Augmented Generation system built for the TCS Accelerate Academic Partnership Programme (Generative AI Track).

## Project Overview

This system enables employees to query a corpus of 500 enterprise documents spanning HR policies, IT standards, compliance guidelines, and product documentation. It returns accurate, citation-backed answers with hallucination detection and safety guardrails.

## Architecture
User Query

↓

Safety Guardrails (PII, Injection, Scope Check)

↓

Hybrid Search

├── Semantic Search (ChromaDB + HuggingFace Embeddings)

└── Keyword Search (TF-IDF style matching)

↓

Reciprocal Rank Fusion (RRF)

↓

Reranking (Cross-encoder scoring)

↓

Answer Generation (Gemini 2.0 Flash)

↓

Hallucination Detection

↓

Citation-backed Response

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Google Gemini 2.0 Flash |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Store | ChromaDB |
| Framework | LangChain |
| UI | Streamlit |
| Evaluation | RAGAS |

## Features

- **Hybrid Search** — combines semantic and keyword search for better recall
- **Reciprocal Rank Fusion** — merges results from multiple search strategies
- **Reranking** — selects top 5 most relevant chunks
- **Citation-backed answers** — every claim cites its source document
- **Hallucination detection** — flags ungrounded claims
- **Safety guardrails** — PII detection, prompt injection defense, scope validation
- **RAGAS evaluation** — measures faithfulness, relevance, precision, recall

## Project Structure
enterprise-rag/

├── src/

│   ├── ingestion/

│   │   ├── document_generator.py

│   │   ├── document_loader.py

│   │   ├── chunker.py

│   │   └── embeddings.py

│   ├── retrieval/

│   │   └── retriever.py

│   ├── generation/

│   │   └── generator.py

│   ├── evaluation/

│   │   └── ragas_eval.py

│   ├── safety/

│   │   └── guardrails.py

│   └── pipeline.py

├── app/

│   └── app.py

├── documents/

├── reports/

├── .env

├── requirements.txt

└── README.md
## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/NexusNavneet/enterprise-rag.git
cd enterprise-rag
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API key
Create a `.env` file:

Get your free key from [aistudio.google.com](https://aistudio.google.com)

### 5. Generate documents
```bash
python src/ingestion/document_generator.py
```

### 6. Create vector store
```bash
python src/ingestion/embeddings.py
```

### 7. Run the application
```bash
streamlit run app/app.py
```

## Evaluation Results

| Metric | Iteration 1 | Iteration 2 | Iteration 3 |
|--------|-------------|-------------|-------------|
| Context Recall | TBD | TBD | TBD |
| Context Precision | TBD | TBD | TBD |
| Answer Relevance | TBD | TBD | TBD |
| Faithfulness | TBD | TBD | TBD |

*Results will be updated after each evaluation iteration*

## Known Limitations and Production Improvements

- **Embeddings** — Currently using local sentence-transformers. Production would use hosted embedding API for scale
- **Reranking** — Currently uses simple keyword scoring. Production would use Cohere Rerank or BAAI cross-encoder
- **Documents** — Currently synthetic. Production would use real enterprise documents
- **API Rate Limits** — Free tier Gemini has 20 requests/day limit. Production would use paid tier

## Assessment Criteria Coverage

| Criteria | Weight | Implementation |
|----------|--------|----------------|
| Technical Implementation | 40% | Full RAG pipeline with hybrid search, reranking, citations |
| Architectural Thinking | 25% | See architecture section above |
| Operational Readiness | 20% | Safety guardrails, evaluation harness, error handling |
| Communication | 15% | This README + demo recording |

## Author

**Navneet** — TCS Accelerate GenAI Track  
GitHub: [@NexusNavneet](https://github.com/NexusNavneet)

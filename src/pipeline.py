import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from generation.generator import generate_answer, check_hallucination

load_dotenv()

def load_vector_store():
    embedding_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    vector_store = Chroma(
        persist_directory=".chroma",
        embedding_function=embedding_model
    )
    return vector_store


def semantic_search(query, vector_store, k=10):
    """Dense retrieval — finds chunks with similar MEANING"""
    return vector_store.similarity_search(query, k=k)


def keyword_search(query, vector_store, k=10):
    """Sparse retrieval — finds chunks with same WORDS"""
    all_docs = vector_store.similarity_search(query, k=50)
    query_words = set(query.lower().split())
    scored = []
    for doc in all_docs:
        content_words = set(doc.page_content.lower().split())
        matches = len(query_words.intersection(content_words))
        if matches > 0:
            scored.append((matches, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:k]]


def reciprocal_rank_fusion(semantic_results, keyword_results, k=60):
    """Combines semantic and keyword results using RRF"""
    scores = {}
    for rank, doc in enumerate(semantic_results):
        key = doc.page_content[:100]
        if key not in scores:
            scores[key] = {"doc": doc, "score": 0}
        scores[key]["score"] += 1 / (k + rank + 1)
    for rank, doc in enumerate(keyword_results):
        key = doc.page_content[:100]
        if key not in scores:
            scores[key] = {"doc": doc, "score": 0}
        scores[key]["score"] += 1 / (k + rank + 1)
    sorted_results = sorted(
        scores.values(),
        key=lambda x: x["score"],
        reverse=True
    )
    return [item["doc"] for item in sorted_results]


def rerank(query, documents, top_k=5):
    """
    Simple reranker — scores each chunk against query
    In production this would use a cross-encoder model
    """
    query_words = set(query.lower().split())
    scored = []
    for doc in documents:
        content = doc.page_content.lower()
        # Score based on query word matches + position bonus
        matches = sum(1 for word in query_words if word in content)
        scored.append((matches, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]


def run_pipeline(query):
    """
    MAIN FUNCTION — runs the complete RAG pipeline
    Input: user query
    Output: answer with citations and hallucination check
    """
    
    print(f"\n{'='*50}")
    print(f"QUERY: {query}")
    print(f"{'='*50}")
    
    # Step 1 — Load vector store
    print("\n📂 Loading vector store...")
    vs = load_vector_store()
    
    # Step 2 — Semantic search
    print("🔍 Running semantic search...")
    semantic_results = semantic_search(query, vs, k=10)
    print(f"   Found {len(semantic_results)} semantic results")
    
    # Step 3 — Keyword search
    print("🔍 Running keyword search...")
    keyword_results = keyword_search(query, vs, k=10)
    print(f"   Found {len(keyword_results)} keyword results")
    
    # Step 4 — RRF fusion
    print("🔀 Combining results with RRF...")
    combined = reciprocal_rank_fusion(semantic_results, keyword_results)
    print(f"   Combined into {len(combined)} results")
    
    # Step 5 — Reranking
    print("⚡ Reranking top results...")
    top_chunks = rerank(query, combined, top_k=5)
    print(f"   Selected top {len(top_chunks)} chunks")
    
    # Step 6 — Generate answer
    print("🤖 Generating answer...")
    answer = generate_answer(query, top_chunks)
    
    # Step 7 — Hallucination check
    print("🔍 Checking for hallucinations...")
    verdict = check_hallucination(answer, top_chunks)
    
    # Step 8 — Prepare sources
    sources = []
    for i, chunk in enumerate(top_chunks):
        sources.append({
            "index": i + 1,
            "category": chunk.metadata["category"],
            "filename": chunk.metadata["filename"],
            "preview": chunk.page_content[:150]
        })
    
    result = {
        "query": query,
        "answer": answer,
        "verdict": verdict,
        "sources": sources
    }
    
    return result


if __name__ == "__main__":
    # Test the full pipeline
    query = "What is the leave policy for employees?"
    result = run_pipeline(query)
    
    print(f"\n{'='*50}")
    print("FINAL ANSWER:")
    print(f"{'='*50}")
    print(result["answer"])
    print(f"\nHallucination Check: {result['verdict']}")
    print(f"\nSources Used:")
    for source in result["sources"]:
        print(f"  [{source['index']}] {source['category']} — {source['filename']}")
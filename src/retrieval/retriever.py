import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

def load_vector_store():
    """Load the vector store from disk"""
    
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    vector_store = Chroma(
        persist_directory=".chroma",
        embedding_function=embedding_model
    )
    
    return vector_store


def semantic_search(query, vector_store, k=10):
    """
    Dense retrieval — finds chunks with similar MEANING
    Returns top k results
    """
    results = vector_store.similarity_search(query, k=k)
    return results


def keyword_search(query, chunks, k=10):
    """
    Sparse retrieval — finds chunks with same WORDS
    Simple keyword matching for now
    """
    query_words = set(query.lower().split())
    scored = []
    
    for chunk in chunks:
        content_words = set(chunk.page_content.lower().split())
        # Count how many query words appear in chunk
        matches = len(query_words.intersection(content_words))
        if matches > 0:
            scored.append((matches, chunk))
    
    # Sort by number of matches
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:k]]


def reciprocal_rank_fusion(semantic_results, keyword_results, k=60):
    """
    RRF combines semantic and keyword results
    Gives each result a score based on its rank in both lists
    Higher score = more relevant
    """
    scores = {}
    
    # Score semantic results
    for rank, doc in enumerate(semantic_results):
        key = doc.page_content[:100]  # Use first 100 chars as unique key
        if key not in scores:
            scores[key] = {"doc": doc, "score": 0}
        scores[key]["score"] += 1 / (k + rank + 1)
    
    # Score keyword results
    for rank, doc in enumerate(keyword_results):
        key = doc.page_content[:100]
        if key not in scores:
            scores[key] = {"doc": doc, "score": 0}
        scores[key]["score"] += 1 / (k + rank + 1)
    
    # Sort by combined score
    sorted_results = sorted(
        scores.values(),
        key=lambda x: x["score"],
        reverse=True
    )
    
    return [item["doc"] for item in sorted_results]


def hybrid_search(query, vector_store, all_chunks, top_k=5):
    """
    Main search function combining semantic + keyword search
    """
    print(f"\n🔍 Searching for: '{query}'")
    
    # Step 1 — Semantic search
    semantic_results = semantic_search(query, vector_store, k=10)
    print(f"✅ Semantic search: {len(semantic_results)} results")
    
    # Step 2 — Keyword search
    keyword_results = keyword_search(query, all_chunks, k=10)
    print(f"✅ Keyword search: {len(keyword_results)} results")
    
    # Step 3 — Combine with RRF
    combined = reciprocal_rank_fusion(semantic_results, keyword_results)
    print(f"✅ After RRF fusion: {len(combined)} results")
    
    # Return top results
    return combined[:top_k]


if __name__ == "__main__":
    # Only test if vector store exists
    if not os.path.exists(".chroma"):
        print("⚠️ Vector store not ready yet — still being created!")
        print("Check Terminal 1 for progress...")
    else:
        from ingestion.document_loader import load_documents
        from ingestion.chunker import chunk_documents
        
        print("Loading vector store...")
        vs = load_vector_store()
        
        docs = load_documents()
        chunks = chunk_documents(docs)
        
        results = hybrid_search(
            "what is the leave policy for employees?",
            vs,
            chunks,
            top_k=5
        )
        
        print(f"\n--- TOP {len(results)} RESULTS ---")
        for i, r in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"Category: {r.metadata['category']}")
            print(f"Content: {r.page_content[:200]}")
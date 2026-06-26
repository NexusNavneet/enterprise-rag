import os
import sys
import time

# This allows importing from parent folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from ingestion.document_loader import load_documents
from ingestion.chunker import chunk_documents

load_dotenv()

import time

def create_vector_store(chunks):
    print("⏳ Creating embeddings — this will take 30-40 minutes due to free tier limits...")
    
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    batch_size = 50
    vector_store = None
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        
        # Retry logic — try up to 3 times if rate limited
        for attempt in range(3):
            try:
                if vector_store is None:
                    vector_store = Chroma.from_documents(
                        documents=batch,
                        embedding=embedding_model,
                        persist_directory=".chroma"
                    )
                else:
                    vector_store.add_documents(batch)
                break  # Success — exit retry loop
                
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    print(f"⏳ Rate limited — waiting 65 seconds...")
                    time.sleep(65)
                else:
                    raise e
        
        processed = min(i + batch_size, len(chunks))
        print(f"✅ Processed {processed}/{len(chunks)} chunks...")
        
        # Wait 65 seconds between every batch
        if i + batch_size < len(chunks):
            time.sleep(65)
    
    print(f"\n🎉 Vector store created!")
    return vector_store
    



def load_vector_store():
    """
    Load existing vector store instead of recreating it
    """
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    vector_store = Chroma(
        persist_directory=".chroma",
        embedding_function=embedding_model
    )
    
    print(f"✅ Loaded existing vector store")
    return vector_store


if __name__ == "__main__":
    # Check if vector store already exists
    if os.path.exists(".chroma"):
        print("📂 Vector store already exists — loading it...")
        vs = load_vector_store()
    else:
        print("🆕 Creating new vector store...")
        docs = load_documents()
        chunks = chunk_documents(docs)
        vs = create_vector_store(chunks)
    
    # Test a search
    print("\n--- TEST SEARCH ---")
    results = vs.similarity_search("what is the leave policy?", k=3)
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Category: {result.metadata['category']}")
        print(f"Content: {result.page_content[:150]}")

from langchain_text_splitters import RecursiveCharacterTextSplitter
from document_loader import load_documents

def chunk_documents(documents):
    """
    Split documents into smaller chunks
    Each chunk = ~500 characters with 50 character overlap
    """
    
    # This splitter tries to split on paragraphs first,
    # then sentences, then words — keeps context intact
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,        # Each chunk = 500 characters
        chunk_overlap=50,      # 50 characters overlap between chunks
        separators=["\n\n", "\n", ".", " "]  # Split priority order
    )
    
    chunks = splitter.split_documents(documents)
    
    # Add chunk number to metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
    
    print(f"✅ Original documents: {len(documents)}")
    print(f"✅ Total chunks created: {len(chunks)}")
    print(f"📊 Average chunks per document: {len(chunks)//len(documents)}")
    
    return chunks


if __name__ == "__main__":
    # Load documents first
    docs = load_documents()
    
    # Then chunk them
    chunks = chunk_documents(docs)
    
    # Show a sample chunk
    print(f"\n--- SAMPLE CHUNK ---")
    print(f"Category: {chunks[0].metadata['category']}")
    print(f"Chunk ID: {chunks[0].metadata['chunk_id']}")
    print(f"Content: {chunks[0].page_content}")
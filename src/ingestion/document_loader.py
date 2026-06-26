import os
from langchain_core.documents import Document

def load_documents(documents_path="documents"):
    """
    Load all text files from the documents folder
    Returns a list of Document objects
    """
    
    all_documents = []
    total_files = 0
    
    # Walk through every folder and file
    for category in os.listdir(documents_path):
        category_path = os.path.join(documents_path, category)
        
        # Skip if not a folder
        if not os.path.isdir(category_path):
            continue
            
        for filename in os.listdir(category_path):
            
            # Only process .txt files
            if not filename.endswith(".txt"):
                continue
                
            file_path = os.path.join(category_path, filename)
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create a Document object with metadata
            # Metadata tells us WHERE this content came from
            doc = Document(
                page_content=content,
                metadata={
                    "source": file_path,
                    "category": category,
                    "filename": filename
                }
            )
            
            all_documents.append(doc)
            total_files += 1
    
    print(f"✅ Loaded {total_files} documents")
    print(f"📂 Categories found: {set(doc.metadata['category'] for doc in all_documents)}")
    
    return all_documents


# Test it
if __name__ == "__main__":
    docs = load_documents()
    
    # Show a sample document
    print(f"\n--- SAMPLE DOCUMENT ---")
    print(f"Category: {docs[0].metadata['category']}")
    print(f"Filename: {docs[0].metadata['filename']}")
    print(f"Content preview: {docs[0].page_content[:200]}")
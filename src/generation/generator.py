import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def generate_answer(query, retrieved_chunks):
    """
    Takes a query and relevant chunks
    Generates an answer WITH citations
    """
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Build context from retrieved chunks
    context = ""
    for i, chunk in enumerate(retrieved_chunks):
        context += f"""
[SOURCE {i+1}]
Category: {chunk.metadata['category']}
File: {chunk.metadata['filename']}
Content: {chunk.page_content}
---
"""
    
    # Prompt that forces citations
    prompt = f"""You are an Enterprise Knowledge Assistant.
Answer the question using ONLY the provided sources below.
You MUST cite sources using [SOURCE 1], [SOURCE 2] etc.
If the answer is not in the sources, say "I cannot find this information in the available documents."

SOURCES:
{context}

QUESTION: {query}

ANSWER (with citations):"""
    
    response = llm.invoke(prompt)
    
    # Extract text from response
    if isinstance(response.content, list):
        answer = ""
        for block in response.content:
            if isinstance(block, dict) and block.get('type') == 'text':
                answer += block['text']
    else:
        answer = response.content
    
    return answer


def check_hallucination(answer, retrieved_chunks):
    """
    Simple hallucination check
    Checks if key claims in answer are supported by retrieved chunks
    """
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    context = " ".join([chunk.page_content for chunk in retrieved_chunks])
    
    prompt = f"""Check if this answer is supported by the context below.
Reply with only: GROUNDED or HALLUCINATED and one line reason.

CONTEXT: {context[:2000]}

ANSWER: {answer}

VERDICT:"""
    
    response = llm.invoke(prompt)
    
    if isinstance(response.content, list):
        verdict = ""
        for block in response.content:
            if isinstance(block, dict) and block.get('type') == 'text':
                verdict += block['text']
    else:
        verdict = response.content
    
    return verdict


if __name__ == "__main__":
    # Mock test without vector store
    from langchain_core.documents import Document
    
    # Fake chunks for testing
    test_chunks = [
        Document(
            page_content="Employees are entitled to 20 days of annual leave per year. Leave must be approved by the manager.",
            metadata={"category": "hr", "filename": "leave_policy_1.txt"}
        ),
        Document(
            page_content="Sick leave of up to 10 days per year is provided. A medical certificate is required for more than 2 consecutive days.",
            metadata={"category": "hr", "filename": "leave_policy_2.txt"}
        )
    ]
    
    query = "How many days of annual leave do employees get?"
    
    print("🤖 Generating answer...")
    answer = generate_answer(query, test_chunks)
    print(f"\nAnswer:\n{answer}")
    
    print("\n🔍 Checking for hallucinations...")
    verdict = check_hallucination(answer, test_chunks)
    print(f"Verdict: {verdict}")
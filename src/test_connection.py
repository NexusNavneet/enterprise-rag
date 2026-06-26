from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env file
load_dotenv()

# Check if key is being read — add this debug line
api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key found: {api_key[:10]}...")  # Only prints first 10 characters

# Create AI model
llm = ChatGoogleGenerativeAI(
     model="gemini-3.5-flash",
    temperature=0,
    google_api_key=api_key  # Pass key directly
)

response = llm.invoke("Hello! Explain RAG in 2 lines.")

for block in response.content:
    if isinstance(block, dict) and block.get('type') == 'text':
        print(block['text'])
    elif hasattr(block, 'text'):
        print(block.text)
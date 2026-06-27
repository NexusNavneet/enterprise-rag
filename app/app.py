import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.pipeline import run_pipeline

# Page config
st.set_page_config(
    page_title="Enterprise Knowledge Assistant",
    page_icon="🏢",
    layout="wide"
)

# Header
st.title("🏢 Enterprise Knowledge Assistant")
st.markdown("*Powered by Advanced RAG — Hybrid Search + Reranking + Citation*")
st.divider()

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This assistant searches across **500 enterprise documents** including:
    - 📋 HR Policies
    - 💻 IT Standards  
    - ✅ Compliance Guidelines
    - 📦 Product Documentation
    """)
    st.divider()
    st.markdown("**How it works:**")
    st.markdown("""
    1. Hybrid Search (Semantic + Keyword)
    2. Reciprocal Rank Fusion
    3. Reranking
    4. AI Answer Generation
    5. Hallucination Detection
    """)

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    query = st.text_input(
        "Ask a question about company policies:",
        placeholder="e.g. What is the leave policy for employees?"
    )
    search_btn = st.button("🔍 Search", type="primary")

# Process query
if search_btn and query:
    with st.spinner("Searching through 500 documents..."):
        try:
            result = run_pipeline(query)
            
            # Answer section
            st.subheader("💡 Answer")
            st.markdown(result["answer"])
            
            # Hallucination verdict
            verdict = result["verdict"]
            if "GROUNDED" in verdict.upper():
                st.success(f"✅ Hallucination Check: {verdict}")
            else:
                st.warning(f"⚠️ Hallucination Check: {verdict}")
            
            st.divider()
            
            # Sources section
            st.subheader("📄 Sources Used")
            for source in result["sources"]:
                with st.expander(
                    f"[SOURCE {source['index']}] {source['category'].upper()} — {source['filename']}"
                ):
                    st.markdown(f"**Preview:**")
                    st.text(source["preview"])
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("If you see a quota error, please wait a few minutes and try again.")

elif search_btn and not query:
    st.warning("Please enter a question first!")

# Example questions
st.divider()
st.subheader("💬 Example Questions")
examples = [
    "What is the leave policy for employees?",
    "What are the password requirements?",
    "What is the GDPR compliance policy?",
    "How do I request work from home?",
    "What happens if I violate the code of conduct?"
]
for ex in examples:
    if st.button(ex, key=ex):
        st.session_state["query"] = ex
import streamlit as st
import os
import json
import uuid
import sys

# Ensure src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.rag.rag_engine import ResearchRAG
from src.eval.evaluator import Evaluator
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Personal Research Portal", layout="wide")

# ---- Constants & Initialization ----
HISTORY_DIR = "outputs/history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

@st.cache_resource
def get_rag_engine():
    return ResearchRAG(persist_directory="./data/chroma_db", use_reranking=True)

try:
    rag = get_rag_engine()
except Exception as e:
    st.error(f"Failed to load RAG engine. Is GROQ_API_KEY set? Error: {e}")
    st.stop()

# Initialize session state for current session
if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "generated_memo" not in st.session_state:
    st.session_state.generated_memo = None

# ---- Helper Functions ----
def save_thread():
    if len(st.session_state.chat_history) > 0:
        filepath = os.path.join(HISTORY_DIR, f"{st.session_state.current_thread_id}.json")
        with open(filepath, 'w') as f:
            json.dump(st.session_state.chat_history, f, indent=4)

def load_thread(thread_id):
    filepath = os.path.join(HISTORY_DIR, f"{thread_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            thread_data = json.load(f)
            st.session_state.chat_history = thread_data
            st.session_state.current_thread_id = thread_id
            st.session_state.generated_memo = None
            st.rerun()

def new_thread():
    st.session_state.current_thread_id = str(uuid.uuid4())
    st.session_state.chat_history = []
    st.session_state.generated_memo = None
    st.rerun()

def get_latest_eval_report():
    eval_dir = "outputs/eval"
    if not os.path.exists(eval_dir):
        return None
    md_files = [f for f in os.listdir(eval_dir) if f.endswith('.md')]
    if not md_files:
        return None
    latest_file = max(md_files, key=lambda x: os.path.getmtime(os.path.join(eval_dir, x)))
    with open(os.path.join(eval_dir, latest_file), 'r') as f:
        return f.read(), latest_file

# ---- Sidebar (History & Evaulation Navigation) ----
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Research Assistant", "Evaluation Report"])

if page == "Research Assistant":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Research Threads")
    if st.sidebar.button("➕ New Thread"):
        new_thread()
    
    st.sidebar.markdown("---")
    # Load past threads
    past_threads = [f.replace('.json', '') for f in os.listdir(HISTORY_DIR) if f.endswith('.json')]
    for thread in sorted(past_threads, reverse=True):
        if st.sidebar.button(f"📄 Thread {thread[:8]}..."):
            load_thread(thread)

# ---- Main View ----
if page == "Research Assistant":
    st.title("📚 Personal Research Portal")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "sources" in msg:
                with st.expander("View Retrieved Evidence"):
                    for s in msg["sources"]:
                        st.markdown(f"**Source:** {s['source_id']} | **Chunk:** {s['chunk_id']}")
                        st.markdown(f"> {s['text']}")
                        st.markdown("---")

    st.markdown("---")
    
    # Chat Input
    query = st.chat_input("Ask a research question...")
    if query:
        # Add user msg
        st.session_state.chat_history.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
            
        with st.chat_message("assistant"):
            with st.spinner("Searching and generating answer..."):
                try:
                    answer, docs = rag.answer(query, return_docs=True)
                    st.markdown(answer)
                    
                    sources_data = []
                    with st.expander("View Retrieved Evidence"):
                        for d in docs:
                            src_id = d.metadata.get("source_id", "Unknown")
                            chk_id = d.metadata.get("chunk_id", "Unknown")
                            sources_data.append({
                                "source_id": src_id,
                                "chunk_id": chk_id,
                                "text": d.page_content
                            })
                            st.markdown(f"**Source:** {src_id} | **Chunk:** {chk_id}")
                            st.markdown(f"> {d.page_content}")
                            st.markdown("---")
                            
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources_data
                    })
                    save_thread()
                    
                except Exception as e:
                    st.error(f"Error answering query: {e}")

    # Artifact Generation Section
    if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]["role"] == "assistant":
        st.markdown("### Generate Artifacts")
        if st.button("Generate Synthesis Memo"):
            with st.spinner("Synthesizing memo..."):
                last_assistant_msg = st.session_state.chat_history[-1]
                last_user_msg = st.session_state.chat_history[-2]
                
                # Re-construct docs for the method
                from langchain_core.documents import Document
                docs = [
                    Document(page_content=s["text"], metadata={"source_id": s["source_id"], "chunk_id": s["chunk_id"]})
                    for s in last_assistant_msg["sources"]
                ]
                
                try:
                    memo = rag.generate_synthesis_memo(last_user_msg["content"], last_assistant_msg["content"], docs)
                    st.session_state.generated_memo = memo
                except Exception as e:
                    st.error(f"Failed to generate memo: {e}")

        # Display and export memo if generated
        if st.session_state.generated_memo:
            st.markdown("#### Synthesis Memo")
            st.markdown(st.session_state.generated_memo)
            st.download_button(
                label="📥 Download Synthesis Memo (Markdown)",
                data=st.session_state.generated_memo,
                file_name=f"Synthesis_Memo_{st.session_state.current_thread_id[:8]}.md",
                mime="text/markdown"
            )

elif page == "Evaluation Report":
    st.title("📊 Evaluation View")
    eval_data = get_latest_eval_report()
    
    if eval_data:
        report_text, report_name = eval_data
        st.success(f"Loaded latest report: `{report_name}`")
        st.markdown(report_text)
    else:
        st.warning("No evaluation reports found in `outputs/eval/`. Please run the evaluation script.")
    
    st.markdown("---")
    st.subheader("Run New Evaluation")
    if st.button("Run System Evaluator"):
        with st.spinner("Running evaluation suite (this may take several minutes)..."):
            try:
                evaluator = Evaluator(use_reranking=True) # or False based on preference
                evaluator.run_evaluation()
                st.success("Evaluation complete! The page will now refresh to show the new report.")
                st.rerun()
            except Exception as e:
                st.error(f"Evaluation failed: {e}")

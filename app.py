import os
import sqlite3
import streamlit as st
import subprocess
import sys
import re
import numpy as np

# Ensure project root is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "uav_knowledgebase.db")

# Initialize directories if they do not exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Streamlit Page Configuration
st.set_page_config(
    page_title="UAV Drone Field Maintenance & Flight Operations Assistant",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling citation badges
st.markdown("""
<style>
    .metric-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 16px 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    .metric-card strong {
        color: rgba(255, 255, 255, 0.55);
        font-size: 0.78em;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        display: block;
        margin-bottom: 6px;
    }
    .metric-card span {
        color: #ffffff !important;
        font-size: 1.4em !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Main Title and Technical Context
st.title("UAV Field Maintenance & Flight Operations Support System")
st.markdown("#### Offline Local Retrieval-Augmented Generation (RAG) Assistant")
st.write(
    "This decision support system provides field technicians and flight crews with fully offline, "
    "source-grounded answers for UAV checklists, diagnostics, and emergency protocols. "
    "All computations are executed locally via Microsoft Foundry Local SDK and SQLite."
)

def get_db_status():
    """
    Returns the count of distinct files and total chunks indexed in SQLite.
    """
    if not os.path.exists(DB_PATH):
        return 0, 0
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT filename), COUNT(*) FROM documents")
        num_docs, num_chunks = cursor.fetchone()
        conn.close()
        return num_docs or 0, num_chunks or 0
    except Exception:
        return 0, 0

def format_citations(text):
    """
    Parses output text to wrap citations in a professional styled HTML badge.
    E.g. [Source: failsafe_protocols.md] -> Styled badge
    """
    pattern = r'\[Source:\s*([^\]]+)\]'
    replacement = (
        r'<span style="'
        r'display: inline-block; '
        r'background-color: #f1f5f9; '
        r'color: #334155; '
        r'border: 1px solid #cbd5e1; '
        r'padding: 2px 8px; '
        r'border-radius: 4px; '
        r'font-size: 0.85em; '
        r'font-weight: 500; '
        r'margin: 2px 4px; '
        r'font-family: monospace;'
        r'">📄 \1</span>'
    )
    return re.sub(pattern, replacement, text)

# Sidebar Configuration
st.sidebar.header("System Controls")

# Model Configuration
st.sidebar.subheader("Model Configuration")
llm_model = st.sidebar.selectbox(
    "Large Language Model (LLM)",
    ["phi-3.5-mini", "qwen2.5-0.5b (fast, experimental)", "qwen3-0.6b"],
    help="phi-3.5-mini → accurate, ~30s. qwen2.5-0.5b → fast ~5s but less reliable on complex queries."
)
# Strip label suffix before passing to engine
llm_model_alias = llm_model.split(" ")[0]

# Initialize Session States
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None

if "current_model" not in st.session_state:
    st.session_state.current_model = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Load/Switch RAG Engine
if st.session_state.rag_engine is None or st.session_state.current_model != llm_model_alias:
    with st.spinner(f"Initializing local LLM '{llm_model_alias}'..."):
        try:
            from rag_engine import UAVRAGEngine
            st.session_state.rag_engine = UAVRAGEngine(llm_alias=llm_model_alias)
            st.session_state.current_model = llm_model_alias
            st.toast(f"Model '{llm_model_alias}' successfully loaded.", icon="✅")
        except Exception as e:
            st.error(f"Failed to initialize local LLM: {e}")
            st.info("Ensure internet connectivity for initial model download.")

# Drag-and-Drop File Uploader
st.sidebar.markdown("---")
st.sidebar.subheader("Knowledge base management")
uploaded_file = st.sidebar.file_uploader(
    "Upload Field Manual (Markdown or Text)",
    type=["md", "txt"],
    help="Upload manual to parse, vectorise, and index automatically."
)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name
    file_path = os.path.join(DATA_DIR, filename)
    
    # Save the file to data/ directory
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    # Append the uploaded manual dynamically
    with st.sidebar.status(f"Indexing '{filename}'...", expanded=True) as status:
        try:
            status.write("Initializing embedding model...")
            from retriever import UAVRetriever
            retriever = st.session_state.rag_engine.retriever if st.session_state.rag_engine else UAVRetriever()
            client = retriever.client
            
            status.write("Chunking document content...")
            content = file_bytes.decode("utf-8")
            from ingest import chunk_document
            chunks = chunk_document(content)
            
            status.write(f"Generated {len(chunks)} chunks. Updating local database...")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Avoid duplication: Clear previous indexing of the same filename
            cursor.execute("DELETE FROM documents WHERE filename = ?", (filename,))
            
            for idx, chunk in enumerate(chunks):
                response = client.generate_embedding(chunk)
                embedding = response.data[0].embedding
                emb_blob = np.array(embedding, dtype=np.float32).tobytes()
                
                cursor.execute(
                    "INSERT INTO documents (filename, chunk_index, content, embedding_blob) VALUES (?, ?, ?, ?)",
                    (filename, idx, chunk, emb_blob)
                )
            conn.commit()
            conn.close()
            status.update(label=f"'{filename}' indexed successfully!", state="complete")
            st.toast(f"'{filename}' added to knowledge base.", icon="✅")
            st.rerun()
        except Exception as e:
            status.write(f"Ingestion failed: {e}")
            status.update(label="Ingestion Failed", state="error")

# Re-ingest database trigger button
st.sidebar.markdown("---")
if st.sidebar.button("Re-Index Complete Database", use_container_width=True):
    with st.sidebar.status("Re-indexing complete data folder...", expanded=True) as status:
        try:
            status.write("Executing ingestion pipeline...")
            result = subprocess.run(
                [sys.executable, os.path.join(BASE_DIR, "ingest.py")],
                capture_output=True,
                text=True,
                check=True
            )
            status.update(label="Re-indexing Successful!", state="complete")
            st.toast("Database re-indexed successfully.", icon="✅")
            st.rerun()
        except subprocess.CalledProcessError as e:
            status.write(f"Execution failed:\n{e.stderr}")
            status.update(label="Index Failure", state="error")

# Reset Conversation History
if st.sidebar.button("Clear Conversation History", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

# Layout Status Cards
num_docs, num_chunks = get_db_status()
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"<div class='metric-card'><strong>Active Model</strong><br><span style='font-size: 20px; font-weight: bold;'>{st.session_state.current_model or 'Initializing...'}</span></div>",
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"<div class='metric-card'><strong>Indexed Manuals</strong><br><span style='font-size: 20px; font-weight: bold;'>{num_docs} Files</span></div>",
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"<div class='metric-card'><strong>Total Chunks</strong><br><span style='font-size: 20px; font-weight: bold;'>{num_chunks} Chunks</span></div>",
        unsafe_allow_html=True
    )

# Chat Messages Rendering
st.markdown("---")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Use HTML renderer to support highlighted badges
        st.markdown(message["content"], unsafe_allow_html=True)
        
        # Display Latency Metrics right below the response
        if "latency" in message:
            st.markdown(f"<span style='color: #64748b; font-size: 0.85em;'>Latency: {message['latency']:.3f} seconds</span>", unsafe_allow_html=True)
            
        # Display Retrieved Context & Metadata
        if "chunks" in message and message["chunks"]:
            with st.expander("Retrieved Context & Metadata"):
                for idx, chunk in enumerate(message["chunks"]):
                    approx_tokens = int(len(chunk['content']) / 4)
                    st.markdown(
                        f"**Source {idx+1}:** `{chunk['filename']}` | "
                        f"**Similarity Score:** `{chunk['score']:.3f}` | "
                        f"**Chunk Index:** `{chunk['chunk_index']}` | "
                        f"**Approx. Tokens:** `{approx_tokens}`"
                    )
                    st.code(chunk["content"], language="markdown")

# Take user query input
if prompt := st.chat_input("Ask a question about UAV maintenance, calibration, or emergency procedures..."):
    # Append user prompt
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process query
    with st.chat_message("assistant"):
        if st.session_state.rag_engine:
            with st.spinner("Retrieving relevant documents and generating answer..."):
                answer, retrieved_chunks, latency = st.session_state.rag_engine.query(prompt)
                
                # Format citations visually
                formatted_answer = format_citations(answer)
                
                # Render response
                st.markdown(formatted_answer, unsafe_allow_html=True)
                st.markdown(f"<span style='color: #64748b; font-size: 0.85em;'>Latency: {latency:.3f} seconds</span>", unsafe_allow_html=True)
                
                # Display context details
                if retrieved_chunks:
                    with st.expander("Retrieved Context & Metadata"):
                        for idx, chunk in enumerate(retrieved_chunks):
                            approx_tokens = int(len(chunk['content']) / 4)
                            st.markdown(
                                f"**Source {idx+1}:** `{chunk['filename']}` | "
                                f"**Similarity Score:** `{chunk['score']:.3f}` | "
                                f"**Chunk Index:** `{chunk['chunk_index']}` | "
                                f"**Approx. Tokens:** `{approx_tokens}`"
                            )
                            st.code(chunk["content"], language="markdown")
                
                # Save answer to state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": formatted_answer,
                    "chunks": retrieved_chunks,
                    "latency": latency
                })
        else:
            st.error("System error: The local inference engine was not loaded successfully.")

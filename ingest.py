import os
import sqlite3
import numpy as np
import sys
from foundry_local_sdk import Configuration, FoundryLocalManager

# Project folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "uav_knowledgebase.db")

def chunk_document(content, max_chars=1500, min_chars=150):
    """
    Splits text content into semantic chunks (roughly 200-400 tokens / 1000-1500 chars).
    """
    paragraphs = content.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        
        # If it's a heading or starting a new logical section, and the current chunk has some content
        if p.startswith('#') and current_length > min_chars:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [p]
            current_length = len(p)
        else:
            current_chunk.append(p)
            current_length += len(p) + 2
            if current_length >= max_chars:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = []
                current_length = 0
                
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
        
    valid_chunks = [c.strip() for c in chunks if c.strip()]
    return valid_chunks

def init_db():
    """
    Initializes the SQLite database and drops/creates the documents table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS documents")
    cursor.execute("""
        CREATE TABLE documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            chunk_index INTEGER,
            content TEXT,
            embedding_blob BLOB
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def get_embedding_client():
    """
    Initializes Foundry Local SDK and loads the embedding model.
    """
    print("Initializing Foundry Local SDK...")
    try:
        config = Configuration(app_name="uav_rag_app")
        FoundryLocalManager.initialize(config)
    except Exception:
        pass
    manager = FoundryLocalManager.instance
    
    model_alias = "qwen3-embedding-0.6b"
    model = manager.catalog.get_model(model_alias)
    
    if not model.is_cached:
        print(f"Embedding model '{model_alias}' is not cached. Downloading...")
        model.download()
    
    if not model.is_loaded:
        print(f"Loading embedding model '{model_alias}'...")
        model.load()
        
    return model.get_embedding_client(), model_alias

def main():
    if not os.path.exists(DATA_DIR):
        print(f"Data directory '{DATA_DIR}' does not exist. Please create it first.")
        sys.exit(1)
        
    init_db()
    
    try:
        client, model_alias = get_embedding_client()
    except Exception as e:
        print("Failed to load embedding model:", e)
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".md") or f.endswith(".txt")]
    print(f"Found files to ingest: {files}")
    
    total_chunks = 0
    for filename in files:
        file_path = os.path.join(DATA_DIR, filename)
        print(f"Processing '{filename}'...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        chunks = chunk_document(content)
        print(f"Split '{filename}' into {len(chunks)} chunks.")
        
        for idx, chunk in enumerate(chunks):
            # Compute embedding
            try:
                response = client.generate_embedding(chunk)
                embedding = response.data[0].embedding
                
                # Convert embedding to numpy binary format
                emb_array = np.array(embedding, dtype=np.float32)
                emb_blob = emb_array.tobytes()
                
                cursor.execute(
                    "INSERT INTO documents (filename, chunk_index, content, embedding_blob) VALUES (?, ?, ?, ?)",
                    (filename, idx, chunk, emb_blob)
                )
                total_chunks += 1
            except Exception as e:
                print(f"Error embedding chunk {idx} of {filename}: {e}")
                
    conn.commit()
    conn.close()
    print(f"Ingestion pipeline completed! Total chunks stored: {total_chunks}")

if __name__ == "__main__":
    main()

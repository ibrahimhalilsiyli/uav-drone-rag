import os
import sqlite3
import numpy as np
from foundry_local_sdk import Configuration, FoundryLocalManager

# Project folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "uav_knowledgebase.db")

class UAVRetriever:
    def __init__(self, model_alias="qwen3-embedding-0.6b"):
        self.model_alias = model_alias
        self._initialize_sdk()
        
    def _initialize_sdk(self):
        """
        Initializes Foundry Local SDK and gets the embedding client.
        """
        # Configuration is app-wide. If already initialized, SDK handles it.
        try:
            config = Configuration(app_name="uav_rag_app")
            FoundryLocalManager.initialize(config)
        except Exception:
            pass
        self.manager = FoundryLocalManager.instance
        
        # Load embedding model
        self.model = self.manager.catalog.get_model(self.model_alias)
        if not self.model.is_cached:
            print(f"Retriever: Downloading embedding model '{self.model_alias}'...")
            self.model.download()
        if not self.model.is_loaded:
            print(f"Retriever: Loading embedding model '{self.model_alias}'...")
            self.model.load()
            
        self.client = self.model.get_embedding_client()

    def get_query_embedding(self, query):
        """
        Generates embedding vector for a given query string.
        """
        response = self.client.generate_embedding(query)
        return response.data[0].embedding

    def retrieve(self, query, k=3):
        """
        Performs vector similarity search against stored chunks in SQLite and returns top K.
        """
        if not os.path.exists(DB_PATH):
            print("Warning: Database does not exist. Run ingest.py first.")
            return []

        # Get query embedding
        query_emb = np.array(self.get_query_embedding(query), dtype=np.float32)
        norm_query = np.linalg.norm(query_emb)
        if norm_query == 0:
            norm_query = 1e-8

        # Connect to SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT filename, chunk_index, content, embedding_blob FROM documents")
        rows = cursor.fetchall()
        conn.close()

        results = []
        for filename, chunk_index, content, emb_blob in rows:
            # Reconstruct document vector from binary blob
            doc_emb = np.frombuffer(emb_blob, dtype=np.float32)
            norm_doc = np.linalg.norm(doc_emb)
            if norm_doc == 0:
                norm_doc = 1e-8
            
            # Compute cosine similarity
            similarity = np.dot(query_emb, doc_emb) / (norm_query * norm_doc)
            
            results.append({
                "filename": filename,
                "chunk_index": chunk_index,
                "content": content,
                "score": float(similarity)
            })

        # Sort by similarity score in descending order
        results.sort(key=lambda x: x["score"], reverse=True)

        # Apply similarity threshold — reject chunks below relevance cutoff
        # In-domain queries typically score 0.50+; off-topic queries score <0.40
        SIMILARITY_THRESHOLD = 0.45
        filtered = [r for r in results[:k] if r["score"] >= SIMILARITY_THRESHOLD]

        if not filtered:
            print(f"Retriever: All scores below threshold ({SIMILARITY_THRESHOLD}). Query appears off-domain.")
            return []

        return filtered

if __name__ == "__main__":
    # Quick CLI test of the retriever
    print("Testing Retriever...")
    retriever = UAVRetriever()
    test_query = "What is the battery voltage limit?"
    print(f"Query: '{test_query}'")
    matches = retriever.retrieve(test_query, k=2)
    for idx, match in enumerate(matches):
        print(f"\nMatch {idx+1} [Score: {match['score']:.4f}] from '{match['filename']}' (Chunk {match['chunk_index']}):")
        print(match['content'][:200] + "...")

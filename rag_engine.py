import os
import sys
from foundry_local_sdk import Configuration, FoundryLocalManager
from retriever import UAVRetriever

class UAVRAGEngine:
    def __init__(self, llm_alias="phi-3.5-mini", embedding_alias="qwen3-embedding-0.6b"):
        self.llm_alias = llm_alias
        self.embedding_alias = embedding_alias
        
        # Initialize Retriever
        print("Initializing retriever...")
        self.retriever = UAVRetriever(model_alias=embedding_alias)
        
        # Initialize LLM
        self._initialize_llm()

    def _initialize_llm(self):
        """
        Initializes Foundry Local SDK and loads the chat model.
        """
        # Configuration is already initialized by UAVRetriever, but we specify it just in case
        try:
            config = Configuration(app_name="uav_rag_app")
            FoundryLocalManager.initialize(config)
        except Exception:
            pass
        self.manager = FoundryLocalManager.instance
        
        # Select model (fallback to cached ones if the requested one is not cached yet)
        target_model = self.llm_alias
        try:
            m = self.manager.catalog.get_model(target_model)
            if not m.is_cached:
                # Check fallback models that might be cached
                for fallback in ["qwen2.5-0.5b", "qwen3-0.6b"]:
                    fallback_model = self.manager.catalog.get_model(fallback)
                    if fallback_model.is_cached:
                        print(f"RAGEngine: '{target_model}' is not cached. Falling back to cached model '{fallback}'.")
                        target_model = fallback
                        break
        except Exception as e:
            print(f"RAGEngine: Error resolving model fallback: {e}")

        self.llm_alias = target_model
        self.model = self.manager.catalog.get_model(self.llm_alias)
        
        if not self.model.is_cached:
            print(f"RAGEngine: Downloading LLM '{self.llm_alias}' (this may take a few minutes)...")
            self.model.download()
        if not self.model.is_loaded:
            print(f"RAGEngine: Loading LLM '{self.llm_alias}'...")
            self.model.load()
            
        self.chat_client = self.model.get_chat_client()

    def query(self, user_query, k=3):
        """
        Retrieves context and generates an answer using the local LLM.
        """
        import time
        start_time = time.perf_counter()
        
        # Step 1: Retrieve relevant chunks
        retrieved_chunks = self.retriever.retrieve(user_query, k=k)
        
        if not retrieved_chunks:
            # If nothing is in the database
            latency = time.perf_counter() - start_time
            return "I do not have sufficient field documentation to answer this question.", [], latency

        # Step 2: Format the context string
        context_str = ""
        for chunk in retrieved_chunks:
            context_str += f"--- START OF CONTEXT (Source: {chunk['filename']}) ---\n"
            context_str += f"{chunk['content']}\n"
            context_str += f"--- END OF CONTEXT ---\n\n"

        # Step 3: Build prompt — use explicit markers for small model compliance
        system_prompt = (
            "You are a UAV technical assistant. "
            "Answer using ONLY the information in the CONTEXT section below. "
            "Do NOT use any outside knowledge. "
            "For every fact, cite the actual source filename from the context header, "
            "for example: [Source: failsafe_protocols.md] or [Source: preflight_checklist.md]. "
            "If the CONTEXT does not contain the answer, respond with exactly: "
            "'I do not have sufficient field documentation to answer this question.'"
        )

        user_content = (
            f"CONTEXT:\n{context_str}\n"
            f"QUESTION: {user_query}\n\n"
            f"ANSWER (cite the actual source filename for every fact):"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        # Step 4: Generate response via local LLM
        # temperature=0 → deterministic, reproducible output (critical for small models)
        # max_tokens=512 → prevent truncation while keeping responses focused
        try:
            print(f"Generating answer using model '{self.llm_alias}'...")
            response = self.chat_client.complete_chat(
                messages,
                temperature=0,
                max_tokens=512
            )
            answer = response.choices[0].message.content
        except TypeError:
            # Fallback: some SDK versions don't support extra kwargs
            response = self.chat_client.complete_chat(messages)
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Error during local model inference: {e}"

        # Step 5: Validate answer quality
        # Strip citations like [Source: x.md] and check remaining content length.
        # If only citations remain (no real content), model couldn't answer — return refusal.
        import re
        stripped = re.sub(r'\[Source:[^\]]+\]', '', answer).strip()
        MINIMUM_CONTENT_LENGTH = 30
        if len(stripped) < MINIMUM_CONTENT_LENGTH:
            print("RAGEngine: Answer too short after stripping citations — treating as off-domain.")
            answer = "I do not have sufficient field documentation to answer this question."
            retrieved_chunks = []  # Don't show misleading context

        latency = time.perf_counter() - start_time
        return answer, retrieved_chunks, latency

if __name__ == "__main__":
    # Quick CLI test of the engine
    print("Testing RAG Engine...")
    engine = UAVRAGEngine()
    
    test_query = "What is the emergency procedure for a quadcopter motor loss?"
    print(f"Query: {test_query}")
    ans, chunks, latency = engine.query(test_query)
    print("\n--- Answer ---")
    print(ans)
    print(f"\nLatency: {latency:.3f} seconds")
    print("\n--- Sources ---")
    for c in chunks:
        print(f"- {c['filename']} (Score: {c['score']:.4f})")

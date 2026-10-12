from llm import call_ollama

class Reranker:
    def __init__(self, model="llama2"):
        self.model = model

    def rank(self, query, chunks, top_k=3):

        if not chunks:
            return []

        # Build the prompt for the LLM reranker
        chunk_texts = [f"{i}: {c['chunk']}" for i, c in enumerate(chunks)]
        prompt = (
            "You are an expert assistant. "
            "Given the following text chunks and a user question, "
            "rank the chunks by relevance to the question. "
            "Return only a comma-separated list of chunk indices (highest relevance first).\n\n"
            f"Chunks:\n{chr(10).join(chunk_texts)}\n\n"
            f"Question: {query}\n"
            "Indices:"
        )

        # Call the LLM
        try:
            response = call_ollama(prompt, model=self.model)

            # Parse response: expect comma-separated indices
            indices = [int(x.strip()) for x in response.split(",") if x.strip().isdigit()]

            # Return top_k chunks in reranked order
            top_chunks = [chunks[i] for i in indices if i < len(chunks)]
            return top_chunks[:top_k]

        except Exception as e:
            # Fallback: return first top_k chunks if anything goes wrong
            print(f"[Reranker] Warning: LLM rerank failed: {e}")
            return chunks[:top_k]

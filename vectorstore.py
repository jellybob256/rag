import faiss
import numpy as np
from embeddings import get_embedding
from llm import call_ollama  # ✅ import from llm.py, no circular import

chunks = []
metadata = []
index = None
dimension = None


def summarize_chunk(chunk_text):
    """
    Uses the LLM to summarize a chunk into a short summary.
    """
    prompt = f"""
Summarize the following text into 2-3 concise sentences that capture the main idea:
{chunk_text}
Summary:
"""
    summary = call_ollama(prompt, model="llama2")
    return summary


def add_to_vectorstore(chunks_to_add, source):
    global chunks, metadata, index, dimension

    vectors = []

    for chunk in chunks_to_add:
        # 1️⃣ Summarize chunk
        summary = summarize_chunk(chunk)

        # 2️⃣ Get embedding from the summary
        vec = get_embedding(summary)

        # Initialize index on first vector
        if index is None:
            dimension = len(vec)
            index = faiss.IndexFlatL2(dimension)

        vectors.append(vec)

        # Store both original chunk and summary in memory
        chunks.append({"original": chunk, "summary": summary})
        metadata.append({"source": source})

    vectors = np.array(vectors, dtype=np.float32)
    index.add(vectors)

    return len(vectors)


def retrieve(query, top_k=3):
    """
    Retrieves top_k chunks based on query embeddings of summaries.
    Returns original chunks for LLM.
    """
    if index is None:
        return []

    query_vec = get_embedding(query).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_vec, top_k)

    results = []
    for i in indices[0]:
        results.append({
            "chunk": chunks[i]["original"],  # return full text for LLM
            "source": metadata[i]["source"]
        })

    return results


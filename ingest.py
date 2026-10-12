import os

def load_docs(path="data/"):
    docs = []
    for filename in os.listdir(path):
        if filename.endswith(".txt"):
            with open(os.path.join(path, filename), "r", encoding="utf-8") as f:
                docs.append({"filename": filename, "content": f.read()})
    return docs

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks

def load_and_chunk_all_docs(path="data/"):
    """
    Load all documents from disk and chunk them.
    Returns:
        chunks: list of dicts {"chunk": text}
        metadata: list of dicts {"source": filename}
    """
    docs = load_docs(path)
    chunks = []
    metadata = []
    for doc in docs:
        doc_chunks = chunk_text(doc["content"])
        for chunk in doc_chunks:
            chunks.append({"chunk": chunk})
            metadata.append({"source": doc["filename"]})
    return chunks, metadata

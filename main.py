import os
import json
import time
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import redis
import logging
from vectorstore import retrieve, add_to_vectorstore
from ingest import chunk_text
from reranker import call_ollama

# -----------------------------
# App & CORS setup
# -----------------------------
app = FastAPI()

origins = ["http://127.0.0.1", "http://localhost"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag")

# -----------------------------
# Frontend
# -----------------------------
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend")
frontend_index = os.path.join(frontend_path, "index.html")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse(frontend_index)

# -----------------------------
# Redis for caching
# -----------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
# -----------------------------
# Models
# -----------------------------
class Query(BaseModel):
    question: str

# -----------------------------
# Metrics in-memory
# -----------------------------
metrics = {
    "total_questions": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "total_latency_ms": 0,
    "total_tokens": 0,
    "average_latency_ms": 0,
    "average_tokens": 0,
    "feedback_count": 0
}

# -----------------------------
# Health check
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------
# Ask endpoint with latency, token usage, Redis caching
# -----------------------------
@app.post("/ask")
def ask(query: Query):
    question = query.question.strip()
    metrics["total_questions"] += 1

    # Try to get cached answer from Redis
    cached_value = r.get(question)
    if cached_value:
        metrics["cache_hits"] += 1
        data = json.loads(cached_value)
        data["cached"] = True
        return data

    # Cache miss → process the question
    start_time = time.time()
    results = retrieve(question, top_k=3)
    context = "\n---\n".join([r["chunk"] for r in results])

    prompt = f"Answer the question based on the following context:\n{context}\nQuestion: {question}\nAnswer:"
    llm_response_raw = call_ollama(prompt)  # returns JSON string
    llm_response = json.loads(llm_response_raw)

    # For this response format
    answer = llm_response.get("text")  # directly get the "text" field

    latency_ms = (time.time() - start_time) * 1000
    metrics["total_latency_ms"] += latency_ms
    #metrics["total_tokens"] += tokens_used
    metrics["average_latency_ms"] = metrics["total_latency_ms"] / metrics["total_questions"]
    #metrics["average_tokens"] = metrics["total_tokens"] / metrics["total_questions"]
    metrics["cache_misses"] += 1

    # Cache the answer in Redis
    cache_data = {
        "context": context,
        "results": results,
        "answer": answer,
        "cached": False,
        "latency_ms": latency_ms,
        #"tokens": tokens_used
    }
    r.set(question, json.dumps(cache_data))

    return cache_data

# -----------------------------
# Ingest endpoint (multi-file upload)
# -----------------------------
@app.post("/ingest")
async def ingest(files: list[UploadFile] = File(...)):
    total_chunks = 0
    for file in files:
        text = await file.read()
        text = text.decode("utf-8")
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        count = add_to_vectorstore(chunks, source=file.filename)
        total_chunks += count
    return {"message": f"Ingested {len(files)} files, {total_chunks} chunks added."}

# -----------------------------
# Feedback endpoint to collect user feedback
# -----------------------------
@app.post("/feedback")
async def feedback(data: dict):
    question = data.get("question")
    answer = data.get("answer")
    score = data.get("score")  # Numeric relevance/quality score
    comment = data.get("comment", "")

    cached_value = r.get(question)
    if not cached_value:
        return {"status": "error", "message": "Question not found in cache."}

    cache_entry = json.loads(cached_value)
    if "feedback" not in cache_entry:
        cache_entry["feedback"] = []
    feedback_entry = {
        "answer": answer,
        "score": score,
        "comment": comment,
        "timestamp": time.time()
    }
    cache_entry["feedback"].append(feedback_entry)

    r.set(question, json.dumps(cache_entry))  # Update cached entry with feedback
    metrics["feedback_count"] += 1

    print(f"Feedback received for '{question[:50]}...': {score} - {comment}")
    logger.info(f"Feedback score={score} question={question[:30]}")
    return {"status": "ok"}

# -----------------------------
# Metrics endpoint returning collected metrics and Redis cache size
# -----------------------------
@app.get("/metrics")
def get_metrics():
    return {
        **metrics,
        "cache_size": r.dbsize()
    }

@app.get("/metrics/prom")
def prom_metrics():
    return {
        "total_questions": metrics["total_questions"],
        "cache_hit_ratio": (
            metrics["cache_hits"] /
            max(1, metrics["total_questions"])
        ),
        "avg_latency_ms": metrics["average_latency_ms"],
        "feedback_count": metrics["feedback_count"]
    }

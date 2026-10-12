import subprocess
import numpy as np
import json

OLLAMA_PATH = r"C:\Users\GH22208\AppData\Local\Programs\Ollama\ollama.exe"

def get_embedding(text, model="nomic-embed-text"):
    """
    Get embedding from Ollama CLI using subprocess.
    Uses 'ollama run <model> <text>' and parses the JSON array output.
    """
    try:
        # Run the embedding model via Ollama CLI
        result = subprocess.run(
        [OLLAMA_PATH, "run", model, text],
        capture_output=True,
        text=True,
        encoding="utf-8",  # <--- important
        check=True
    )


        # Ollama outputs a JSON array like: [0.123, 0.456, ...]
        vector = np.array(json.loads(result.stdout), dtype=np.float32)
        return vector

    except subprocess.CalledProcessError as e:
        print("Error getting embedding:", e)
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)
        # fallback vector (size depends on model, adjust if needed)
        return np.zeros(1, dtype=np.float32)

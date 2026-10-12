# Use Python slim image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install dependencies for Ollama (if needed)
RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY ./app ./app

# Install Ollama Linux binary
RUN curl -fsSL https://ollama.com/download/linux/ollama -o /usr/local/bin/ollama && \
    chmod +x /usr/local/bin/ollama

# Expose port
EXPOSE 8000

# Run FastAPI with Gunicorn + Uvicorn workers
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000"]

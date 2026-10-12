# import subprocess

# # OLLAMA_PATH = r"C:\Users\GH22208\AppData\Local\Programs\Ollama\ollama.exe"
# OLLAMA_PATH = r"/usr/local/bin/ollama"


# def call_ollama(prompt, model="llama2"):
#     """
#     Call Ollama LLM with a prompt and return the response text.
#     """
#     try:
#         result = subprocess.run(
#             [OLLAMA_PATH, "run", model, prompt, "--format", "json"],
#             capture_output=True,
#             text=True,
#             check=True,
#         )

#         print("stdout:", result.stdout)
#         print("stderr:", result.stderr)
#         print("returncode:", result.returncode)

#         return result.stdout.strip()
#     except subprocess.CalledProcessError as e:
#         return f"Error calling Ollama: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}"
import subprocess

OLLAMA_PATH = "/usr/local/bin/ollama"

def call_ollama(prompt, model="llama2"):
    try:
        result = subprocess.run(
            [OLLAMA_PATH, "run", model, prompt, "--format", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error calling Ollama: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}"

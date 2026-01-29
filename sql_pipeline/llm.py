import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2:7b"  # OR gemma:7b if installed

def llm_call(prompt: str) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    data = resp.json()

    if "response" not in data:
        raise RuntimeError(f"Ollama error: {data}")

    return data["response"].strip()

qwen = llm_call
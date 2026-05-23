import requests

def ask_ollama(prompt: str, model: str = "llama3.2:3b") -> str:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=240,
    )
    response.raise_for_status()
    return response.json()["response"]

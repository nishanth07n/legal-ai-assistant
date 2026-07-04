import requests

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

CPU_ONLY_OPTIONS = {
    "num_gpu": 0
}


def generate_with_ollama(prompt, timeout=120, options=None):
    request_options = {
        **CPU_ONLY_OPTIONS,
        **(options or {})
    }

    response = requests.post(
        OLLAMA_GENERATE_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": request_options
        },
        timeout=timeout
    )

    response.raise_for_status()
    return response.json()

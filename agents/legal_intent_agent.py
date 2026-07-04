import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"


def detect_legal_domain(text):

    prompt = f"""
You are an expert legal classifier.

Classify the user's legal issue into ONE category.

Possible categories:
- criminal
- consumer
- cybercrime
- property
- family
- civil
- unknown

User problem:
{text}

Return JSON:

{{
 "domain": "category"
}}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    output = response.json()["response"]

    try:
        start = output.find("{")
        end = output.rfind("}") + 1
        data = json.loads(output[start:end])
        return data.get("domain", "unknown")

    except:
        return "unknown"
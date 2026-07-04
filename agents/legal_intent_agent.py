import json
from agents.ollama_client import generate_with_ollama


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

    response_json = generate_with_ollama(prompt)

    output = response_json["response"]

    try:
        start = output.find("{")
        end = output.rfind("}") + 1
        data = json.loads(output[start:end])
        return data.get("domain", "unknown")

    except:
        return "unknown"

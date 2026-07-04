import re
import requests

from vector_store.case_law_vector_store import search_case_law


# ---------------- CLEAN VERDICT ----------------

def clean_verdict_text(text):

    if not text:
        return "Verdict not available"

    # Remove extra spaces/newlines
    text = re.sub(r"\s+", " ", str(text))

    # Remove weird characters
    text = text.replace("\n", " ")

    # Trim large text
    text = text[:500]

    return text.strip()


# ---------------- SUMMARIZE VERDICT USING OLLAMA ----------------

def summarize_verdict(verdict_text):

    try:

        prompt = f"""
        Summarize this legal verdict in 2-3 simple and clear lines.

        Verdict:
        {verdict_text}
        """

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        return response.json()["response"].strip()

    except Exception:

        # fallback if Ollama fails
        return verdict_text


# ---------------- MAIN FUNCTION ----------------

def retrieve_case_law(text):

    results = search_case_law(text, top_k=3)

    formatted = []

    for r in results:

        raw_verdict = clean_verdict_text(
            r.get("verdict", "")
        )

        summarized_verdict = summarize_verdict(
            raw_verdict
        )

        formatted.append({

            "title": r.get("title", ""),

            "summary": r.get("summary", ""),

            "sections": r.get("sections", []),

            "verdict": summarized_verdict,

            "source_link": r.get("source_link", "")

        })

    return formatted
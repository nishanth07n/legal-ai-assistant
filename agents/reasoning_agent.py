import json
import re

from agents.ollama_client import generate_with_ollama


MAX_CONTEXT_ITEMS = 2
OLLAMA_TIMEOUT = 300
OLLAMA_OPTIONS = {
    "temperature": 0.1,
    "num_predict": 220
}


def extract_json(text):
    """Extract the first valid JSON object from model text."""
    if not text:
        return None

    cleaned = str(text).strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    decoder = json.JSONDecoder()
    start_positions = [
        index for index, char in enumerate(cleaned)
        if char == "{"
    ]

    for start in start_positions:
        try:
            parsed, _ = decoder.raw_decode(cleaned[start:])
        except json.JSONDecodeError:
            continue

        if isinstance(parsed, dict):
            return parsed

    return None


def clean_text(text):
    if not text:
        return ""

    return re.sub(r"\s+", " ", str(text)).strip()


def _trimmed_text(value, limit=280):
    text = clean_text(value)
    if len(text) <= limit:
        return text

    return text[:limit].rsplit(" ", 1)[0].strip()


def _prepare_ipc_sections(ipc_sections):
    clean_ipc = []

    for ipc in (ipc_sections or [])[:MAX_CONTEXT_ITEMS]:
        if not isinstance(ipc, dict):
            continue

        clean_ipc.append({
            "section": clean_text(ipc.get("section_or_article", "")),
            "title": clean_text(ipc.get("title", ""))
        })

    return clean_ipc


def _prepare_case_laws(case_laws):
    clean_cases = []

    for case in (case_laws or [])[:MAX_CONTEXT_ITEMS]:
        if not isinstance(case, dict):
            continue

        clean_cases.append({
            "title": clean_text(case.get("title", "")),
            "summary": _trimmed_text(case.get("summary", ""))
        })

    return clean_cases


def _base_prompt(user_text, domain, ipc_sections, case_laws):
    return (
        "You are Gemma 3 1B acting as an Indian legal assistant. "
        "Return only compact valid JSON. No markdown.\n\n"
        f"Problem: {_trimmed_text(user_text, 700)}\n"
        f"Domain: {clean_text(domain)}\n"
        f"IPC: {json.dumps(ipc_sections, ensure_ascii=True)}\n"
        f"Cases: {json.dumps(case_laws, ensure_ascii=True)}\n"
    )


def _build_prompt(user_text, ipc_sections, case_laws, role, domain):
    base = _base_prompt(user_text, domain, ipc_sections, case_laws)

    if role == "Lawyer":
        return base + """
JSON schema:
{
  "legal_analysis": "max 90 words",
  "simple_explanation": "plain language",
  "severity_level": "Low/Moderate/High",
  "recommended_next_steps": ["step 1", "step 2"],
  "estimated_legal_timeline": {
    "FIR Registration": "...",
    "Investigation": "...",
    "Trial": "...",
    "Final Judgment": "..."
  },
  "cross_examination_questions": ["q1", "q2", "q3"],
  "document_comparison": "brief note",
  "legal_probability_prediction": {
    "Conviction Probability": "...",
    "Bail Probability": "...",
    "Settlement Chance": "..."
  }
}
Rules: be concise; do not repeat IPC text; use case facts only.
"""

    return base + """
JSON schema:
{
  "legal_analysis": "max 70 words",
  "simple_explanation": "plain language",
  "severity_level": "Low/Moderate/High",
  "recommended_next_steps": ["step 1", "step 2"]
}
Rules: simple citizen-friendly language; do not repeat IPC text.
"""


def _clean_steps(steps):
    if not isinstance(steps, list):
        return []

    return [
        clean_text(step)
        for step in steps
        if clean_text(step)
    ]


def _base_response(parsed):
    return {
        "legal_analysis": clean_text(parsed.get("legal_analysis", "")),
        "simple_explanation": clean_text(parsed.get("simple_explanation", "")),
        "severity_level": clean_text(parsed.get("severity_level", "Moderate")),
        "recommended_next_steps": _clean_steps(
            parsed.get("recommended_next_steps", [])
        )
    }


def _lawyer_fields(parsed):
    timeline = parsed.get("estimated_legal_timeline", {})
    probabilities = parsed.get("legal_probability_prediction", {})

    return {
        "estimated_legal_timeline": (
            timeline if isinstance(timeline, dict) else {}
        ),
        "cross_examination_questions": _clean_steps(
            parsed.get("cross_examination_questions", [])
        ),
        "document_comparison": clean_text(
            parsed.get("document_comparison", "")
        ),
        "legal_probability_prediction": (
            probabilities if isinstance(probabilities, dict) else {}
        )
    }


def _fallback_response(output, role):
    response = {
        "legal_analysis": clean_text(output),
        "simple_explanation": "The legal issue was analyzed successfully.",
        "severity_level": "Moderate",
        "recommended_next_steps": [
            "Consult a lawyer.",
            "Review supporting documents."
        ]
    }

    if role == "Lawyer":
        response.update({
            "estimated_legal_timeline": {},
            "cross_examination_questions": [],
            "document_comparison": "",
            "legal_probability_prediction": {}
        })

    return response


def _error_response(error):
    return {
        "legal_analysis": f"Error: {str(error)}",
        "simple_explanation": "System could not process request.",
        "severity_level": "Unknown",
        "recommended_next_steps": [
            "Retry request",
            "Check backend connection"
        ],
        "estimated_legal_timeline": {},
        "cross_examination_questions": [],
        "document_comparison": "",
        "legal_probability_prediction": {}
    }


def run_reasoning_agent(
    user_text,
    ipc_sections,
    case_laws,
    role,
    domain
):
    clean_ipc = _prepare_ipc_sections(ipc_sections)
    clean_cases = _prepare_case_laws(case_laws)
    prompt = _build_prompt(user_text, clean_ipc, clean_cases, role, domain)

    try:
        response_json = generate_with_ollama(
            prompt,
            timeout=OLLAMA_TIMEOUT,
            options=OLLAMA_OPTIONS
        )

        output = response_json.get("response", "No response generated.")
        parsed = extract_json(output)

        if not parsed:
            return _fallback_response(output, role)

        final_response = _base_response(parsed)

        if role == "Lawyer":
            final_response.update(_lawyer_fields(parsed))

        return final_response

    except Exception as e:
        return _error_response(e)

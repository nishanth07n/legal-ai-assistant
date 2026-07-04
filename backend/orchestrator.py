from agents.document_agent import process_document
from agents.translation_agent import translate_to_english
from agents.similar_case_agent import get_similar_cases
from agents.case_law_agent import retrieve_case_law
from agents.reasoning_agent import run_reasoning_agent


def detect_domain(text):

    text = text.lower()

    if any(word in text for word in ["mrp", "price", "shop", "consumer", "product"]):
        return "consumer"

    if any(word in text for word in ["hack", "fraud", "online", "cyber", "otp"]):
        return "cybercrime"

    if any(word in text for word in ["murder", "kill", "theft", "steal", "assault"]):
        return "criminal"

    return "civil"


def run_agents(text, role):

    # ---------------- DOCUMENT PROCESSING ----------------
    doc = process_document(text)

    processed_text = doc["content"]

    if doc["language"] != "en":
        processed_text = translate_to_english(processed_text)

    processed_text = processed_text.lower()

    # ---------------- DOMAIN DETECTION ----------------
    domain = detect_domain(processed_text)

    # ---------------- IPC RETRIEVAL ----------------
    ipc_sections = get_similar_cases(processed_text)

    # ---------------- CASE LAW RETRIEVAL ----------------
    case_laws = retrieve_case_law(processed_text)

    # ---------------- LLM REASONING ----------------
    reasoning = run_reasoning_agent(
        processed_text,
        ipc_sections,
        case_laws,
        role,
        domain
    )

    result = {
        "detected_language": doc["language"],
        "processed_text": processed_text,
        "domain": domain,
        "ipc_sections": ipc_sections,
        "case_laws": case_laws,
        "legal_analysis": reasoning.get("legal_analysis", ""),
        "simple_explanation": reasoning.get("simple_explanation", ""),
        "severity_level": reasoning.get("severity_level", "Unknown"),
        "recommended_next_steps": reasoning.get("recommended_next_steps", [])
    }

    return result
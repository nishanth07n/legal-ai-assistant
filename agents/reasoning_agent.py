import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"


# =====================================================
# ================= JSON EXTRACTION ===================
# =====================================================

def extract_json(text):

    try:

        # Remove markdown formatting
        text = text.replace("```json", "")
        text = text.replace("```", "")

        # Extract JSON block
        start = text.find("{")
        end = text.rfind("}") + 1

        if start != -1 and end != -1:

            json_text = text[start:end]

            parsed = json.loads(json_text)

            return parsed

    except Exception as e:

        print("JSON Extraction Error:", e)

    return None


# =====================================================
# ================= CLEAN TEXT ========================
# =====================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =====================================================
# ================= MAIN AGENT ========================
# =====================================================

def run_reasoning_agent(
    user_text,
    ipc_sections,
    case_laws,
    role,
    domain
):

    # =================================================
    # ============ CLEAN IPC DATA =====================
    # =================================================

    clean_ipc = []

    for ipc in ipc_sections:

        clean_ipc.append({

            "section":
                ipc.get(
                    "section_or_article",
                    ""
                ),

            "title":
                ipc.get(
                    "title",
                    ""
                )
        })

    # =================================================
    # ============ LAWYER PROMPT ======================
    # =================================================

    if role == "Lawyer":

        prompt = f"""
You are an Indian Legal AI Assistant for lawyers.

Analyze the case using the IPC sections and case laws.

User Problem:
{user_text}

Legal Domain:
{domain}

IPC Sections:
{json.dumps(clean_ipc)}

Case Laws:
{json.dumps(case_laws)}

Return ONLY valid JSON.

Format:

{{
  "legal_analysis": "...",

  "simple_explanation": "...",

  "severity_level": "...",

  "recommended_next_steps": [
    "...",
    "..."
  ],

  "estimated_legal_timeline": {{
    "FIR Registration": "...",
    "Investigation": "...",
    "Trial": "...",
    "Final Judgment": "..."
  }},

  "cross_examination_questions": [
    "...",
    "...",
    "..."
  ],

  "document_comparison": "...",

  "legal_probability_prediction": {{
    "Conviction Probability": "...",
    "Bail Probability": "...",
    "Settlement Chance": "..."
  }}
}}

Rules:
- Do NOT repeat IPC descriptions.
- Keep legal analysis under 120 words.
- Keep explanation simple.
- Questions must relate to the case.
- Timeline must be realistic.
- Probability must be realistic.
- Output ONLY JSON.
"""

    # =================================================
    # ============ CITIZEN PROMPT =====================
    # =================================================

    else:

        prompt = f"""
You are an Indian Legal AI Assistant for citizens.

Analyze the legal issue simply.

User Problem:
{user_text}

Legal Domain:
{domain}

IPC Sections:
{json.dumps(clean_ipc)}

Case Laws:
{json.dumps(case_laws)}

Return ONLY valid JSON.

Format:

{{
  "legal_analysis": "...",

  "simple_explanation": "...",

  "severity_level": "...",

  "recommended_next_steps": [
    "...",
    "..."
  ]
}}

Rules:
- Keep response simple.
- Do NOT repeat IPC descriptions.
- Output ONLY JSON.
"""

    # =================================================
    # ============ OLLAMA REQUEST =====================
    # =================================================

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.2,
                "num_predict": 700
            },
            timeout=120
        )

        response_json = response.json()

        print(response_json)

        output = response_json.get(
            "response",
            "No response generated."
        )

        # =================================================
        # ============ PARSE JSON ==========================
        # =================================================

        parsed = extract_json(output)

        # =================================================
        # ============ SUCCESS =============================
        # =================================================

        if parsed:

            final_response = {

                "legal_analysis": clean_text(
                    parsed.get(
                        "legal_analysis",
                        ""
                    )
                ),

                "simple_explanation": clean_text(
                    parsed.get(
                        "simple_explanation",
                        ""
                    )
                ),

                "severity_level": clean_text(
                    parsed.get(
                        "severity_level",
                        "Moderate"
                    )
                ),

                "recommended_next_steps": [
                    clean_text(step)
                    for step in parsed.get(
                        "recommended_next_steps",
                        []
                    )
                ]
            }

            # =============================================
            # ============ LAWYER FIELDS ==================
            # =============================================

            if role == "Lawyer":

                final_response.update({

                    "estimated_legal_timeline":
                        parsed.get(
                            "estimated_legal_timeline",
                            {}
                        ),

                    "cross_examination_questions": [
                        clean_text(q)
                        for q in parsed.get(
                            "cross_examination_questions",
                            []
                        )
                    ],

                    "document_comparison":
                        clean_text(
                            parsed.get(
                                "document_comparison",
                                ""
                            )
                        ),

                    "legal_probability_prediction":
                        parsed.get(
                            "legal_probability_prediction",
                            {}
                        )
                })

            return final_response

        # =================================================
        # ============ FALLBACK ============================
        # =================================================

        fallback_response = {

            "legal_analysis":
                clean_text(output),

            "simple_explanation":
                "The legal issue was analyzed successfully.",

            "severity_level":
                "Moderate",

            "recommended_next_steps": [
                "Consult a lawyer.",
                "Review supporting documents."
            ]
        }

        if role == "Lawyer":

            fallback_response.update({

                "estimated_legal_timeline": {},

                "cross_examination_questions": [],

                "document_comparison": "",

                "legal_probability_prediction": {}
            })

        return fallback_response

    # =====================================================
    # ================= ERROR HANDLING ====================
    # =====================================================

    except Exception as e:

        return {

            "legal_analysis":
                f"Error: {str(e)}",

            "simple_explanation":
                "System could not process request.",

            "severity_level":
                "Unknown",

            "recommended_next_steps": [
                "Retry request",
                "Check backend connection"
            ],

            "estimated_legal_timeline": {},

            "cross_examination_questions": [],

            "document_comparison": "",

            "legal_probability_prediction": {}
        }
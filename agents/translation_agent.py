HINDI_TO_ENGLISH = {
    "धोखाधड़ी": "cheating",
    "धोखा": "cheating",
    "आरोप": "allegation",
    "शिकायतकर्ता": "complainant",
    "विश्वासघात": "breach of trust",
}


def translate_to_english(text: str) -> str:
    translated = text
    for h, e in HINDI_TO_ENGLISH.items():
        translated = translated.replace(h, e)
    return translated.lower()
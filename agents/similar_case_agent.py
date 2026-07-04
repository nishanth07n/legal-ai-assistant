from vector_store.fir_vector_store import find_relevant_ipc
from vector_store.ipc_metadata_loader import get_ipc_metadata


def get_similar_cases(text):

    results = find_relevant_ipc(text, top_k=3)

    formatted = []

    for r in results:

        section = ""

        if r.get("url"):
            section = r["url"].split("-")[-1]

        meta = get_ipc_metadata(section)

        formatted.append({
            "act_name": "Indian Penal Code",
            "section_or_article": section,
            "title": r.get("offense") or meta.get("title", ""),
            "punishment": r.get("punishment") or meta.get("punishment", ""),
            "cognizable": r.get("cognizable") or meta.get("cognizable", ""),
            "bailable": r.get("bailable") or meta.get("bailable", ""),
            "court": r.get("court") or meta.get("court", ""),
            "url": r.get("url", "")
        })

    return formatted
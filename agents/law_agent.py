from vector_store.fir_vector_store import find_relevant_ipc


def identify_laws(text: str):
    ipc_matches = find_relevant_ipc(text)

    laws = []

    for match in ipc_matches:
        laws.append({
            "act_name": "Indian Penal Code",
            "section_or_article": match["offense"],
            "title": match["offense"],
            "punishment": match["punishment"],
            "cognizable": match["cognizable"],
            "bailable": match["bailable"],
            "court": match["court"],
            "url": match["url"]
        })

    return laws
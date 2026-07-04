def explain_ipc_sections(laws):
    explanations = []

    for law in laws:
        explanations.append(
            f"{law['act_name']} Section {law['section_or_article']} "
            f"relates to {law['title']} and defines criminal liability "
            f"along with prescribed punishment."
        )

    return explanations
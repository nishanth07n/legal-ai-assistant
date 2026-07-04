import json
import os
import numpy as np
from vector_store.model_config import EMBEDDING_MODEL_NAME, MODEL_DEVICE
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME, device=MODEL_DEVICE)

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "datasets",
    "indian_laws",
    "ipc_normalized.json"
)

with open(DATA_PATH, encoding="utf-8") as f:
    IPC_DATA = json.load(f)

# Prepare text for embedding
IPC_TEXTS = [
    f"{law['title']}. {law['text']}"
    for law in IPC_DATA
]

IPC_EMBEDDINGS = MODEL.encode(IPC_TEXTS, show_progress_bar=True)

def find_relevant_ipc_sections(query, top_k=5):
    query_embedding = MODEL.encode([query])
    scores = cosine_similarity(query_embedding, IPC_EMBEDDINGS)[0]

    ranked_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in ranked_indices:
        law = IPC_DATA[idx]
        results.append({
            "act_name": law["act"],
            "act_year": law["year"],
            "section_or_article": law["section"],
            "title": law["title"],
            "similarity": float(scores[idx])
        })

    return results

import os
import pandas as pd
from vector_store.model_config import EMBEDDING_MODEL_NAME, MODEL_DEVICE
from sentence_transformers import SentenceTransformer, util

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "consumer_law_dataset.csv")

df = pd.read_csv(DATASET_PATH)

model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=MODEL_DEVICE)

texts = df["summary"].astype(str).tolist()
embeddings = model.encode(texts, convert_to_tensor=True)


def search_consumer_law(query, top_k=3):

    query_embedding = model.encode(query, convert_to_tensor=True)

    scores = util.cos_sim(query_embedding, embeddings)[0]

    top_results = scores.topk(top_k)

    results = []

    for idx in top_results.indices:
        row = df.iloc[int(idx)]

        results.append({
            "title": row["title"],
            "summary": row["summary"],
            "law": row["law"],
            "source_link": row["source_link"]
        })

    return results

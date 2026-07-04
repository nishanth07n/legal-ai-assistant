import os
import pandas as pd
from vector_store.model_config import EMBEDDING_MODEL_NAME, MODEL_DEVICE
from sentence_transformers import (
    SentenceTransformer,
    util
)

# =====================================================
# ================= BASE PATH =========================
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "datasets",
    "case_law_dataset.csv"
)

# =====================================================
# ================= LOAD DATASET ======================
# =====================================================

df = pd.read_csv(DATASET_PATH)

# =====================================================
# ================= LOAD MODEL ========================
# =====================================================

model = SentenceTransformer(
    EMBEDDING_MODEL_NAME,
    device=MODEL_DEVICE
)

# =====================================================
# ================= COMBINED SEARCH TEXT ==============
# =====================================================

df["combined_text"] = (

    df["title"].fillna("").astype(str) + " " +

    df["summary"].fillna("").astype(str) + " " +

    df["sections"].fillna("").astype(str)
)

texts = df["combined_text"].tolist()

# =====================================================
# ================= CREATE EMBEDDINGS =================
# =====================================================

embeddings = model.encode(
    texts,
    convert_to_tensor=True
)

# =====================================================
# ================= CLEAN VALUE =======================
# =====================================================

def clean_value(v):

    if pd.isna(v):
        return ""

    return str(v).strip()

# =====================================================
# ================= SEARCH FUNCTION ===================
# =====================================================

def search_case_law(query, top_k=3):

    # ---------------- QUERY EMBEDDING ----------------

    query_embedding = model.encode(
        query,
        convert_to_tensor=True
    )

    # ---------------- COSINE SIMILARITY ----------------

    scores = util.cos_sim(
        query_embedding,
        embeddings
    )[0]

    # ---------------- GET TOP RESULTS ----------------

    top_results = scores.topk(15)

    results = []

    # =================================================
    # ================= LOOP RESULTS ==================
    # =================================================

    for idx in top_results.indices:

        row = df.iloc[int(idx)]

        title = clean_value(
            row.get("title")
        )

        summary = clean_value(
            row.get("summary")
        )

        sections = clean_value(
            row.get("sections")
        )

        verdict = clean_value(
            row.get("verdict")
        )

        source_link = clean_value(
            row.get("source_link")
        )

        # ---------------- SKIP EMPTY ----------------

        if not title and not summary:
            continue

        # ---------------- CLEAN VERDICT ----------------

        if not verdict or len(verdict) < 20:

            verdict = (
                "Detailed verdict unavailable."
            )

        # ---------------- CLEAN SUMMARY ----------------

        if not summary:

            summary = (
                "Case summary unavailable."
            )

        # ---------------- ADD RESULT ----------------

        results.append({

            "title": title,

            "summary": summary[:400],

            "sections": sections,

            "verdict": verdict[:600],

            "source_link": source_link
        })

        # ---------------- LIMIT RESULTS ----------------

        if len(results) >= top_k:
            break

    # =================================================
    # ================= RETURN RESULTS =================
    # =================================================

    return results

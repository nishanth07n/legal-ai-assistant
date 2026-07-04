import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dataset path
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "FIR_DATASET.csv")

# Load dataset
df = pd.read_csv(DATASET_PATH)

# Remove NaN values
df = df.fillna("")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Text column used for embeddings
TEXT_COLUMN = "Description"

# Convert every value safely to string
texts = [str(x) for x in df[TEXT_COLUMN].fillna("").values]

# Generate embeddings
embeddings = model.encode(
    texts,
    convert_to_tensor=True
)


def safe_value(v):
    """
    Safely convert values to string
    """

    if pd.isna(v):
        return ""

    return str(v)


def find_relevant_ipc(query, top_k=3):

    # Convert query to string
    query = str(query)

    # Generate query embedding
    query_embedding = model.encode(
        query,
        convert_to_tensor=True
    )

    # Compute cosine similarity
    scores = util.cos_sim(
        query_embedding,
        embeddings
    )[0]

    # Get top matching results
    top_results = scores.topk(top_k)

    results = []

    for idx in top_results.indices:

        row = df.iloc[int(idx)]

        results.append({
            "offense": safe_value(row.get("Offense")),
            "punishment": safe_value(row.get("Punishment")),
            "cognizable": safe_value(row.get("Cognizable")),
            "bailable": safe_value(row.get("Bailable")),
            "court": safe_value(row.get("Court")),
            "description": safe_value(row.get("Description")),
            "url": safe_value(row.get("URL"))
        })

    return results
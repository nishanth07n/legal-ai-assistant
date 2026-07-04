import json
import os

DATASET_PATH = "datasets/indian_laws"

def load_all_laws():
    all_laws = []
    for file in os.listdir(DATASET_PATH):
        if file.endswith(".json"):
            with open(os.path.join(DATASET_PATH, file), "r", encoding="utf-8") as f:
                all_laws.extend(json.load(f))
    return all_laws

ALL_LAWS = load_all_laws()
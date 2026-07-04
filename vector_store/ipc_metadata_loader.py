import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "ipc_metadata.csv")

ipc_df = pd.read_csv(DATASET_PATH)

ipc_lookup = {}

for _, row in ipc_df.iterrows():
    ipc_lookup[str(row["section"])] = {
        "title": row["title"],
        "punishment": row["punishment"],
        "cognizable": row["cognizable"],
        "bailable": row["bailable"],
        "court": row["court"]
    }


def get_ipc_metadata(section):

    return ipc_lookup.get(str(section), {})
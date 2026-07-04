import os

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
MODEL_DEVICE = "cpu"

# Hide GPU backends from libraries that auto-detect accelerators at import time.
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "0")

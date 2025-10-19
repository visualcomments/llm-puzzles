from __future__ import annotations
import os
from typing import Optional
from kaggle.api.kaggle_api_extended import KaggleApi

def ensure_auth():
    """Authenticate with Kaggle API using env vars or ~/.kaggle/kaggle.json."""
    # KaggleApi reads KAGGLE_USERNAME/KAGGLE_KEY or ~/.kaggle/kaggle.json
    api = KaggleApi()
    api.authenticate()
    return api

def submit_file(api: KaggleApi, competition: str, filepath: str, message: str = "auto-submit") -> dict:
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)
    api.competition_submit(file_name=filepath, message=message, competition=competition)
    # Kaggle API doesn't return a structured object here; we return a stub
    return {"competition": competition, "file": filepath, "message": message}

# v2025‑06‑27‑AI-generated
"""
core/env.py
Loads the project‑root .env file so ordinary `os.getenv(...)`
calls work everywhere.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# locate repo root (folder that contains pyproject.toml)
ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"

# load if it exists; never raise if missing
load_dotenv(ENV_FILE, override=False)

# convenience getter
def require(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env var: {name}")
    return val

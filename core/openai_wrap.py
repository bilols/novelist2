# v2025‑07‑01‑AI-generated
"""
core/openai_wrap.py
Thin wrapper around openai.chat.completions.create that
• logs token usage & cost to logs/cost.csv
• centralises model/price mapping
Usage:
    from core.openai_wrap import chat_completion
    resp = chat_completion(model="gpt-4o-mini", messages=[...])
"""
from __future__ import annotations
import csv, datetime as dt, os, pathlib
import openai

import core.env  # .env loader

PRICE = {
    "gpt-4o-mini": 0.0005,  # USD per 1K tokens (example)
    "gpt-4o": 0.002,
}

LOG_FILE = pathlib.Path("logs/cost.csv")
LOG_FILE.parent.mkdir(exist_ok=True)

def _log(model: str, usage: dict):
    row = {
        "ts": dt.datetime.utcnow().isoformat(timespec="seconds"),
        "model": model,
        **usage,
        "usd": round(usage["total_tokens"] / 1000 * PRICE.get(model, 0.002), 4),
    }
    write_header = not LOG_FILE.exists()
    with LOG_FILE.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=row.keys())
        if write_header:
            w.writeheader()
        w.writerow(row)

def chat_completion(**kwargs):
    model = kwargs.get("model", "gpt-4o-mini")
    resp = openai.chat.completions.create(**kwargs)
    _log(model, resp.usage.model_dump())
    return resp

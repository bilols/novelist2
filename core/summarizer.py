# v2025‑06‑27‑AI-generated
"""
core/summarizer.py
Produces a ≤150‑character summary for continuity prompts.

Two modes:
* FAST   – simple heuristic (first 150 chars, stripped) for offline tests.
* OPENAI – short `chat.completions` call for production.

Switch via env var  SUMMARY_MODE = fast | openai
"""

from __future__ import annotations

import os
import re

import core.env  # loads .env
import openai

MODE = os.getenv("SUMMARY_MODE", "openai").lower()
MAX_CHAR = 150


def _heuristic(text: str) -> str:
    snippet = re.sub(r"\s+", " ", text).strip()
    return snippet[:MAX_CHAR]


def summarize(text: str) -> str:
    if MODE == "fast":
        return _heuristic(text)

    prompt = [
        {
            "role": "system",
            "content": (
                "Summarise the following chapter in no more than "
                f"{MAX_CHAR} characters, plain text:"
            ),
        },
        {"role": "user", "content": text},
    ]
    resp = openai.chat.completions.create(model="gpt-4o-mini", messages=prompt)
    return resp.choices[0].message.content.strip()[:MAX_CHAR]

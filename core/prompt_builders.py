# v2025‑07‑03‑AI-generated
"""
core/prompt_builders.py
• outline_prompt  – returns kwargs for openai.chat.completions.create
• draft_prompt    – returns   messages=[...]  for chapter drafting
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import List

# ---------------------------------------------------------------- outline

_SCHEMA = (Path(__file__).parent.parent / "schemas" / "outline.v1.json").read_text()

def outline_prompt(
    premise: str,
    genre: str | None,
    words: int,
    themes: List[str] | None,
) -> dict:
    sys = (
        "You are a professional story architect.\n"
        "Return ONLY valid JSON that follows the schema below.\n"
        "Each chapter MUST include a non‑empty 'beats' array (≥3 items).\n"
        "If a 'themes' array is provided, echo it unchanged.\n\n"
        f"SCHEMA:\n{_SCHEMA}"
    )
    usr = (
        f"Premise: {premise}\n"
        f"Genre: {genre or 'unspecified'}\n"
        f"Target novel words: {words}\n"
        f"Themes: {', '.join(themes) if themes else 'None'}\n\n"
        "Generate the outline now."
    )
    return {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": sys},
            {"role": "user", "content": usr},
        ],
        "response_format": {"type": "json_object"},
    }

# ---------------------------------------------------------------- draft

def draft_prompt(chapter_spec: dict, prior_summaries: List[str]) -> List[dict]:
    """
    Build chat messages for drafting one chapter.
    chapter_spec: {"num":1,"title":...,"summary":...,"target_words":3000,"beats":[...]}
    prior_summaries: list of ≤150‑char summaries for chapters 1..n‑1
    """
    num = chapter_spec["num"]
    beats = "\n".join(f"- {b}" for b in chapter_spec.get("beats", []))
    sys = (
        "You are a bestselling novelist drafting chapter prose.\n"
        "Write vivid, engaging fiction in Markdown.\n"
        "Honor target word count ±10% and include all beats."
    )
    usr = (
        f"Novel so far (summaries):\n{json.dumps(prior_summaries, indent=2)}\n\n"
        f"Chapter {num} spec:\n"
        f"Title: {chapter_spec['title']}\n"
        f"Target words: {chapter_spec['target_words']}\n"
        f"Beats:\n{beats}\n\n"
        "Draft the full chapter now."
    )
    return [
        {"role": "system", "content": sys},
        {"role": "user", "content": usr},
    ]

# v2025‑06‑27‑AI-generated
"""
core/prompt_builders.py
Helpers to build OpenAI ChatCompletion messages.

Functions:
* outline_prompt(...)
* draft_prompt(...)
"""

from __future__ import annotations
import json
from pathlib import Path

# --------------------------------------------------------- outline

SCHEMA_PATH = Path(__file__).with_suffix("").parent.parent / "schemas" / "outline.v1.json"
_OUTLINE_SCHEMA_STR = SCHEMA_PATH.read_text(encoding="utf-8")


def outline_prompt(premise: str, genre: str | None, words: int) -> dict:
    """Return kwargs for openai.chat.completions.create(...)"""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a seasoned fiction development editor. "
                "Return ONLY valid JSON that exactly matches the schema below. "
                "Do NOT wrap the JSON in markdown or commentary.\n\n"
                f"JSON Schema:\n{_OUTLINE_SCHEMA_STR}"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Premise: {premise}\n"
                f"Genre: {genre or 'unspecified'}\n"
                f"Target total words: {words}\n\n"
                "Generate the outline."
            ),
        },
    ]
    return {
        "model": "gpt-4o-mini",
        "messages": messages,
        "response_format": {"type": "json_object"},
    }


# --------------------------------------------------------- chapter draft

DRAFT_SYS = (
    "You are a professional novelist. Write immersive, publish‑quality prose. "
    "Stay within the requested word count."
)


def draft_prompt(
    chapter_spec: dict,
    prior_summaries: list[str],
) -> list[dict]:
    """
    Build ChatCompletion messages to write one chapter.

    * prior_summaries – list of ≤150‑char strings (oldest → newest).
    """
    context = "\n".join(f"{i+1}. {s}" for i, s in enumerate(prior_summaries))
    beats = "\n".join(f"- {b}" for b in chapter_spec.get("beats", []))
    words = chapter_spec["target_words"]

    user = (
        "Continuity so far (micro‑summaries):\n"
        f"{context or 'N/A'}\n\n"
        f"Write Chapter {chapter_spec['num']}: {chapter_spec['title']}\n"
        f"Target words: {words}\n"
        "Be sure to cover these beats:\n"
        f"{beats or 'N/A'}\n\n"
        "Return ONLY the chapter prose. Do not add commentary or JSON."
    )

    return [
        {"role": "system", "content": DRAFT_SYS},
        {"role": "user", "content": user},
    ]

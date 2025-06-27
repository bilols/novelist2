# v2025‑07‑01‑AI-generated
"""
core/outline.py  – robust outline generator with retries and cost logging
"""
from __future__ import annotations
import json, time
from pathlib import Path
from typing import Any
import jsonschema
import core.env
from core.openai_wrap import chat_completion
from core.prompt_builders import outline_prompt
from core import projects as pj

SCHEMA = json.loads(
    (Path(__file__).parent.parent / "schemas" / "outline.v1.json").read_text()
)
OUTLINE_FILE = "outline.json"
MAX_RETRIES = 3


def _validate(obj: dict[str, Any]) -> None:
    jsonschema.validate(obj, SCHEMA)


def _call_openai(premise: str, genre: str | None, words: int) -> dict | None:
    kwargs = outline_prompt(premise, genre, words)
    resp = chat_completion(**kwargs)
    try:
        return json.loads(resp.choices[0].message.content)
    except json.JSONDecodeError:
        return None


def generate_outline(pid: str, premise: str, genre: str | None, words: int) -> dict:
    root = pj.NOVELIST_ROOT / pid
    attempt = 0
    outline: dict | None = None
    explanation = ""

    while attempt < MAX_RETRIES:
        attempt += 1
        outline = _call_openai(premise, genre, words)
        try:
            _validate(outline)  # type: ignore[arg-type]
            break
        except Exception as e:
            explanation = str(e)
            outline = None
            time.sleep(1)  # brief back‑off

    if outline is None:
        raise RuntimeError(f"Failed to obtain valid outline after {MAX_RETRIES} tries.\n{explanation}")

    (root / OUTLINE_FILE).write_text(json.dumps(outline, indent=2), encoding="utf-8")

    manifest = pj.load_manifest(pid)
    manifest.update({"outline_status": "ready", "target_words": words})
    (root / pj.MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return outline

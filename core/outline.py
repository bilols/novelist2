# v2025‑07‑03‑AI-generated
"""
core/outline.py – outline with themes merge & beats enforcement
"""
from __future__ import annotations
import json, time
from pathlib import Path
from typing import Any
import jsonschema, openai
import core.env
from core.prompt_builders import outline_prompt
from core.openai_wrap import chat_completion
from core import projects as pj

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "outline.v1.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text())
OUTLINE_FILE = "outline.json"

def _validate(obj: dict[str, Any]) -> None:
    jsonschema.validate(obj, SCHEMA)

def generate_outline(pid: str, premise: str, genre: str | None, words: int) -> dict:
    root = pj.NOVELIST_ROOT / pid
    wizard_path = root / "wizard.json"
    wizard_themes = json.loads(wizard_path.read_text())["themes"] if wizard_path.exists() else []

    attempt = 0
    outline: dict[str, Any] | None = None
    while attempt < 3:
        attempt += 1
        try:
            payload = outline_prompt(premise, genre, words, wizard_themes)
            resp = chat_completion(**payload)
            outline = json.loads(resp.choices[0].message.content)
            _validate(outline)
            break
        except (jsonschema.ValidationError, openai.OpenAIError, json.JSONDecodeError):
            time.sleep(1)
            outline = None
    if outline is None:
        raise RuntimeError("Failed to obtain valid outline after 3 attempts.")

    # Ensure themes exist
    if wizard_themes and not outline.get("themes"):
        outline["themes"] = wizard_themes

    (root / OUTLINE_FILE).write_text(json.dumps(outline, indent=2), encoding="utf-8")

    manifest = pj.load_manifest(pid)
    manifest.update({"outline_status": "ready", "target_words": words})
    (root / pj.MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return outline

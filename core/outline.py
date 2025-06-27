# v2025‑06‑27‑AI-generated
"""
core/outline.py
Calls OpenAI with enforced JSON format and retries once if validation fails.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import jsonschema
import openai

import core.env  # .env loader
from core import projects as pj
from core.prompt_builders import outline_prompt

SCHEMA_PATH = Path(__file__).with_suffix("").parent.parent / "schemas" / "outline.v1.json"
OUTLINE_FILE = "outline.json"

with open(SCHEMA_PATH, encoding="utf-8") as fh:
    _OUTLINE_SCHEMA = json.load(fh)


def _validate(data: dict[str, Any]) -> None:
    jsonschema.validate(data, _OUTLINE_SCHEMA)


def _call_openai(kwargs: dict) -> dict:
    resp = openai.chat.completions.create(**kwargs)
    return json.loads(resp.choices[0].message.content)


def generate_outline(pid: str, premise: str, genre: str | None, words: int) -> dict:
    manifest = pj.load_manifest(pid)
    root = pj.NOVELIST_ROOT / pid

    kwargs = outline_prompt(premise, genre, words)

    # first try
    outline = _call_openai(kwargs)
    try:
        _validate(outline)
    except jsonschema.ValidationError:
        # one retry – tell the model exactly what failed
        kwargs["messages"].append(
            {
                "role": "system",
                "content": "Previous JSON failed validation. Please return a corrected object.",
            }
        )
        outline = _call_openai(kwargs)
        _validate(outline)  # will raise if still bad

    # write to disk
    (root / OUTLINE_FILE).write_text(json.dumps(outline, indent=2), encoding="utf-8")

    # update manifest
    manifest["outline_status"] = "ready"
    manifest["target_words"] = words
    (root / pj.MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return outline

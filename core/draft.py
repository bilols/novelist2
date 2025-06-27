# v2025‑06‑30‑AI-generated
"""
core/draft.py
Generate one chapter, summarise, beat‑check, theme‑check.
"""

from __future__ import annotations

import json, os
from pathlib import Path
from typing import Any

import openai

import core.env  # .env loader
from core import projects as pj
from core.prompt_builders import draft_prompt
from core import summarizer as sz
from core import beats as bt

OPENAI_MODEL = os.getenv("CHAPTER_MODEL", "gpt-4o-mini")


# ---------------------------------------------------------------- utilities

def _load_outline(pid: str) -> dict[str, Any]:
    return json.loads((pj.NOVELIST_ROOT / pid / "outline.json").read_text())

def _load_summaries(pid: str, up_to: int) -> list[str]:
    root = pj.NOVELIST_ROOT / pid / "summaries"
    return [
        json.loads((root / f"ch{i:02d}.json").read_text())["summary"]
        for i in range(1, up_to)
        if (root / f"ch{i:02d}.json").exists()
    ]


# ---------------------------------------------------------------- main entry

def generate_chapter(pid: str, chapter_num: int) -> str:
    outline = _load_outline(pid)
    chapter_spec = next(c for c in outline["chapters"] if c["num"] == chapter_num)
    prior_summaries = _load_summaries(pid, chapter_num)

    messages = draft_prompt(chapter_spec, prior_summaries)
    resp = openai.chat.completions.create(model=OPENAI_MODEL, messages=messages)
    prose = resp.choices[0].message.content.strip()

    root = pj.NOVELIST_ROOT / pid
    ch_path = root / "chapters" / f"ch{chapter_num:02d}.md"
    ch_path.write_text(prose, encoding="utf-8")

    # micro‑summary
    summ_path = root / "summaries" / f"ch{chapter_num:02d}.json"
    summ_path.write_text(json.dumps({"summary": sz.summarize(prose)}, indent=2), encoding="utf-8")

    # beat check
    beats = chapter_spec.get("beats", [])
    rep_path = root / "reports" / f"ch{chapter_num:02d}.beats.json"
    rep_path.write_text(json.dumps(bt.verify_beats(prose, beats), indent=2), encoding="utf-8")

    # theme advisor
    try:
        from plugins import theme as th
        th.check_themes(pid, chapter_num, prose)
    except Exception:
        pass  # non‑fatal

    return str(ch_path)

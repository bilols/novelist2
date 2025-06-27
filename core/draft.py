# v2025‑07‑01‑AI-generated
"""
core/draft.py – chapter generator (uses cost logger & theme advisor)
"""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any
from core.openai_wrap import chat_completion
import core.env  # .env loader
from core import projects as pj
from core.prompt_builders import draft_prompt
from core import summarizer as sz, beats as bt

OPENAI_MODEL = os.getenv("CHAPTER_MODEL", "gpt-4o-mini")

def _outline(pid: str) -> dict[str, Any]:
    return json.loads((pj.NOVELIST_ROOT / pid / "outline.json").read_text())

def _priors(pid: str, up_to: int) -> list[str]:
    root = pj.NOVELIST_ROOT / pid / "summaries"
    out = []
    for i in range(1, up_to):
        p = root / f"ch{i:02d}.json"
        if p.exists():
            out.append(json.loads(p.read_text())["summary"])
    return out

def generate_chapter(pid: str, num: int) -> str:
    outline = _outline(pid)
    spec = next(c for c in outline["chapters"] if c["num"] == num)
    messages = draft_prompt(spec, _priors(pid, num))
    resp = chat_completion(model=OPENAI_MODEL, messages=messages)
    prose = resp.choices[0].message.content.strip()

    root = pj.NOVELIST_ROOT / pid
    (root / "chapters").mkdir(exist_ok=True)
    ch_path = root / "chapters" / f"ch{num:02d}.md"
    ch_path.write_text(prose, encoding="utf-8")

    # summary
    (root / "summaries").mkdir(exist_ok=True)
    (root / "summaries" / f"ch{num:02d}.json").write_text(
        json.dumps({"summary": sz.summarize(prose)}, indent=2), encoding="utf-8"
    )

    # beat report
    (root / "reports").mkdir(exist_ok=True)
    beats = spec.get("beats", [])
    (root / "reports" / f"ch{num:02d}.beats.json").write_text(
        json.dumps(bt.verify_beats(prose, beats), indent=2), encoding="utf-8"
    )

    # theme advisor
    try:
        from plugins import theme as th
        th.check_themes(pid, num, prose)
    except Exception:
        pass

    return str(ch_path)

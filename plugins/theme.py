# v2025‑06‑30‑AI-generated
"""
plugins/theme.py
Post‑chapter motif coverage checker.

Usage: imported by core.draft.generate_chapter().
Requires outline.json to contain a top‑level key:
    "themes": ["Hope", "Memory"]
Outputs:
    reports/chNN.theme.json     { "Hope": 3, "Memory": 0 }
    reports/theme_totals.json   accumulated counts
"""

from __future__ import annotations
import json, re
from pathlib import Path
from typing import Dict, List

from core import projects as pj

def _norm(text: str) -> str:
    return re.sub(r"\W+", "", text.lower())

def _score(text: str, themes: List[str]) -> Dict[str, int]:
    norm = _norm(text)
    return {t: norm.count(_norm(t)) for t in themes}

def check_themes(pid: str, chapter_num: int, prose: str) -> None:
    root = pj.NOVELIST_ROOT / pid
    outline = json.loads((root / "outline.json").read_text(encoding="utf-8"))
    themes = outline.get("themes", [])
    if not themes:
        return

    scores = _score(prose, themes)

    # per‑chapter report
    (root / "reports").mkdir(exist_ok=True)
    (root / "reports" / f"ch{chapter_num:02d}.theme.json").write_text(
        json.dumps(scores, indent=2), encoding="utf-8"
    )

    # project aggregate
    agg_path = root / "reports" / "theme_totals.json"
    totals = {t: 0 for t in themes}
    if agg_path.exists():
        totals.update(json.loads(agg_path.read_text()))
    for t, n in scores.items():
        totals[t] = totals.get(t, 0) + n
    agg_path.write_text(json.dumps(totals, indent=2), encoding="utf-8")

def register(core):
    # reserved for future plug‑in registry
    pass

# v2025‑06‑28‑AI-generated
"""
core/bulk_draft.py
Sequentially (re)generates chapters that are missing or flagged
for regeneration. Progress is reported via Celery task.update_state.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core import draft as dr
from core import projects as pj


def _load_outline(pid: str) -> list[dict[str, Any]]:
    root = pj.NOVELIST_ROOT / pid
    with open(root / "outline.json", encoding="utf-8") as fh:
        outline = json.load(fh)
    return outline["chapters"]


def _chapter_done(root: Path, num: int) -> bool:
    return (root / "chapters" / f"ch{num:02d}.md").exists()


def run_bulk(pid: str, chapters: list[int] | None, update_state) -> None:
    """
    * chapters == None  → generate all that are missing
    * chapters == [2,4] → generate exactly 2 & 4 (overwrite)
    update_state – Celery task's self.update_state
    """
    root = pj.NOVELIST_ROOT / pid
    outline = _load_outline(pid)

    wanted = (
        chapters if chapters is not None
        else [c["num"] for c in outline if not _chapter_done(root, c["num"])]
    )
    total = len(wanted)

    for idx, ch_num in enumerate(wanted, start=1):
        update_state(
            state="PROGRESS",
            meta={"current": idx, "total": total, "chapter": ch_num},
        )
        dr.generate_chapter(pid, ch_num)

    # mark manifest
    manifest = pj.load_manifest(pid)
    manifest["draft_status"] = "ready"
    (root / pj.MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")

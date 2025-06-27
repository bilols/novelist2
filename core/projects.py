# v2025‑06‑26‑AI-generated
"""
core/projects.py
Create / load project manifests and ensure on‑disk folder layout.

Project root defaults to  ~/NovelistProjects/<slug>
but can be overridden with the env var  NOVELIST_ROOT.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any

NOVELIST_ROOT = Path(os.getenv("NOVELIST_ROOT", Path.home() / "NovelistProjects"))
MANIFEST = "project.json"


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:50] or "untitled"


class ProjectError(RuntimeError):
    pass


def _ensure_dirs(root: Path) -> None:
    for sub in (
        "chapters",
        "summaries",
        "reports",
        "logs",
        "marketing",
        "drafts",
    ):
        (root / sub).mkdir(parents=True, exist_ok=True)


def create_project(title: str, author: str = "Unknown") -> dict[str, Any]:
    """Initialise a new project folder and manifest."""
    slug = _slugify(title)
    pid = f"{slug}-{uuid.uuid4().hex[:8]}"
    root = NOVELIST_ROOT / pid
    if root.exists():
        raise ProjectError(f"Project directory already exists: {root}")

    _ensure_dirs(root)

    manifest = {
        "id": pid,
        "title": title,
        "author": author,
        "created_at": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "outline_status": "pending",
        "draft_status": "pending",
        "target_words": None,
    }
    with open(root / MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


def load_manifest(pid: str) -> dict[str, Any]:
    root = NOVELIST_ROOT / pid
    mf = root / MANIFEST
    if not mf.exists():
        raise ProjectError(f"Project not found: {pid}")
    with open(mf, encoding="utf-8") as fh:
        return json.load(fh)


def list_projects() -> list[dict[str, Any]]:
    if not NOVELIST_ROOT.exists():
        return []
    out: list[dict[str, Any]] = []
    for mf in NOVELIST_ROOT.glob("*/project.json"):
        try:
            with open(mf, encoding="utf-8") as fh:
                out.append(json.load(fh))
        except json.JSONDecodeError:
            continue
    return sorted(out, key=lambda x: x["created_at"], reverse=True)

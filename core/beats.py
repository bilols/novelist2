# v2025‑06‑27‑AI-generated
"""
core/beats.py
Checks that expected beats are present in the generated chapter.
"""

from __future__ import annotations
import re
from typing import Iterable, Dict, List


def normalise(text: str) -> str:
    return re.sub(r"\W+", "", text.lower())


def verify_beats(chapter_text: str, beats: Iterable[str]) -> Dict[str, List[str]]:
    present, missing = [], []
    norm_chapter = normalise(chapter_text)
    for beat in beats:
        if normalise(beat) in norm_chapter:
            present.append(beat)
        else:
            missing.append(beat)
    return {"present": present, "missing": missing}

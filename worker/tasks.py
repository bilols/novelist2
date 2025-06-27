# v2025‑06‑28‑AI-generated
"""
worker/tasks.py
Demo, outline, single‑chapter, and bulk‑draft tasks.
"""

import time
from core.celery_app import celery_app

# ---------------------------------------------------------------- demo


@celery_app.task(bind=True)
def demo_long_task(self, steps: int) -> str:
    for i in range(steps):
        time.sleep(1)
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": steps})
    return f"Completed {steps} steps"


# ---------------------------------------------------------------- outline

from core import outline as ol  # noqa: E402


@celery_app.task(bind=True)
def generate_outline_task(self, pid: str, premise: str, genre: str | None, words: int):
    self.update_state(state="PROGRESS", meta={"phase": "calling_openai"})
    ol.generate_outline(pid, premise, genre, words)
    return "outline.json"


# ---------------------------------------------------------------- single‑chapter

from core import draft as dr  # noqa: E402


@celery_app.task(bind=True)
def generate_chapter_task(self, pid: str, chapter_num: int):
    self.update_state(state="PROGRESS", meta={"phase": "drafting", "chapter": chapter_num})
    path = dr.generate_chapter(pid, chapter_num)
    return path


# ---------------------------------------------------------------- bulk‑draft

from core import bulk_draft as bd  # noqa: E402


@celery_app.task(bind=True)
def bulk_draft_task(self, pid: str, chapters: list[int] | None = None):
    """
    chapters == None  → generate all missing
    chapters == [2,4] → generate only 2 and 4 (overwriting)
    """
    bd.run_bulk(pid, chapters, self.update_state)
    return "bulk‑draft completed"

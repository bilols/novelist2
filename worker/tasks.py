# v2025‑07‑02‑AI-generated
"""
worker/tasks.py – Celery tasks with retry wrapper.
"""
from core.celery_app import celery_app
from core.retry import retry
import time

# ---------------------------------------------------------------- demo
@celery_app.task(bind=True)
def demo_long_task(self, steps: int) -> str:
    for i in range(steps):
        time.sleep(1)
        self.update_state(state="PROGRESS", meta={"current": i + 1, "total": steps})
    return f"Completed {steps} steps"

# ---------------------------------------------------------------- outline
from core import outline as ol  # noqa: E402

@celery_app.task(bind=True, acks_late=True)
@retry()
def generate_outline_task(self, pid: str, premise: str, genre: str | None, words: int):
    self.update_state(state="PROGRESS", meta={"phase": "calling_openai"})
    ol.generate_outline(pid, premise, genre, words)
    return "outline.json"

# ---------------------------------------------------------------- chapter
from core import draft as dr  # noqa: E402

@celery_app.task(bind=True, acks_late=True)
@retry()
def generate_chapter_task(self, pid: str, chapter_num: int):
    self.update_state(state="PROGRESS", meta={"phase": "drafting", "chapter": chapter_num})
    return dr.generate_chapter(pid, chapter_num)

# ---------------------------------------------------------------- bulk
from core import bulk_draft as bd  # noqa: E402

@celery_app.task(bind=True, acks_late=True)
def bulk_draft_task(self, pid: str, chapters: list[int] | None = None):
    bd.run_bulk(pid, chapters, self.update_state)
    return "bulk‑draft completed"

# v2025‑06‑30‑AI-generated
"""
api/main.py – FastAPI backend v0.6
Adds theme totals endpoint.
"""

from __future__ import annotations

import asyncio, json
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from celery.result import AsyncResult

import core.env
from core.celery_app import celery_app
from core import projects as pj

app = FastAPI(title="Novelist 2.0 API", version="0.6.0")

# ---------- root -----------------------------------------------------------

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index() -> str:
    return "<h1>Novelist 2.0 backend is running ✔</h1>"

# ---------- project CRUD ---------------------------------------------------

@app.get("/projects")
def list_projects():
    return pj.list_projects()

@app.post("/projects")
def create_project(payload: dict):
    title = payload.get("title")
    if not title:
        raise HTTPException(422, detail="title required")
    author = payload.get("author", "Unknown")
    return pj.create_project(title, author)

@app.get("/projects/{pid}")
def get_project(pid: str):
    try:
        return pj.load_manifest(pid)
    except pj.ProjectError as e:
        raise HTTPException(404, detail=str(e)) from None

# ---------- outline --------------------------------------------------------

@app.post("/projects/{pid}/outline")
def gen_outline(pid: str, payload: dict):
    premise = payload.get("premise")
    if not premise:
        raise HTTPException(422, detail="premise required")
    words = int(payload.get("words", 60000))
    genre = payload.get("genre")
    task = celery_app.send_task("worker.tasks.generate_outline_task", args=[pid, premise, genre, words])
    return {"task_id": task.id}

@app.get("/projects/{pid}/outline")
def get_outline(pid: str):
    path = pj.NOVELIST_ROOT / pid / "outline.json"
    if not path.exists():
        raise HTTPException(404, detail="outline not found")
    return json.loads(path.read_text())

# ---------- chapters & validation -----------------------------------------

def _chapter_report(pid: str, num: int) -> Dict:
    root = pj.NOVELIST_ROOT / pid
    exists = (root / "chapters" / f"ch{num:02d}.md").exists()
    rep_file = root / "reports" / f"ch{num:02d}.beats.json"
    report = json.loads(rep_file.read_text()) if rep_file.exists() else None
    return {"num": num, "exists": exists, "report": report}

@app.get("/projects/{pid}/chapters")
def list_chapters(pid: str):
    outline = json.loads((pj.NOVELIST_ROOT / pid / "outline.json").read_text())
    return [_chapter_report(pid, c["num"]) for c in outline["chapters"]]

@app.get("/projects/{pid}/chapters/{num}/report")
def get_chapter_report(pid: str, num: int):
    return _chapter_report(pid, num)

@app.post("/projects/{pid}/chapters/{num}/regenerate")
def regen_chapter(pid: str, num: int):
    task = celery_app.send_task("worker.tasks.generate_chapter_task", args=[pid, num])
    return {"task_id": task.id}

@app.post("/projects/{pid}/chapters/{num}")
def gen_chapter(pid: str, num: int):
    task = celery_app.send_task("worker.tasks.generate_chapter_task", args=[pid, num])
    return {"task_id": task.id}

# ---------- bulk draft -----------------------------------------------------

@app.post("/projects/{pid}/draft")
def bulk_draft(pid: str, payload: dict | None = None):
    chapters = payload.get("chapters") if payload else None
    task = celery_app.send_task("worker.tasks.bulk_draft_task", args=[pid, chapters])
    return {"task_id": task.id}

# ---------- theme totals ---------------------------------------------------

@app.get("/projects/{pid}/themes")
def get_theme_totals(pid: str):
    path = pj.NOVELIST_ROOT / pid / "reports" / "theme_totals.json"
    if not path.exists():
        raise HTTPException(404, detail="theme totals not found")
    return json.loads(path.read_text())

# ---------- task status & websocket ---------------------------------------

@app.get("/tasks/{task_id}")
def task_status(task_id: str):
    res = AsyncResult(task_id, app=celery_app)
    return {"state": res.state, "info": res.info, "ready": res.ready()}

@app.websocket("/ws/{task_id}")
async def ws_task(task_id: str, ws: WebSocket):
    await ws.accept()
    try:
        while True:
            res = AsyncResult(task_id, app=celery_app)
            if res.ready():
                await ws.send_json({"state": res.state, "result": res.result})
                break
            await ws.send_json({"state": res.state, "info": res.info})
            await asyncio.sleep(1)
    finally:
        await ws.close()

# ---------- entry‑point ----------------------------------------------------

def run() -> None:
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run()

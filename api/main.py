# v2025‑07‑01‑AI-generated
"""
api/main.py – FastAPI backend v0.7
Adds wizard route and cost endpoint.
"""
from __future__ import annotations
import asyncio, json, csv, datetime as dt
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from celery.result import AsyncResult
import core.env
from core.celery_app import celery_app
from core import projects as pj

app = FastAPI(title="Novelist 2.0 API", version="0.7.0")

# ---------- helper ---------------------------------------------------------
def _chapter_report(pid: str, n: int):
    root = pj.NOVELIST_ROOT / pid
    exists = (root / "chapters" / f"ch{n:02d}.md").exists()
    beat_file = root / "reports" / f"ch{n:02d}.beats.json"
    report = json.loads(beat_file.read_text()) if beat_file.exists() else None
    return {"num": n, "exists": exists, "report": report}

# ---------- root -----------------------------------------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def idx():
    return "<h1>Novelist 2.0 backend v0.7 is running ✔</h1>"

# ---------- projects -------------------------------------------------------
@app.get("/projects")
def list_projects():
    return pj.list_projects()

@app.post("/projects")
def create_project(payload: dict):
    t = payload.get("title"); a = payload.get("author", "Unknown")
    if not t: raise HTTPException(422, "title required")
    return pj.create_project(t, a)

@app.get("/projects/{pid}")
def get_project(pid: str):
    try: return pj.load_manifest(pid)
    except pj.ProjectError as e: raise HTTPException(404, str(e))

# ---------- wizard ---------------------------------------------------------
@app.post("/wizard")
def launch_wizard(payload: dict):
    """
    Body requires: title, author, premise, themes[], words
    Stores wizard.json then launches outline task.
    """
    required = ["title", "premise", "words"]
    missing = [k for k in required if k not in payload]
    if missing: raise HTTPException(422, f"missing: {', '.join(missing)}")

    man = pj.create_project(payload["title"], payload.get("author", "Unknown"))
    pid = man["id"]
    (pj.NOVELIST_ROOT / pid / "wizard.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    task = celery_app.send_task(
        "worker.tasks.generate_outline_task",
        args=[pid, payload["premise"], payload.get("genre"), int(payload["words"])],
    )
    return {"project_id": pid, "task_id": task.id}

# ---------- outline --------------------------------------------------------
@app.get("/projects/{pid}/outline")
def get_outline(pid: str):
    p = pj.NOVELIST_ROOT / pid / "outline.json"
    if not p.exists(): raise HTTPException(404, "outline not found")
    return json.loads(p.read_text())

# ---------- chapters -------------------------------------------------------
@app.get("/projects/{pid}/chapters")
def list_ch(pid: str):
    outline = get_outline(pid)
    return [_chapter_report(pid, c["num"]) for c in outline["chapters"]]

@app.post("/projects/{pid}/chapters/{n}")
def gen_ch(pid: str, n: int):
    task = celery_app.send_task("worker.tasks.generate_chapter_task", args=[pid, n])
    return {"task_id": task.id}

@app.post("/projects/{pid}/chapters/{n}/regenerate")
def regen_ch(pid: str, n: int):
    return gen_ch(pid, n)

# ---------- costs ----------------------------------------------------------
@app.get("/projects/{pid}/costs")
def cost_totals(pid: str):
    log = Path("logs/cost.csv")
    if not log.exists(): return {"usd": 0, "tokens": 0}
    total_tokens = total_usd = 0.0
    with log.open() as fh:
        rdr = csv.DictReader(fh)
        for row in rdr:
            total_tokens += int(row["total_tokens"])
            total_usd += float(row["usd"])
    return {"usd": round(total_usd, 4), "tokens": int(total_tokens)}

# ---------- bulk draft -----------------------------------------------------
@app.post("/projects/{pid}/draft")
def bulk(pid: str, payload: dict | None = None):
    chapters = payload.get("chapters") if payload else None
    task = celery_app.send_task("worker.tasks.bulk_draft_task", args=[pid, chapters])
    return {"task_id": task.id}

# ---------- themes ---------------------------------------------------------
@app.get("/projects/{pid}/themes")
def theme_tot(pid: str):
    p = pj.NOVELIST_ROOT / pid / "reports" / "theme_totals.json"
    if not p.exists(): raise HTTPException(404, "theme totals not found")
    return json.loads(p.read_text())

# ---------- tasks ----------------------------------------------------------
@app.get("/tasks/{task_id}")
def task_status(task_id: str):
    r = AsyncResult(task_id, app=celery_app)
    return {"state": r.state, "info": r.info, "ready": r.ready()}

@app.websocket("/ws/{task_id}")
async def ws_task(task_id: str, ws: WebSocket):
    await ws.accept()
    try:
        while True:
            r = AsyncResult(task_id, app=celery_app)
            if r.ready():
                await ws.send_json({"state": r.state, "result": r.result})
                break
            await ws.send_json({"state": r.state, "info": r.info})
            await asyncio.sleep(1)
    finally:
        await ws.close()

# ---------- entry ----------------------------------------------------------
def run(): import uvicorn; uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
if __name__ == "__main__": run()

# Novelist 2.0 — Local AI‑Assisted Novel Writing Suite
*Last updated 2025‑06‑28*

```
Root
├─ api/          FastAPI backend (Python 3.12)
├─ core/         Domain logic, prompt builders, validators
├─ worker/       Celery tasks
├─ schemas/      JSON‑Schema files
├─ plugins/      (future) optional modules
├─ frontend/     (future) React UI
└─ .env          ← your private OpenAI key
```

---

## 1  Prerequisites

| Tool | Version | Get it |
|------|---------|--------|
| **Python** | 3.12 x64 | https://python.org |
| **Poetry** | ≥ 2.1 | `pip install poetry` |
| **Node.js** | LTS 20 *(UI later)* | https://nodejs.org |
| **Docker Desktop** | latest | https://www.docker.com/products/docker-desktop |
| **Git** | any | https://git‑scm.com |

Enable **WSL 2** + virtualization in BIOS so Docker can run Redis.

---

## 2  Installation

```bash
git clone <repo-url> Novelist2
cd Novelist2

# install Python deps
poetry install

# run Redis via Docker
docker compose up -d redis

# create .env with your OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env
```

*(`.env` is auto‑loaded by `core/env.py`; do not commit it.)*

---

## 3  Running the stack

### 3.1 Backend API (FastAPI + Uvicorn)

```bash
poetry run novelist-web
# http://localhost:8000/  →  "backend is running ✔"
# http://localhost:8000/docs  → interactive Swagger UI
```

### 3.2 Worker (Celery)

```bash
poetry shell
celery -A core.celery_app.celery_app worker --pool threads --concurrency 8 --loglevel info
```

*(Use `--pool solo` if threads misbehave; or run worker in Docker for full prefork.)*

### 3.3 Validation UI (React + Vite)

```bash
cd frontend
npm i
npm run dev    # http://localhost:5173/

---

## 4  REST API Cheat‑Sheet

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/projects` | `{title, author?}` → create project |
| GET | `/projects` | list projects |
| GET | `/projects/{pid}` | read manifest |
| POST | `/projects/{pid}/outline` | `{premise, words, genre?}` → generate outline |
| GET | `/projects/{pid}/outline` | fetch outline JSON |
| POST | `/projects/{pid}/chapters/{num}` | generate **one** chapter |
| POST | `/projects/{pid}/draft` | `{chapters:[…]}?` → bulk draft (all missing if body empty) |
| GET | `/tasks/{task_id}` | poll Celery task |
| WS | `/ws/{task_id}` | live progress feed |

---

## 5  PowerShell Examples

```powershell
# create project
$p = Invoke-RestMethod -Method Post http://localhost:8000/projects `
     -Body (@{title='My First Novel';author='Bill'}|ConvertTo-Json) `
     -ContentType 'application/json'

# generate outline
$t = Invoke-RestMethod -Method Post `
     -Body (@{premise='A carpenter finds a time‑traveling door';words=50000}|ConvertTo-Json) `
     -ContentType 'application/json' `
     http://localhost:8000/projects/$($p.id)/outline
Invoke-RestMethod http://localhost:8000/tasks/$($t.task_id)

# generate Chapter 1
$t = Invoke-RestMethod -Method Post `
     http://localhost:8000/projects/$($p.id)/chapters/1
Invoke-RestMethod http://localhost:8000/tasks/$($t.task_id)

# bulk draft remaining chapters
$t = Invoke-RestMethod -Method Post `
     http://localhost:8000/projects/$($p.id)/draft
```

---

## 6  Project Folder Layout

```
~/NovelistProjects/<project-id>/
├─ outline.json
├─ chapters/
│   ├─ ch01.md
│   └─ …
├─ summaries/           micro‑summaries (≤150 chars)
│   └─ ch01.json
├─ reports/
│   └─ ch01.beats.json  present / missing beats
├─ logs/
└─ marketing/           (future) cover prompts, blurbs
```

---

## 7  Environment Variables

| Name | Default | Purpose |
|------|---------|---------|
| `OPENAI_API_KEY` | **(required)** | Access to OpenAI API |
| `SUMMARY_MODE` | `openai` | `fast` → heuristic summaries (offline tests) |
| `CHAPTER_MODEL` | `gpt-4o-mini` | override LLM for chapter drafting |
| `BROKER_URL` | `redis://localhost:6379/0` | Celery broker |
| `NOVELIST_ROOT` | `~/NovelistProjects` | project storage root |

Put overrides in `.env`.

---

## 8  Docker‑Compose (Redis + optional Linux worker)

```yaml
version: "3.9"
services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  worker:
    image: python:3.12-slim
    command: >
      bash -c "
        pip install poetry &&
        poetry install &&
        celery -A core.celery_app.celery_app worker --loglevel info"
    volumes: [".:/code"]
    depends_on: [redis]
```

Start with:

```bash
docker compose up -d redis worker
```

---

## 9  Troubleshooting

| Symptom | Fix |
|---------|-----|
| **404 on chapter endpoint** | Ensure API banner shows `version 0.5.0` and `/docs` lists `/chapters/{num}`. |
| **Celery ImportError ('draft_prompt')** | Confirm `core/prompt_builders.py` is latest and both API & worker were restarted. |
| **ValidationError on outline** | Outline prompt now enforces `response_format=json_object`; restart worker if still wrong. |
| **PermissionError WinError 5** | Start worker with `--pool solo` or `threads`, or run worker in Docker. |

---

## 10  Next Planned Features

1. **Validation dashboard** – UI surfacing beat reports & missing items.  
2. **Theme Advisor plug‑in** – motif consistency checks.  
3. **Marketing toolkit** – cover prompts, back‑cover blurb, elevator pitch.  
4. **EPUB/DOCX Exporter** – Pandoc wrapper.  
5. **React front‑end** – drag‑and‑drop builder and live console.

---

*End of README*

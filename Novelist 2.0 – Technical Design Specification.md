# Novelist 2.0 – **Technical Design Specification**

*Revision 1 – 24 Jun 2025*

> **Scope of this document** – A practical, file‑level design you can copy‑paste into an `docs/` folder. It complements the Vision & Scope and is written for local deployment only (OpenAI SDK is the single external dependency). All code the assistant supplies later will be delivered as *whole* files suitable for drop‑in replacement.

```
Root
├─ frontend/            (React 19.1 + Vite)
├─ api/                 (FastAPI 0.115.13)
├─ worker/              (Celery tasks)
├─ core/                (domain logic, prompt builders, validators)
├─ plugins/             (optional extensions)
├─ storage/             ← default project root (configurable)
└─ docs/
```

---

## 1 High‑Level Architecture

```
 ┌────────┐  HTTP/WebSocket   ┌────────────┐    Redis  ┌──────────────┐
 │Frontend│ ────────────────► │  FastAPI   │ ◄────────►│  Celery       │
 └────────┘                   │  API       │           │  Worker Pool  │
    ▲  ▲  ▲                   └────────────┘           └──────────────┘
    │  │  │                         ▲                         ▲
    │  │  └──────── progress WS ────┘                         │
    │  └───────── static assets ──────────────────────────────┘
    │                                        local disk I/O (projects)
    └──────────────────── download / preview files ──────────────────►
```

* **Frontend** – React 19 components, Tailwind CSS, Zustand store, websockets for live task updates.
* **API** – FastAPI synchronous endpoints for CRUD + websocket for job progress; `uvicorn[standard]` runner.
* **Worker** – Celery + Redis; executes all OpenAI calls, validation steps, file generation.
* **Core** – Pure‑python domain layer, *no FastAPI imports*, so workers and unit tests reuse logic.
* **Plugins** – Drop a `*.py` file exposing `register(core)` to extend the system (critique models, theme advisor, etc.).

---

## 2 Subsystem Responsibilities

| Subsystem            | Key Modules         | Responsibilities                                                            |
| -------------------- | ------------------- | --------------------------------------------------------------------------- |
| **project\_manager** | `core/projects.py`  | Create/load projects, issue folder paths, maintain `project.json` manifest. |
| **outline\_engine**  | `core/outline.py`   | Prompt stub creation, multi‑pass chapter seeding, JSON‑schema validation.   |
| **draft\_engine**    | `core/draft.py`     | Adaptive chunking, strict prompt scaffolds, calls to `llm_gateway`.         |
| **summarizer**       | `core/summary.py`   | Summarise chapter → feed into next prompt.                                  |
| **validation**       | `core/validate.py`  | JSON‑schema, grammar (LanguageTool), user nuance rules.                     |
| **theme\_advisor**   | `plugins/theme.py`  | Checks motif coverage, suggests weave‑ins.                                  |
| **marketing**        | `core/marketing.py` | Cover prompt builder, blurbs, pitches.                                      |
| **exporter**         | `core/export.py`    | Markdown merge, Pandoc wrappers to EPUB/DOCX.                               |
| **llm\_gateway**     | `core/llm.py`       | Thin OpenAI wrapper, cost logging (`~/.novelist_costs.csv`).                |

---

## 3 Key Data Models (Pydantic v2)

```python
# core/models.py
class ChapterBeat(BaseModel):
    summary: str
    target_words: int
    sub_plots: list[str] = Field(default_factory=list)

class Chapter(BaseModel):
    num: int = Field(ge=1)
    title: str
    pov: str
    beats: list[ChapterBeat]

class Outline(BaseModel):
    title: str
    author: str
    revision_date: datetime
    premise: str
    genre: str
    novel_target_words: int = Field(ge=1_000)
    chapters: list[Chapter]
    prologue: Chapter | None = None
    epilogue: Chapter | None = None
    # …additional fields omitted
```

Schemas in `schemas/` mirror these definitions and are version‑tagged (e.g. `outline.v1.json`).

---

## 4 API Surface (condensed)

| Method | Path                     | Description                             |
| ------ | ------------------------ | --------------------------------------- |
| `POST` | `/projects`              | create new project                      |
| `GET`  | `/projects/{id}`         | read manifest                           |
| `POST` | `/projects/{id}/outline` | launch outline generation task          |
| `POST` | `/projects/{id}/draft`   | launch draft task (body: chapter range) |
| `POST` | `/projects/{id}/export`  | build manuscript                        |
| `GET`  | `/ws/{id}` (WS)          | push task progress events               |

**Progress event JSON**

```json
{
  "event": "task_update",
  "task_id": "df23a9",
  "status": "in_progress",
  "detail": "Drafting chapter 3 piece 2/6"
}
```

---

## 5 Algorithm Highlights

### 5.1 Adaptive Chunking

```
target_words / piece_length ≈ n_pieces
n_pieces clamped 4…10
while draft_wordcount < min_words:
    request += "Continue…" prompt
```

Completion `max_tokens` =
`min( cap·0.9 , requested , cap − prompt_tokens )` (same logic from prototype).

### 5.2 Continuity Guard

* After each chapter:

  1. Summarise (`≈130 words`).
  2. Persist summary to `summaries/chXX.json`.
  3. Inject last summary + beat checklist into next chapter prompt.

### 5.3 Theme Advisor (plug‑in)

* Runs post‑chapter.
* Simple regex / keyword hit‑map against declared motifs.
* Emits advisory report: `{ "motif": "Memory", "status": "weak", "suggestions": [...] }`.

---

## 6 Storage Layout (per project)

```
my‑novel/
├─ outline.json
├─ style.json
├─ chapters/
│   ├─ ch01.md
│   └─ …
├─ summaries/
│   └─ ch01.summary.json
├─ reports/
│   ├─ ch01.validation.md
│   └─ ch01.theme.json
├─ logs/
│   └─ run_2025‑06‑24T12‑33‑11Z.jsonl
└─ drafts/        (intermediate, may be purged)
```

---

## 7 Error Handling & Logging

* **Per‑run JSONL log** – chronological OpenAI calls (prompt hash, model, p\_tok, c\_tok, cost).
* **Validation errors** – written to `reports/…` and surfaced in UI; block pipeline until resolved.
* **Crash recovery** – tasks are idempotent; status tracked in DB table `runs`. Worker requeues on failure.

---

## 8 Plugin Interface (PEP 420 namespace)

```python
# plugins/theme.py
def register(core):
    core.validation.register_post_step("theme", check_themes)

def check_themes(chapter_text: str, outline: Outline, **ctx) -> Report:
    ...
```

Plugins placed in `plugins/` are auto‑imported at startup (guarded by try/except).

---

## 9 Local Installation & Dev Workflow

1. `git clone …`
2. `python -m venv .venv && . .venv/bin/activate`
3. `pip install -r requirements.txt` (pins FastAPI 0.115+, Pydantic 2.7, Celery 6.x)
4. `docker compose up redis` ← single‑service compose file.
5. `uvicorn api.main:app --reload` (runs API + serves `/frontend` build).
6. `cd frontend && npm i && npm run dev` for hot‑reload during dev.

> *The assistant will cross‑check installation steps against current FastAPI & React docs before producing automated scripts.*

---

## 10 Testing Strategy

* **unit** – pytest; 90 %+ coverage on core logic.
* **schema** – jsonschema test suite (`tests/test_schemas.py`).
* **e2e** – Playwright script: create project → outline → first chapter → export.
* **load** – Locust: simulate 5 concurrent projects on i7/16 GB machine.

---

## 11 File‑Drop Update Policy

* Each change supplied by the assistant will come as **one complete file** (`core/draft.py` etc.) with a header comment `# v<date>-AI‑generated`.
* No patch snippets unless explicitly requested.
* File names and module paths stay stable to keep imports intact.

---

## 12 Open Points

| Item                 | Notes                                             |
| -------------------- | ------------------------------------------------- |
| Authentication       | Local single‑user for now; JWT optional.          |
| Rich‑text editor     | QuillJS vs TipTap – pending decision.             |
| LanguageTool install | Java runtime dependency; document in setup guide. |
| Pandoc binaries      | Provide download links for Windows/macOS/Linux.   |

---

*End of specification.*

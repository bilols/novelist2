# Novelist 2.0 – Vision and Scope Document  
*Revision 1* — 2025‑06‑24

## 1 Purpose
Build a **fully local** web‑based system that helps a human author and an AI language model co‑write publish‑ready novels. The system shepherds the user from blank page to finished manuscript plus basic marketing assets while keeping costs and legal exposure low.

## 2 Goals
* Generate novels that read like professional, human‑written work.
* Emulate an author’s stylistic **hallmarks** without copying protected text.
* Keep the human author in charge by presenting choices at every major step.
* Track cost and token use in real time.
* Offer flexible targets (total words, chapter words, prologue, epilogue).
* Deliver auxiliary assets (cover prompts, blurbs, pitches).

## 3 Core Principles
1. **Human‑in‑the‑loop** – suggestions, not surprises.  
2. **Local‑first** – all artefacts, logs, and assets stay on disk. Only outbound traffic is to the OpenAI API.  
3. **Modular** – outline, drafting, validation, and marketing live in separate services.  
4. **Observability** – every OpenAI call is logged with prompt, response, token counts, and USD cost.  
5. **Scalability** – chunk size, chapter count, and model choice auto‑adjust to hit the user’s targets.  
6. **Extensibility** – plug‑in points for additional models (critique passes, theme advisor) and future services.

## 4 Functional Requirements
| ID | Feature | Description |
|----|---------|-------------|
| F1 | Project Wizard | Guided intake of title, premise, genre, targets, characters, themes. |
| F2 | Style Presets | Library of JSON style guides that describe an author’s voice; user may create or edit presets. |
| F3 | Outline Builder | Multi‑pass generator that fills `<string>` placeholders and validates against JSON Schema. |
| F4 | Draft Engine | Generates chapters in adaptive pieces, maintaining continuity through strict per‑chapter prompts. |
| F5 | Validation Layer | JSON‑schema checks, grammar analysis, custom “nuance” rules, continuity enforcement. |
| F6 | Cost Tracker | Live display + CSV log of prompt/completion tokens and cost per call. |
| F7 | Summarizer | Auto‑summary of each part; summaries fed back into subsequent prompts. |
| F8 | Adaptive Chunking | Splits/merges generation pieces to meet word goals without abrupt cut‑offs. |
| F9 | Theme Advisor | Optional module that suggests motifs and ensures they are woven throughout. |
| F10| Marketing Toolkit | Generates cover‑prompt suggestions, back‑cover blurb, elevator pitch, ad copy. |
| F11| Exporter | Outputs clean Markdown plus optional EPUB/DOCX via Pandoc. |
| F12| Plugin API | Hooks for external critique models or additional validation passes. |

## 5 Non‑Functional Requirements
* **Usability** – browser UI, no command‑line required for core flow.
* **Reliability** – autosave and resumable jobs; no draft loss.
* **Performance** – async task queue keeps UI responsive.
* **Security & Privacy** – only OpenAI SDK traffic; no S3 or third‑party storage.
* **Legal Safety** – style emulation uses descriptive hallmarks only, never copyrighted source text.

## 6 High‑Level Workflow
1. **Create Project** – Wizard gathers metadata and theme ideas.  
2. **Outline Generation** – Outline Builder produces multi‑chapter scaffold.  
3. **User Review** – Author edits or regenerates outline until satisfied.  
4. **Draft Loop** – Draft Engine generates prologue, chapters, epilogue; Validation Layer and Summarizer run after each part.  
5. **User Acceptance** – Author accepts, revises, or regenerates content.  
6. **Export** – Manuscript packaged; Marketing Toolkit produces optional collateral.

## 7 System Architecture
* **Frontend** – React + Vite, bundled as a desktop‑style web app.  
* **Backend API** – FastAPI (Python 3.12) running locally.  
* **Task Queue** – Celery + Redis (Dockerised) for async OpenAI calls.  
* **LLM Gateway** – Thin wrapper around OpenAI SDK that logs usage and cost.  
* **Storage** – local filesystem under `~/NovelistProjects/{project}`.  
* **Validation Service** – Python workers running `jsonschema`, language‑tool grammar checks, nuance validators.  
* **File Renderer** – Markdown → EPUB/DOCX via Pandoc (installed locally).

## 8 Local Installation Overview
1. **Prerequisites**: Python ≥3.12, Poetry, Docker (or Podman) for Redis.  
2. **Clone repo** → `poetry install`.  
3. `docker compose up redis` (bundled compose file).  
4. `poetry run novelist-web` → opens browser at `http://localhost:8000`.  
*(Full, up‑to‑date instructions will be supplied and checked against current docs before release.)*

## 9 Data Model (simplified)
```text
Project
├─ outline.json
├─ style_guide.json
├─ chapters/
│   ├─ ch01.md
│   └─ …
├─ summaries/
│   ├─ ch01.summary.json
│   └─ …
├─ run_log.csv
└─ marketing/
    ├─ cover_prompts.txt
    └─ blurb.txt
```

## 10 Extensibility Roadmap
* **v1.1** – Add external critique pass (e.g. Claude) via optional plugin.  
* **v1.2** – Theme Advisor surfaces motif consistency reports.  
* **v1.3** – “Try another voice” sandbox to experiment with alternative style guides.  
* **v2.0** – Real‑time collaborative editing and comment threads.

## 11 Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| API cost overrun | High | Per‑project spending cap and live tracker. |
| Continuity drift | Medium | Per‑chapter summaries + strict prompt scaffolds (lesson learned). |
| JSON schema drift | Medium | Versioned schemas, migrations on load. |
| Installation friction | Medium | Provide tested Docker compose and scripts; keep docs current. |

## 12 Lessons Applied from Prototype v1
* **Prompt exactness** – Every generation prompt embeds outline beats, last‑chapter summary, and explicit word targets.  
* **Validation early & often** – JSON schema checks at each stage prevent silent drift.  
* **Full‑file drops** – All generated artefacts are saved as whole files; updates replace entire file to avoid patch merge errors.  
* **Local‑first logging** – Costs, logs, and artefacts never leave the host machine.  
* **Theme weaving** – Dedicated Theme Advisor ensures motifs persist.

---

*End of document.*
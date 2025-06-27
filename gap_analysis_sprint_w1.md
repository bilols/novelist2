# Gap Analysis and Sprint W-1 Plan (2025-06-30)

This document captures the current coverage of functional requirements versus the original **novelist_vision_scope_v1.md** specification and defines the next sprint that turns the CLI‑style prototype into a fully interactive wizard‑driven web UI.

All characters are plain ASCII.

---

## 1. Status Matrix

| FR # | Requirement (abridged) | Status (2025‑06‑30) | Missing work |
|------|------------------------|---------------------|--------------|
| FR-1 | Create project / folder scaffold | DONE | -- |
| FR-2 | Flexible word count & auto‑scaling outline | Outline OK; auto-scaling not yet | Implement chapter-length auto‑adjuster |
| FR-3 | Per‑chapter generation with continuity guards | DONE | -- |
| FR-4 | Beat checklist & validation pass | DONE for beats; UI lacks approve/reject | Add approve toggle |
| FR-5 | Theme advisor & motif weaving | MVP done | Semantic matching and weave‑in suggestions |
| FR-6 | Bulk chapter drafting, resumable | DONE | Retry logic per chapter |
| FR-7 | User‑controlled regeneration of any artifact | Partially done (chapters only) | Outline and marketing regeneration endpoints |
| FR-8 | Cost tracking (tokens -> dollars) | Not started | Middleware + UI meter |
| FR-9 | Real‑time progress feedback | Partial (WS endpoint only) | Live console in UI |
| FR-10 | Marketing toolkit (covers, blurbs, pitch) | Not started | Step 9A |
| FR-11 | Exporter to EPUB/DOCX | Not started | Step 9B |
| FR-12 | Style‑guide enforcement & critique passes | Not started | Style validator plugin |
| FR-13 | Plug-in architecture for external models | Foundation proven | Formal registry & docs |
| FR-14 | UI wizard & project dashboard | Partial (validation only) | React wizard, live console |
| FR-15 | Token‑adaptive chunking | Not started | Split/merge logic |

---

## 2. Proposed Backlog (next three sprints)

| Sprint | Focus | Deliverables |
|--------|-------|-------------|
| S-1 | Operational polish | Cost tracker, live WS console, chapter retry |
| S-2 | Creator tools | Marketing toolkit (Step 9A) and outline regeneration |
| S-3 | Publishing | Exporter (Step 9B) and first style-guide validator |

---

## 3. Sprint W-1 ("Wizard foundation") Scope

* Cost logger module `core/openai_wrap.py`, plus `/projects/{pid}/costs` endpoint.
* Wizard API route `/projects/{pid}/wizard` that stores `wizard.json` and triggers outline generation.
* React wizard UI (multi-step form for metadata, author style, themes, model choice, nuance rules, cost preview).
* WebSocket live console component in React.
* Error & success toast notifications.

After W-1 the user can:

1. Launch *Start New Novel* wizard, step through the form, and submit.
2. Watch real-time progress.
3. Land on the existing validation dashboard after the outline is ready.

---

## 4. Next Action

Confirm Sprint W-1 scope or adjust items. Once confirmed, the assistant will supply a single batch of full file drop-in replacements (back end + front end) and updated README instructions.

---

## 5. File-Retention Note

The workspace currently holds all uploads from 26 Jun 2025 onward. Anything older has expired. Re-upload older artifacts if they need to be referenced again.

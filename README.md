# exec-search-ai-workflow

AI workflow system for executive search teams, designed around a real search mandate rather than a chat interface.

This project turns a search process into a structured workflow:

- role intake
- candidate search
- market mapping
- explainable ranking
- brief generation
- approval and export
- audit trail

The goal is not to produce a single prompt response. It is to make candidate research and briefing more structured, reviewable, and repeatable inside a boutique professional services workflow.

## Why I Built It

I built this as a practical internal operating layer for executive search, especially for firms working in regulated, relationship-driven sectors like funds management and financial services.

The project is meant to show how AI can support actual search work:

- turning an unstructured mandate into a reusable project
- reusing an internal candidate pool before jumping to broad sourcing
- making ranking explainable instead of black-box
- generating a client-facing brief with review and approval steps
- preserving version history, export history, and audit visibility

## What The System Does

- **Project-centric workflow**
  Every mandate is tracked as a project with runs, snapshots, brief versions, approvals, and audit history.
- **Role intake and retrieval**
  A raw JD or client brief is parsed into a structured role spec, then grounded with firm and market context via retrieval.
- **Candidate search and review**
  The system searches a demo/internal candidate pool, supports filtering, and surfaces candidate detail for researcher review.
- **Market map view**
  A lightweight market-mapping layer shows which firms appear in the pool and what institutional context is relevant to the mandate.
- **Explainable ranking**
  Candidates receive calibrated fit scores plus structured reasons, evidence, risks, missing information, and dimension-level match logic.
- **Briefing and approval**
  Ranked results can be turned into a markdown brief, submitted for approval, revised, approved, rejected, and exported.
- **Audit and reviewability**
  Key workflow events are stored and exposed through a reviewer console so a team can inspect what happened and when.

## Why It Fits A Firm Like PPP

- It is designed around executive search workflow rather than generic chat.
- It reflects the realities of a lean boutique team: quick review, clear handoffs, and visible process state.
- It treats approval, revision, and audit as first-class product features rather than afterthoughts.
- It is practical to demo, extend, and connect to internal tools over time.

## Demo Surfaces

- **Guided Streamlit UI**
  A 4-step flow for role intake, candidate search, market mapping, and brief creation.
- **Reviewer Console**
  A lightweight internal console for project summary, snapshots, brief versions, approval actions, export artifact viewing, and audit timeline.
- **FastAPI backend**
  Project, search, ranking, brief, audit, and review endpoints.

## Core Stack

- Python, FastAPI, Pydantic
- Anthropic Claude API (`anthropic` SDK) with mock fallback mode
- ChromaDB for retrieval with in-memory fallback
- Streamlit for internal demo and review surfaces

## Quickstart

### Local setup

#### 1) Environment & config

```bash
cp .env.example .env
```

- Set `ANTHROPIC_API_KEY` in `.env` if you want real Claude calls.  
- Leave it empty to run in **mock demo mode** (no cost, still end-to-end).

#### 2) Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3) Seed demo data & ingest documents

```bash
python3 scripts/seed_demo_data.py
python3 scripts/ingest_documents.py
```

Whenever you edit JSON under `data/raw/sample_*`, re-run:

```bash
python3 scripts/ingest_documents.py
```

#### 4) Run API

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Sample requests:

```bash
# Role intake + retrieval
curl -X POST http://127.0.0.1:8000/search/intake \
  -H "Content-Type: application/json" \
  -d '{"raw_input":"Our client is an Australian super fund looking for a Senior Infrastructure Portfolio Manager to oversee core/core-plus mandates, manager selection and portfolio construction across global infrastructure strategies."}'

# End-to-end agentic workflow
curl -X POST http://127.0.0.1:8000/search/run \
  -H "Content-Type: application/json" \
  -d '{"raw_input":"Our client is an Australian super fund looking for a Senior Infrastructure Portfolio Manager to oversee core/core-plus mandates, manager selection and portfolio construction across global infrastructure strategies."}'
```

#### 5) Run Streamlit UI

```bash
streamlit run app/ui/streamlit_app.py
```

The UI is split into 4 guided steps:

1. **Role Intake** – paste a JD or search brief, then parse it into a structured `role_spec` with retrieved context.  
2. **Candidate Search** – fetch demo candidates, view in table + detail card.  
3. **Market Map** – review the current firm distribution and retrieved institutional context.  
4. **Client Brief** – run ranking, generate a markdown brief, and approve before export.

The left sidebar shows a **workflow timeline** (current step + completed steps). Navigation is primarily via the “Next” buttons at the bottom of each page.

## API overview (MVP)

- `POST /search/intake` → parse role + retrieve context
- `POST /search/candidates` → list candidates from demo pool
- `POST /search/rank` → score candidates (explainable)
- `POST /search/run` → run end-to-end agentic workflow (intake + retrieval + ranking + brief + critique)
- `POST /briefs/generate` → generate markdown brief
- `POST /briefs/{brief_id}/submit|approve|reject|request-changes|create-revision|export`
- `GET /briefs/{brief_id}/artifact`
- `GET /projects/{project_id}/review`

## Reviewer demo

### Minimal startup

```bash
python3 scripts/seed_review_demo.py --reset
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
streamlit run app/ui/review_console.py
```

### Reviewer auth context

- Researcher view:
  `x-tenant-id=demo-review-tenant`
  `x-user-role=researcher`
  `x-user-id=demo_researcher`
- Manager view:
  `x-tenant-id=demo-review-tenant`
  `x-user-role=consultant`
  `x-user-id=demo_manager`

The review console exposes these values in the sidebar, so no real third-party credentials are needed.

### Suggested review flow

1. Open `proj_demo_happy` and inspect summary, latest run, snapshot, latest brief, and audit.
2. View exported artifact for the happy-path brief.
3. Open `proj_demo_revision` and create a revision from the `changes_requested` brief.
4. Submit as researcher, then switch to consultant to approve/export.
5. Switch back to researcher and confirm approve/export are disabled or rejected.

## Security / privacy notes (MVP scope)

- Demo data only (no real PII required)
- Designed to support: PII sanitization before logging, audit trails (prompt/model/version, timestamps), and human approval gates for client-facing outputs

## Roadmap (high level)

- LangGraph workflow (planner + critique + retry paths)
- Prompt versioning + prompt caching for stable instruction prefixes
- Audit log + approval workflow
- Evaluation harness (`tests/evals/`) for parse accuracy, retrieval relevance, ranking agreement, hallucination rate
- Adapter-based integrations (CRM/email/doc store)

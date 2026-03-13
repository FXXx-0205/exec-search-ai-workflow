# AI Search Copilot

AI-powered executive search workflow system for candidate research, market mapping, and briefing generation — designed to feel like an internal tool for a boutique executive search firm.

## Why this project

- Decomposes a real executive search workflow into reusable agents/services
- Uses Claude API (Anthropic) + RAG + explainable ranking (rules + narrative)
- Built with regulated professional services in mind (PII minimization, audit-ready outputs)

## MVP features (demo)

- Role intake: raw request → structured `role_spec` JSON
- Internal knowledge retrieval (RAG): ingest demo firm profiles → retrieve relevant context
- Candidate search from demo pool
- Explainable ranking (deterministic scoring + reasons/risks)
- Brief generation (markdown)
- Human approval gate (client-facing export requires approval)
- Streamlit UI to run the whole workflow in minutes

## Tech stack

- Python, FastAPI, Pydantic
- Anthropic Claude API (`anthropic` SDK)
- ChromaDB (optional; auto-fallback to in-memory retrieval if unavailable)
- Streamlit (demo UI)

## Quickstart / 使用说明

### A. Local setup（English）

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

1. **Role Intake** – paste JD, click “解析并检索上下文” to get structured `role_spec` + RAG context.  
2. **Candidate Search** – fetch demo candidates, view in table + detail card.  
3. **Market Map** – see top firms and firm profiles derived from RAG.  
4. **Client Brief** – run ranking, generate markdown brief, approve before export.

The left sidebar shows a **workflow timeline** (current step + completed steps). Navigation is primarily via the “Next” buttons at the bottom of each page.

---

### B. 本地启动与使用（中文）

#### 1）环境与配置

```bash
cp .env.example .env
```

- 如需真实调用 Claude，在 `.env` 里设置 `ANTHROPIC_API_KEY=你的真实 key`。  
- 如果只想 0 成本体验，把这一项留空，系统会自动进入 **mock demo 模式**。

#### 2）安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3）准备 / 更新 demo 数据

```bash
python3 scripts/seed_demo_data.py
python3 scripts/ingest_documents.py
```

当你修改了 `data/raw/sample_candidates/` 或 `data/raw/sample_firm_profiles/` 里的 JSON 时，重新执行：

```bash
python3 scripts/ingest_documents.py
```

#### 4）启动 API 服务

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

常用接口测试：

```bash
# 解析 JD 并检索上下文
curl -X POST http://127.0.0.1:8000/search/intake \
  -H "Content-Type: application/json" \
  -d '{"raw_input":"A mid-sized industry super fund is seeking a Head of Real Assets to lead the strategy and implementation across infrastructure, real estate and private credit."}'

# 一键跑完整 agent 工作流
curl -X POST http://127.0.0.1:8000/search/run \
  -H "Content-Type: application/json" \
  -d '{"raw_input":"A mid-sized industry super fund is seeking a Head of Real Assets to lead the strategy and implementation across infrastructure, real estate and private credit."}'
```

#### 5）启动前端 UI（Streamlit）

```bash
streamlit run app/ui/streamlit_app.py
```

浏览器会打开本地地址（通常是 `http://localhost:8501`），按页面底部按钮依次完成流程：

1. **Role Intake**  
   - 粘贴一段英文 JD 或客户需求；  
   - 点击“解析并检索上下文”，查看结构化 `role_spec` 与检索到的 `firm_*` 公司 profile。
2. **Candidate Search**  
   - 点击“从 demo 候选池检索”；  
   - 在表格中浏览候选人，并从右侧详情卡片中查看 summary / evidence / source URLs。
3. **Market Map**  
   - 查看按候选人数聚合的 Top Firms 柱状图；  
   - 展开每家机构的 RAG 上下文（基金公司 / 咨询机构描述）。
4. **Client Brief**  
   - 选择部分候选人 ID；  
   - 点击“先打分（Ranking）”查看 fit score + reasoning/risks；  
   - 点击“生成 Brief（markdown）”生成 briefing note；  
   - 点击 “Approve（允许对外导出）” 后，再下载 markdown，模拟金融服务场景下的人审 gate。

左侧的 **Workflow 时间线** 会高亮当前步骤，并用 ✅ 标记已完成的步骤，方便 Demo 过程中向面试官解释整个搜索工作流。

## API overview (MVP)

- `POST /search/intake` → parse role + retrieve context
- `POST /search/candidates` → list candidates from demo pool
- `POST /search/rank` → score candidates (explainable)
- `POST /search/run` → run end-to-end agentic workflow (intake + retrieval + ranking + brief + critique)
- `POST /brief/generate` → generate markdown brief
- `POST /brief/approve/{brief_id}` → approve a brief for export
- `GET /brief/{brief_id}/export` → export approved brief (gate enforced)

## Security / privacy notes (MVP scope)

- Demo data only (no real PII required)
- Designed to support: PII sanitization before logging, audit trails (prompt/model/version, timestamps), and human approval gates for client-facing outputs

## Roadmap (high level)

- LangGraph workflow (planner + critique + retry paths)
- Prompt versioning + prompt caching for stable instruction prefixes
- Audit log + approval workflow
- Evaluation harness (`tests/evals/`) for parse accuracy, retrieval relevance, ranking agreement, hallucination rate
- Adapter-based integrations (CRM/email/doc store)


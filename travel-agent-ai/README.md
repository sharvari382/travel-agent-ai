# AI Travel Agent — Wanderly

A single-agent AI travel planner: LangChain agent (OpenAI `gpt-4o-mini`) + tools +
**ChromaDB-backed memory** (exact history + semantic recall), served via FastAPI,
with a travel-themed React + Ant Design chat UI ("Wanderly"). Multi-agent
orchestration, a supervisor, and MCP get layered on top of this same codebase later.

## Project structure

```
travel-agent-ai/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI endpoints
│   │   ├── agent.py           # LangChain agent (OpenAI gpt-4o-mini)
│   │   ├── tools.py           # Tools the agent can call
│   │   ├── memory.py          # ChromaDB-backed history + semantic search
│   │   ├── chroma_client.py   # ChromaDB persistent client + collections
│   │   ├── guardrails.py      # Input/output safety checks
│   │   └── schemas.py         # Pydantic request/response models
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/ChatWindow.tsx   # Travel-themed chat UI ("Wanderly")
│   │   ├── index.css                   # Design tokens, dusk/sunset theme
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
└── docker-compose.yml
```

## Why ChromaDB instead of a SQL database

ChromaDB stores every chat message as a document with metadata (`session_id`, `role`,
`timestamp`). This gives you two things from one store:
- **Exact conversation history** — filter by `session_id`, sort by `timestamp`. Used for
  the context window sent to the LLM each turn.
- **Semantic recall** — `GET /search?q=...` searches across *all* past conversations by
  meaning, not just exact session. e.g. "what did I say about beach destinations."

It's entirely local and file-based (persists to `backend/chroma_data/`) — no external
database server to install or run.

## Run it — VS Code, no Docker (recommended for now)

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # paste your OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```
Open http://localhost:8000/docs to test the API directly.

**Frontend** (new terminal)
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Open http://localhost:5173

## Run it — Docker Compose

```bash
cp backend/.env.example backend/.env   # fill in OPENAI_API_KEY
docker compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

## Feature map

| Feature | Where it lives | Notes |
|---|---|---|
| **LLM** | `backend/app/agent.py` | OpenAI `gpt-4o-mini` via `langchain-openai`. Change `MODEL_NAME` in `.env` to switch models. |
| **Tools** | `backend/app/tools.py` | `get_weather`, `estimate_budget`, `search_attractions`. |
| **Memory** | `backend/app/memory.py`, `chroma_client.py` | ChromaDB, local + persistent. Exact history + semantic search. |
| **Context window** | `memory.py` → `MAX_TURNS_IN_CONTEXT` | Trims history sent to the LLM each turn. |
| **Guardrails** | `backend/app/guardrails.py` | Input/output checks (prompt-injection patterns, off-topic redirect). |
| **UI** | `frontend/src/components/ChatWindow.tsx`, `index.css` | Dusk/sunset theme, time-aware greeting, suggestion chips, boarding-pass styled header. |

## Roadmap

1. **Multiple agents + Supervisor** — split into Destination / Budget / Itinerary agents as LangGraph nodes, supervisor routes between them.
2. **MCP** — register MCP servers as tools in `tools.py`.
3. **n8n** — trigger this agent from a webhook, or fire an n8n workflow off the agent's structured output (email itinerary, calendar event).
4. **Stronger guardrails** — PII redaction, topic classification.

## Notes
- `OPENAI_API_KEY` is required in `backend/.env` — get one from platform.openai.com.
- Weather/attractions tools use placeholder logic unless you also set `OPENWEATHER_API_KEY`.
- ChromaDB data lives in `backend/chroma_data/` — delete that folder to reset all memory.

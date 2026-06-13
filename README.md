# What-If FIFA World Cup 2026 Simulator

An AI-powered scenario simulator for the FIFA World Cup 2026. Ask natural-language
questions ("What if Brazil loses today?") and see the consequences: recomputed
group standings, qualification & title probabilities (Monte Carlo), a projected
knockout route, and an AI-written explanation. It is **not** a score tracker — the
value is understanding tournament consequences.

> Built per the spec in [What-If Simulator.md](./What-If%20Simulator.md). See
> [CLAUDE.md](./CLAUDE.md) for architecture notes.

## Monorepo layout

```
backend/    FastAPI + SQLAlchemy + numpy Monte Carlo engine (Python 3.12)
frontend/   Next.js 15 (App Router, TypeScript, TailwindCSS)
```

## Architecture at a glance

```
NL query ─▶ NLP parser ─▶ Scenario simulator (deterministic)
                               │
                               ▼
                   Standings engine (FIFA tie-breaks)
                               │
              ┌────────────────┼─────────────────┐
              ▼                ▼                  ▼
     Monte Carlo engine   Knockout path      AI explainer
     (qual/title odds)    (projected route)  (Claude, optional)
```

- **Simulation & probability engines are deterministic and LLM-free.** The AI layer
  only writes narrative from numbers the engines already produced.
- **DataProvider abstraction**: ships with an offline `seed` dataset (48 teams, 12
  groups) and a `football-data` provider; falls back to seed if the API has no WC data.
- **AI is optional**: with no `ANTHROPIC_API_KEY`, a deterministic template explainer
  is used, so the whole app runs with zero external keys.

## Quick start (local)

### Backend
```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows;  source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env          # optional — defaults work offline
uvicorn app.main:app --reload # http://localhost:8000  (docs at /docs)
```

Run tests:
```bash
pytest               # all
pytest tests/test_simulation.py::test_probabilities_sum_and_range   # single test
```

### Frontend
```bash
cd frontend
npm install
# point the UI at the backend:
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev                   # http://localhost:3000
```

## Configuration (backend `.env`)

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./fifa.db` | SQLite locally; Postgres URL in prod |
| `DATA_PROVIDER` | `seed` | `seed` or `football-data` |
| `FOOTBALL_DATA_API_KEY` | — | key from football-data.org (optional) |
| `ANTHROPIC_API_KEY` | — | enables Claude explanations (optional) |
| `ANTHROPIC_MODEL` | `claude-haiku-4-5-20251001` | model for explanations |
| `MONTE_CARLO_RUNS` | `20000` | simulations per probability run |
| `CORS_ORIGINS` | `http://localhost:3000` | comma-separated allowed origins |

## API

| Method | Path | Description |
|---|---|---|
| GET | `/teams`, `/teams/{id}`, `/teams/{id}/outlook` | teams + Team Explorer outlook |
| GET | `/groups` | groups with live tables |
| GET | `/matches?group=&status=` | fixtures |
| GET | `/standings`, `/standings/{group}` | computed standings |
| POST | `/simulate` | run a scenario / NL query |
| POST | `/share-card` | render a PNG share card |

## Deployment

Both services deploy to **Railway** (single platform). See
[DEPLOYMENT.md](./DEPLOYMENT.md) for step-by-step instructions.

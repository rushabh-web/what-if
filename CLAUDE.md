# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This App Does

An AI-powered FIFA World Cup 2026 scenario simulator. Users ask natural-language
questions ("What if Brazil loses today?") and the system simulates the tournament
consequences: updated group standings, qualification probabilities, knockout
bracket paths, and an AI-generated explanation. It is **not** a score-tracking
app — the core value is understanding tournament consequences. Original product
spec: `What-If Simulator.md`.

## Repository Layout

```
backend/    FastAPI + SQLAlchemy + numpy Monte Carlo engine (Python 3.12)
frontend/   Next.js 16 (App Router, TypeScript, TailwindCSS v4)
```

> **Git note:** the historical repo root is the user's home directory. This
> project has (or should have) its **own** git repo initialized inside the
> project folder — never `git add` at the home-directory level.

## Commands

### Backend (from `backend/`)
```bash
python -m venv .venv && .venv/Scripts/activate   # Windows path
pip install -r requirements.txt
uvicorn app.main:app --reload                    # http://localhost:8000, docs at /docs
pytest                                           # all tests
pytest tests/test_simulation.py::test_probabilities_sum_and_range   # single test
```
The DB auto-creates and self-seeds on startup (SQLite locally). No migration step.

### Frontend (from `frontend/`)
```bash
npm install
npm run dev      # http://localhost:3000 (reads NEXT_PUBLIC_API_URL from .env.local)
npm run build    # production build (output: standalone, for Docker)
npm run lint
```

### Local toolchain note
Python and Node were installed via winget mid-build. Bash/PowerShell sessions
spawned by the harness may not have them on PATH; prepend:
`$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")`

## Architecture (the big picture)

Request flow for `POST /simulate`, orchestrated by
`backend/app/services/simulation_service.py`:

```
NL query ─▶ nlp/parser.py ─▶ engine/simulator.py (apply hypothetical results)
                                   │
                                   ▼
                       engine/standings.py (FIFA tie-breaks)
                                   │
              ┌────────────────────┼─────────────────────┐
              ▼                    ▼                       ▼
   engine/monte_carlo.py    engine/knockout.py        ai/explainer.py
   (qual/title odds)        (projected route)         (Claude, optional)
```

### Hard rules (from the spec — keep these intact)
- **The simulation & probability engines are deterministic and contain ZERO LLM
  calls.** `ai/` only turns already-computed numbers into prose. Never let the AI
  layer compute standings, probabilities, or rankings.
- **Repository Pattern**: all DB access goes through `repositories/`. Routers stay
  thin — business logic lives in `services/` and `engine/`.
- **DataProvider abstraction** (`providers/`): `get_provider()` returns the
  configured source and **falls back to the offline seed dataset** if the external
  API is unavailable. The app always works with zero external keys.

### Things worth knowing before editing
- **Standings are computed, not stored.** There is intentionally no `standings`
  table; `engine/standings.py` derives tables from match results (single source of
  truth). The `Standing` schema is an API output type only.
- **Monte Carlo is vectorized with numpy** (`engine/monte_carlo.py`), ~0.1s for
  10k runs. The hot loop orders groups by (points, GD, GF, rating) for speed and
  does **not** apply head-to-head; the *displayed* standings (`compute_group_table`)
  use the full FIFA tie-break chain including H2H. Keep that split.
- **Probability results are memoized** by exact match-result signature in
  `services/probabilities.py`. `/simulate` runs Monte Carlo twice (before + after)
  to produce the deltas the UI shows.
- **48-team format**: 12 groups of 4; top 2 + 8 best third-placed advance to a
  Round of 32. Best-third logic lives in both `monte_carlo.py` (probabilistic) and
  `knockout.py` (deterministic projected bracket).
- **Match model is modular** (`engine/poisson.py`, v1 Poisson). v2 Elo / v3 xG can
  replace those functions without touching the engines that call them.
- **AI is optional**: no `ANTHROPIC_API_KEY` → `ai/templates.py` deterministic
  fallback. Model id default `claude-haiku-4-5-20251001`.

### Frontend notes
- **Next.js 16**, not 15. `params`/`searchParams` are async (Promise). Interactive
  pages are Client Components using `useParams()` to avoid awaiting route params.
  See `frontend/AGENTS.md` and `node_modules/next/dist/docs/` before using new APIs.
- Tailwind v4 (CSS-first config via `@theme` in `globals.css`; no tailwind.config).
- API access is centralized in `src/lib/api.ts` (+ types in `src/lib/types.ts`).
  `NEXT_PUBLIC_API_URL` is baked at build time.

## Config (backend `.env`, see `.env.example`)

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./fifa.db` | Postgres URL in prod (auto-rewritten to `+psycopg`) |
| `DATA_PROVIDER` | `seed` | `seed` or `football-data` |
| `FOOTBALL_DATA_API_KEY` | — | football-data.org key (optional) |
| `ANTHROPIC_API_KEY` | — | enables Claude explanations (optional) |
| `MONTE_CARLO_RUNS` | `20000` | simulations per run |
| `CORS_ORIGINS` | `http://localhost:3000` | comma-separated allowed origins |

## Deployment
Both services target **Railway** (single platform) with managed PostgreSQL. Each
has a `Dockerfile` + `railway.json`. Step-by-step: `DEPLOYMENT.md`.

## Scope Boundaries
In scope: groups, fixtures, standings, scenario simulation, qualification
probability, knockout paths, AI explanations, share cards. Out of scope: betting,
fantasy, streaming, UGC, social features, real-money transactions.

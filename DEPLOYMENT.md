# Deployment Guide — Railway (single platform)

Both the FastAPI backend and the Next.js frontend deploy as **two services in one
Railway project**, with a managed PostgreSQL database. Free/low-cost.

## Prerequisites

1. A [Railway](https://railway.app) account (sign in with GitHub).
2. This repo pushed to GitHub.
3. (Optional) An [Anthropic API key](https://console.anthropic.com) for real AI
   explanations. Without it, the deterministic template explainer is used.
4. (Optional) A [football-data.org](https://www.football-data.org/client/register)
   key. Without it (or if WC2026 data isn't published yet), the offline seed
   dataset is used automatically.

## 1. Create the project + database

1. Railway → **New Project** → **Deploy from GitHub repo** → select this repo.
2. In the project, **New → Database → PostgreSQL**. Railway sets `DATABASE_URL`.

## 2. Backend service

1. **New → GitHub Repo** (same repo). Set **Root Directory** to `backend`.
   Railway detects the `Dockerfile`.
2. **Variables**:
   - `DATABASE_URL` → reference the Postgres plugin: `${{Postgres.DATABASE_URL}}`
     (Railway gives `postgresql://...`; the app rewrites it to the `psycopg`
     driver automatically — see note below).
   - `MONTE_CARLO_RUNS=20000`
   - `CORS_ORIGINS` → your frontend URL (fill in after step 3, e.g.
     `https://frontend-production-xxxx.up.railway.app`)
   - `ANTHROPIC_API_KEY` → *(optional)*
   - `FOOTBALL_DATA_API_KEY` + `DATA_PROVIDER=football-data` → *(optional)*
3. **Settings → Networking → Generate Domain**. Note the backend URL.

> **psycopg driver note:** Railway's `DATABASE_URL` starts with `postgresql://`.
> SQLAlchemy + psycopg3 wants `postgresql+psycopg://`. The app normalises this at
> startup (see `app/config.py` `normalized_database_url`), so you can paste the
> Railway value as-is.

## 3. Frontend service

1. **New → GitHub Repo** (same repo). Set **Root Directory** to `frontend`.
   Railway detects Next.js (Nixpacks).
2. **Variables**:
   - `NEXT_PUBLIC_API_URL` → the backend URL from step 2.3.
3. **Settings → Networking → Generate Domain**. This is your app URL.
4. Go back to the **backend** service and set `CORS_ORIGINS` to this frontend URL,
   then redeploy the backend.

## 4. Verify

- Visit `https://<backend>/health` → `{"status":"ok"}`.
- Visit `https://<backend>/docs` → interactive API.
- Open the frontend URL, ask "What if Brazil loses today?".

## Alternative: Render

The backend `Dockerfile` and `/health` endpoint work as-is on Render (Web Service,
Docker). Create a Render PostgreSQL instance, set the same variables, and deploy the
frontend as a separate Render Static/Node service with `NEXT_PUBLIC_API_URL` set.

## CLI deploy (optional)

```bash
npm i -g @railway/cli
railway login
railway link        # select the project
railway up          # from backend/ or frontend/ to deploy that service
```

# FIFA World Cup 2026 What-If Simulator

## Product Overview

Build an AI-powered FIFA World Cup 2026 scenario simulator.

Users can ask questions such as:

- What if Brazil loses today?
- Can Argentina still qualify?
- What happens if England draws?
- Who will Brazil face if they finish second?
- Show easiest path to the final.
- Show hardest path to the final.

The system should simulate tournament outcomes in real time using actual World Cup fixtures, standings, and tournament structure.

The product should focus on:

1.  Scenario simulation
2.  Qualification probability calculations
3.  Knockout path generation
4.  AI-generated explanations
5.  Shareable visual cards

This is NOT a score-tracking app.

The core value is helping users understand tournament consequences.

------------------------------------------------------------------------

# Product Goals

Users should be able to:

- Explore hypothetical match outcomes
- Understand qualification chances
- Visualize knockout brackets
- Compare multiple scenarios
- Generate social media share cards

The application should feel like:

"Playoff Machine for FIFA World Cup"

------------------------------------------------------------------------

# MVP Features

## Feature 1

Natural Language Queries

Examples:

"What if Brazil loses today?"

"What if England wins both matches?"

"Can Morocco still qualify?"

AI should parse user intent into simulation inputs.

------------------------------------------------------------------------

## Feature 2

Scenario Simulator

Allow users to modify match results.

Example:

Brazil vs Morocco

Current:\
Not Played

User:\
Brazil loses 0-1

System:

Recalculate:

- Group standings
- Goal difference
- Qualification status
- Knockout bracket

------------------------------------------------------------------------

## Feature 3

Qualification Probabilities

Show:

Current Probability

After Scenario Probability

Example:

Brazil

Before:\
92%

After:\
61%

------------------------------------------------------------------------

## Feature 4

Knockout Path Generator

Generate projected knockout route.

Example:

Round of 32:\
Germany

Round of 16:\
France

Quarter Final:\
Argentina

------------------------------------------------------------------------

## Feature 5

AI Explanation

Generate concise explanations.

Example:

"Brazil would remain in contention, but a loss significantly increases the risk of elimination."

------------------------------------------------------------------------

# Engineering Philosophy

Prioritize:

1.  Simplicity
2.  Correctness
3.  Fast iteration
4.  Free-tier deployment
5.  Maintainability

Avoid premature optimization.

Do not introduce infrastructure complexity unless clearly justified.

Prefer the simplest solution that satisfies requirements.

Claude may simplify architecture where appropriate.

------------------------------------------------------------------------

# MVP Scope

Must Support:

- Teams
- Groups
- Fixtures
- Standings
- Scenario Simulation
- Qualification Probability Estimation
- Knockout Path Generation
- AI Explanations

Should NOT Include:

- Betting
- Fantasy Football
- Streaming
- User-generated content
- Social network features
- Real-money transactions

------------------------------------------------------------------------

# Suggested Technical Architecture

Claude may modify architecture if a simpler or better solution exists.

## Frontend

Preferred:

- Next.js 15
- TypeScript
- TailwindCSS
- shadcn/ui

Requirements:

- Mobile-first
- Responsive
- SEO-friendly
- Server Components where beneficial

------------------------------------------------------------------------

## Backend

Preferred:

- Python
- FastAPI
- Pydantic
- SQLAlchemy

Requirements:

- REST APIs
- Strong typing
- Clear service separation

------------------------------------------------------------------------

## Database

Preferred:

PostgreSQL

Recommended Free Provider:

- Neon PostgreSQL

Alternative:

- Supabase PostgreSQL

Claude may choose either.

------------------------------------------------------------------------

## Caching

Initial Recommendation:

No Redis.

Use:

- in-memory caching
- cachetools
- functools.lru_cache

Only introduce Redis if actual performance bottlenecks exist.

If Redis becomes necessary:

Preferred:

- Upstash Redis

------------------------------------------------------------------------

## Background Jobs

Initial Recommendation:

Use APScheduler.

Avoid:

- Celery
- RabbitMQ
- Kafka

unless genuinely required.

If application scale justifies it:

Claude may introduce:

- Celery
- RQ

with proper reasoning.

------------------------------------------------------------------------

## Deployment

Frontend:

Preferred:

Vercel Free Tier

Backend:

Preferred:

Render Free Tier

Alternatives:

- Railway
- Fly.io

Database:

- Neon
- Supabase

Cache:

- Upstash (only if needed)

Goal:

Keep monthly infrastructure cost at or near zero during MVP.

------------------------------------------------------------------------

# Data Sources

Priority Order

1.  WorldCup2026 Open API

If unavailable:

2.  Football-Data.org

If unavailable:

3.  API-Football

System should support switching providers.

Create abstraction layer:

DataProvider

Methods:

get_teams()

get_matches()

get_standings()

get_group_table()

------------------------------------------------------------------------

# Database Schema

## Teams

team_id

name

fifa_code

group_name

flag_url

------------------------------------------------------------------------

## Matches

match_id

home_team_id

away_team_id

group_name

match_date

status

home_goals

away_goals

------------------------------------------------------------------------

## Standings

team_id

group_name

played

wins

draws

losses

gf

ga

gd

points

------------------------------------------------------------------------

## Simulations

simulation_id

user_input

simulation_result

created_at

------------------------------------------------------------------------

# FIFA Group Ranking Rules

Sort by:

1.  Points
2.  Goal Difference
3.  Goals Scored
4.  Head-to-Head
5.  Fair Play
6.  Draw of Lots

Implementation must support tie-break rules.

------------------------------------------------------------------------

# Simulation Engine

Core responsibility:

Take current tournament state.

Apply hypothetical outcomes.

Recompute standings.

Return:

- updated tables
- qualification status
- knockout mapping

Engine must be deterministic.

No LLM involved.

------------------------------------------------------------------------

# Probability Engine

Use Monte Carlo Simulation.

Run:

10000 simulations minimum.

Preferred:

100000 simulations.

For each simulation:

1.  Simulate remaining matches.
2.  Generate standings.
3.  Record qualification.
4.  Record bracket progression.

Output:

qualification_probability

group_win_probability

round_of_16_probability

quarter_final_probability

semi_final_probability

final_probability

championship_probability

------------------------------------------------------------------------

# Match Simulation Model

Version 1

Simple Poisson Distribution

Inputs:

team_attack_strength

team_defense_strength

Expected Goals

Output:

scoreline

Version 2

Use Elo Ratings.

Version 3

Use SPI or xG models.

Keep architecture modular.

------------------------------------------------------------------------

# AI Layer

Provider:

OpenAI

Model:

GPT-5.5

Responsibilities:

Only explanation generation.

Never calculate standings.

Never calculate probabilities.

Never calculate rankings.

Prompt Inputs:

Current Standings

Scenario

Probability Changes

Knockout Path

Output:

100-200 word explanation.

------------------------------------------------------------------------

# API Design

POST /simulate

Input

{\
"scenario": \[\
{\
"match_id": 123,\
"home_goals": 0,\
"away_goals": 1\
}\
\]\
}

Output

{\
"updated_standings": \[\],\
"qualification_probabilities": \[\],\
"knockout_path": \[\],\
"ai_summary": ""\
}

------------------------------------------------------------------------

GET /groups

GET /matches

GET /standings

GET /teams

POST /simulate

POST /share-card

------------------------------------------------------------------------

# Frontend Pages

## Home

Ask any World Cup scenario.

Input box:

"What if Brazil loses today?"

------------------------------------------------------------------------

## Scenario Results

Show:

Updated standings

Probability changes

Knockout route

AI explanation

------------------------------------------------------------------------

## Team Explorer

Team page.

Show:

Qualification odds

Remaining matches

Potential opponents

------------------------------------------------------------------------

## Group Explorer

Show:

Live standings

Qualification scenarios

------------------------------------------------------------------------

# UI Requirements

Mobile-first.

Dark mode.

Football-focused visuals.

Avoid dashboard clutter.

Use:

- Flags
- Brackets
- Progress bars
- Sankey-style paths

------------------------------------------------------------------------

# Share Cards

Generate image:

WHAT IF

Brazil loses today

Qualification:\
92% → 61%

Most Likely Opponent:\
Germany

Optimized for:

Twitter/X

Instagram

WhatsApp

------------------------------------------------------------------------

# Performance Targets

API Response:

\<500ms

Simulation:

\<3s

Monte Carlo:

\<10s

Cache expensive calculations.

------------------------------------------------------------------------

# Coding Standards

Strict TypeScript.

Python type hints mandatory.

100% API schema validation.

Use Pydantic.

Use SQLAlchemy.

Use Repository Pattern.

No business logic in controllers.

Simulation engine isolated.

------------------------------------------------------------------------

# Future Features

## Path Finder

Show easiest route to final.

------------------------------------------------------------------------

## Scenario Comparison

Compare:

Scenario A

vs

Scenario B

------------------------------------------------------------------------

## AI Debate Mode

"Should Brazil intentionally rest players?"

Generate multiple perspectives.

------------------------------------------------------------------------

## Notification System

Alert users when probabilities change significantly.

------------------------------------------------------------------------

# Success Metrics

Average Session Length

Scenario Queries Per User

Share Rate

Return Rate

Probability Calculation Accuracy

Latency

------------------------------------------------------------------------

# Non Goals

No fantasy football.

No betting.

No gambling.

No live video.

No streaming.

No player card marketplace.

Focus entirely on tournament scenario intelligence.

# VirtualFit AI

An AI virtual trial room and smart fashion shopping application: upload a
photo, pick clothing, get an AI-generated visualization plus an estimated
size and style suggestions — with clear, honest limitations at every step.

> **Status:** Phase 1 (planning) complete. See [`docs/`](docs/) for the
> full product requirements, architecture, database design, API design,
> security/privacy plan, tech stack rationale, and phased roadmap before
> any code is written.

## Why this exists

Online shoppers can't tell how clothing will look or fit before buying.
VirtualFit AI separates that problem into three honest, independently
useful pieces instead of one overconfident "AI knows best" black box:

1. **Visual try-on** — an AI-generated approximation of how a garment may
   look on you.
2. **Size recommendation** — a measurement-based estimate against the
   product's actual size chart, with a confidence level and an
   explanation.
3. **Style recommendation** — outfit/color suggestions based on
   preferences you provide, never assumptions about you.

## Documentation

| Doc | Contents |
|---|---|
| [`docs/01-product-requirements.md`](docs/01-product-requirements.md) | Problem, MVP scope, product-honesty rules |
| [`docs/02-user-flows.md`](docs/02-user-flows.md) | Main flow, guest boundary, async try-on sequence |
| [`docs/03-architecture.md`](docs/03-architecture.md) | System/frontend/backend/AI-provider architecture |
| [`docs/04-database-design.md`](docs/04-database-design.md) | ERD + schema rationale |
| [`docs/05-api-design.md`](docs/05-api-design.md) | REST endpoint reference and conventions |
| [`docs/06-security-and-privacy.md`](docs/06-security-and-privacy.md) | Privacy commitments and technical controls |
| [`docs/07-tech-stack.md`](docs/07-tech-stack.md) | Stack choices and why |
| [`docs/08-roadmap.md`](docs/08-roadmap.md) | Phased build plan and MVP cut line |

## Tech stack

React + TypeScript + Vite + Tailwind (frontend) · FastAPI + PostgreSQL +
SQLAlchemy + Alembic (backend) · a swappable AI provider interface behind
`VirtualTryOnService`. Full rationale in
[`docs/07-tech-stack.md`](docs/07-tech-stack.md).

## Project structure

```
frontend/     React + TypeScript SPA
backend/      FastAPI application
docs/         Planning & architecture documentation
tests/        Cross-cutting/e2e tests
```

`frontend/` and `backend/` are currently empty — they're built out
starting in Phase 2.

## Important limitations (always shown to users in-app)

- AI try-on is a visualization, not a guarantee of fit.
- Size recommendations are estimates based on the information provided
  and the product's size chart; actual fit varies by fabric, garment
  construction, and brand.
- AI-generated images may contain visual errors.

## License

TBD.

# Development Roadmap

This mirrors Section 48 of the spec. Each phase ends with a **checkpoint —
we don't move to the next phase until you've confirmed the current one
works.**

| Phase | Deliverable |
|---|---|
| 1 | Planning (this doc set) — **current phase** |
| 2 | Frontend foundation: Vite + React + TS + Tailwind + routing + layout/nav |
| 3 | Core UI: Landing, Login, Register, Dashboard, Trial Room shell |
| 4 | Backend foundation: FastAPI + PostgreSQL + SQLAlchemy + Alembic + auth |
| 5 | User profile: profile, measurements, style preferences endpoints + UI |
| 6 | Clothing system: catalog, categories, size charts (seeded sample data) |
| 7 | AI integration: `VirtualTryOnService`, mock provider, async job flow end-to-end |
| 8 | Size Advisor: size recommendation engine + UI |
| 9 | Style Advisor: color/outfit recommendations + UI |
| 10 | Comparison: multiple try-ons, side-by-side, favorites |
| 11 | Wardrobe: digital wardrobe + outfit builder |
| 12 | Security audit pass against `06-security-and-privacy.md` |
| 13 | Testing: backend unit/integration tests, frontend component tests |
| 14 | Deployment prep: prod env config, hosting choices, Docker prod compose |
| 15 | Future features (design-only): video try-on, AR, merchant dashboard, brand integration, subscriptions |

## MVP cut line

Phases 1–9 plus the security items relevant to what's built so far are
the MVP (Section 52's checklist). Phases 10–15 are real, valuable, but
not blocking a usable v1.

## Working agreement for each phase (Section 49)

For every phase, before writing code, you'll get:
1. What we're building and why.
2. The exact folder/file structure for that phase.
3. Complete code for only the files that phase needs.
4. Plain-language explanation of the important parts.
5. Exact terminal commands + which directory to run them in.
6. What you should see when it works.
7. Troubleshooting notes.
8. A short testing checklist.

Then we stop and wait for you to confirm it works before moving on —
no 50-file drops, no skipping ahead.

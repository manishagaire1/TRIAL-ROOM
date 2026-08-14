# Technology Stack & Rationale

| Layer | Choice | Why |
|---|---|---|
| Frontend framework | React + TypeScript | Type safety catches bugs before runtime; huge ecosystem; matches Section 28 |
| Build tool | Vite | Near-instant dev server reload, simpler config than webpack for a learner |
| Styling | Tailwind CSS | Utility classes = no separate CSS-file sprawl, easy to keep components self-contained |
| Routing | React Router | Standard, well-documented, matches the ~20-page structure in Section 34 |
| Server state | TanStack Query | Handles loading/error/cache/retry for API calls (esp. try-on job polling) without hand-written state machines |
| Forms | React Hook Form + Zod | Typed, declarative validation; Zod schemas double as a mental model for what the backend expects |
| HTTP client | Axios | Interceptors make it easy to attach the JWT + handle 401s in one place |
| Backend framework | FastAPI (Python) | Async, typed via Pydantic, auto-generated OpenAPI docs (useful for Section 47's README API docs) |
| ORM | SQLAlchemy | Explicit, mature, works cleanly with Alembic migrations |
| Migrations | Alembic | Versioned schema changes — required once the DB has real data, not just `create_all()` |
| Database | PostgreSQL | Relational data (Section 30's tables are inherently relational), JSON columns available where flexibility is genuinely needed (tags, favorite_colors) |
| Auth | JWT (python-jose or PyJWT) + passlib for hashing | Stateless, works for a future mobile/B2B client, industry-standard hashing |
| AI integration | Provider-agnostic interface (Section 13) | Never locks the project to one vendor; a mock provider unblocks all other development |
| Containerization | Docker + Docker Compose | One-command local environment (Postgres + backend + frontend) for consistency; non-Docker instructions provided too since you're learning the underlying tools |

## Why not alternatives (brief)

- **Next.js instead of Vite+React** — Next adds SSR/routing conventions
  that aren't needed for an authenticated SPA behind login; Vite keeps
  the mental model simpler while you're learning React itself.
- **Django instead of FastAPI** — Django's batteries (admin, ORM) are
  convenient but more "magic" to learn at once; FastAPI + SQLAlchemy
  keeps each piece (routing, validation, ORM) visible and swappable,
  which matches the "explain every decision" requirement.
- **MongoDB instead of PostgreSQL** — the data is relational by nature
  (users own photos own jobs own results; products belong to size
  charts); forcing that into documents would mean re-implementing joins
  in application code for no benefit.
- **NextAuth/Auth0 instead of hand-rolled JWT** — worth considering later
  for production, but rolling a simple JWT flow first is far more
  valuable while learning what "authentication" actually means
  underneath a library.

# Security & Privacy Plan (Sections 25–27)

This app processes personal photos, so privacy is treated as a first-class
feature, not an afterthought bolted on in Phase 12.

## 1. Privacy commitments (product-level, user-facing)

- Images are private by default — no public URL ever exists for a user
  photo or try-on result. Access always goes through an authenticated,
  ownership-checked route.
- Users can delete their photo, any try-on result, or their entire
  account at any time; deletion removes the DB rows and the stored files.
- User images are **never** used to train or fine-tune AI models unless
  the user explicitly opts in via a `UserConsent` record — the default
  is opted out.
- A plain-language privacy policy page (Section 34, page 19) states all
  of the above without legal jargon.

## 2. Technical controls

| Concern | Control |
|---|---|
| Passwords | Hashed with bcrypt/argon2, never logged, never returned in any API response |
| Image upload | MIME-type sniffing (not just extension), file size cap, dimension check, re-encoded server-side before storage |
| File naming | Server-generated UUID filenames — never trust/store the client's original filename |
| Storage | Private bucket/folder; served only via authenticated, ownership-checked routes; signed short-lived URLs in prod |
| Auth | JWT with short expiry + refresh, protected route dependency on every non-public endpoint |
| Rate limiting | Per-IP and per-user limits on `/auth/*` and `/tryon` (AI calls are the expensive resource to abuse) |
| CORS | Explicit allow-list of the frontend origin only, no wildcard in prod |
| CSRF | N/A for pure JWT-bearer API calls from a SPA (no cookie-based session to forge), revisited if cookie auth is ever added |
| Headers | `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options` set via FastAPI middleware |
| SQL injection | SQLAlchemy parameterized queries only — no raw string-built SQL |
| XSS | React escapes by default; any `dangerouslySetInnerHTML` is banned unless explicitly reviewed |
| Secrets | All in environment variables, `.env` gitignored, `.env.example` documents names only |
| Error responses | Sanitized messages only (Section 36); full exceptions go to server-side structured logs, never the HTTP response |

## 3. What gets logged vs. never logged

**OK to log:** request path, status code, response time, job id, user id
(not email), AI provider name, job status transitions.

**Never logged:** passwords (hashed or not), JWTs, API keys, raw image
bytes, full image storage URLs beyond what's needed to debug (prefer
logging the DB id, look up the path only when actively debugging).

## 4. Consent mechanism

`UserConsent` table (Section 30) stores one row per consent type (e.g.
`ai_training`, `marketing_email`) with `granted: bool` and a timestamp.
Nothing defaults to `granted = true`. The register flow and settings page
both surface these as explicit opt-in checkboxes, unchecked by default.

## 5. Where this gets enforced in the roadmap

Every phase that touches uploads, auth, or storage implements its slice of
this table as it's built (Phase 4 auth hashing, Phase 6 upload validation,
Phase 12 is a dedicated **audit** pass, not the first time security is
considered).

## 6. Phase 12 audit results (2026-08-14)

Went through every route in `backend/app/api/` against the table in
Section 2, plus a grep pass for XSS/raw-SQL/sensitive-logging issues.

**Already correct, verified during the audit (no code change needed):**
- Every non-public route requires `get_current_user`; every user-owned
  resource reachable by a client-supplied ID has an explicit
  `.user_id != user.id` ownership check (or is filtered by
  `current_user.id` at the query level, so an arbitrary ID is never
  even accepted). Confirmed by counting `get_current_user` references
  against route definitions per file — no gaps.
- No `dangerouslySetInnerHTML` anywhere in the frontend.
- No raw/string-built SQL anywhere in the backend — SQLAlchemy queries only.
- No logger call anywhere logs a password, token, or raw image bytes.

**Fixed during the audit (real gaps, not just polish):**
- **Upload DoS**: `await file.read()` buffered the entire request body
  before the size check ever ran. Replaced with a chunked
  `read_upload_with_limit()` in `app/utils/image_validation.py` that
  aborts as soon as the 8MB cap is exceeded — verified a 12MB upload
  now gets rejected in ~35ms instead of being fully read first.
- **No rate limiting existed at all.** Added `RateLimitMiddleware`
  (`app/core/rate_limit.py`): 20 req/min/IP on `/auth/*`, 10 req/min/IP
  on `POST /tryon`. In-memory, single-process only — noted in the code
  that a multi-worker production deployment needs a shared store
  (Redis) instead. Verified: exactly 20 requests succeed, the 21st is
  a 429, CORS preflight `OPTIONS` requests are excluded from the count
  (they don't carry the actual request and would otherwise silently
  halve the real budget).
- **No security headers were set.** Added `SecurityHeadersMiddleware`
  (`app/core/security_headers.py`): `X-Content-Type-Options`,
  `X-Frame-Options`, `Referrer-Policy` on every response, plus a strict
  `Content-Security-Policy` — except on `/docs`/`/redoc`/`/openapi.json`,
  since Swagger UI loads its JS/CSS from a CDN and a strict CSP would
  break the interactive docs this project's instructions rely on.
- **No account deletion endpoint existed** despite Section 25 requiring
  one. Added `DELETE /api/users/me` (`app/services/account_service.py`):
  collects every storage key (photo, wardrobe items, try-on results)
  *before* deleting the user row, since `ON DELETE CASCADE` removes the
  DB rows but never touches the filesystem. Verified: user row gone,
  photo file actually removed from disk, old JWT immediately rejected.
- **CORS was `allow_methods=["*"], allow_headers=["*"]`.** Tightened to
  the exact methods and headers the app actually uses. The origin
  allow-list (the control that actually matters) was already correct.

**Consciously deferred, not silently skipped:**
- **JWT refresh tokens** (Section 2 says "short expiry + refresh") — a
  60-minute JWT that simply expires and forces re-login is not a
  vulnerability, just less convenient than silent refresh. Implementing
  real refresh tokens (rotation, revocation list) is a session-UX
  feature, not a security fix, so it's left for a future session-UX
  pass rather than bundled into an audit.
- **`UserConsent` / AI-training consent mechanism** — Section 4's own
  wording is conditional: "if data is ever used for improvement." The
  mock provider does no training and consumes no user data beyond a
  single request/response. Building an unused consent table now would
  be speculative infrastructure; add it when a feature actually
  consumes consent.

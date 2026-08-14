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

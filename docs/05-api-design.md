# API Design (Section 31)

All routes are prefixed `/api`. All request/response bodies are JSON.
Authenticated routes expect `Authorization: Bearer <jwt>`.

## Auth
| Method | Route | Notes |
|---|---|---|
| POST | `/auth/register` | email + password, sends verification email |
| POST | `/auth/login` | returns JWT |
| POST | `/auth/logout` | invalidates session |
| POST | `/auth/forgot-password` | sends reset link |
| POST | `/auth/reset-password` | consumes reset token |
| GET | `/auth/verify-email` | consumes verification token |
| POST | `/auth/guest` | issues a short-lived guest session token |

## User & profile
| Method | Route | Notes |
|---|---|---|
| GET | `/users/me` | current user + profile summary |
| PUT | `/users/profile` | update `UserProfile` |
| POST | `/users/photo` | upload/replace `UserPhoto` (multipart) |
| DELETE | `/users/photo` | delete current photo |
| GET | `/body-measurements` | fetch current `BodyMeasurement` |
| POST \| PUT | `/body-measurements` | create/update (Quick or Accurate mode fields) |
| GET \| PUT | `/style-preferences` | color/style/occasion preferences |

## Catalog
| Method | Route | Notes |
|---|---|---|
| GET | `/clothes` | paginated, filterable by category/color/brand |
| GET | `/clothes/{id}` | full product detail incl. size chart |
| POST | `/clothes` | admin/brand-only, create product |

## Try-on
| Method | Route | Notes |
|---|---|---|
| POST | `/tryon` | body: `user_photo_id, clothing_id, size, color` → `202 { job_id }` |
| GET | `/tryon/{id}` | job status + result when ready |
| GET | `/tryon/history` | paginated, authenticated only |
| DELETE | `/tryon/{id}` | deletes job + result + stored image |

## Recommendations
| Method | Route | Notes |
|---|---|---|
| POST | `/size-recommendation` | body: measurements/usual size + clothing_id + fit pref → recommendation |
| POST | `/style-recommendation` | body: clothing_id(s) + occasion → suggested items |

## Outfits
| Method | Route | Notes |
|---|---|---|
| POST | `/outfits` | create `SavedOutfit` + `OutfitItem`s |
| GET | `/outfits` | list saved outfits |
| POST | `/outfits/compare` | body: outfit ids → side-by-side comparison payload |
| DELETE | `/outfits/{id}` | |

## Wardrobe & shopping list
| Method | Route | Notes |
|---|---|---|
| GET \| POST | `/wardrobe` | list / add `WardrobeItem` |
| DELETE | `/wardrobe/{id}` | |
| GET \| POST | `/shopping-list` | list / add |
| DELETE | `/shopping-list/{id}` | |

## Design conventions

- **Every response has a consistent envelope for errors**:
  `{ "error": { "code": "IMAGE_TOO_LARGE", "message": "..." } }` — the
  `message` is always the plain-language, user-safe string from Section
  36; raw exceptions/stack traces never reach this field.
- **Pagination** uses `?page=&page_size=` with a response shape
  `{ items: [...], total, page, page_size }` everywhere it applies
  (catalog, history, outfits) — one convention, not one per endpoint.
- **`POST /tryon` is fire-and-forget** (202 + job id), never a blocking
  call that waits for the AI provider — this is the API-level contract
  that makes Section 32's async flow possible.
- **Ownership is enforced in a shared dependency** (`get_current_user`
  + a `require_owner(resource)` check), used by every route that reads
  or deletes a user-owned resource (photos, jobs, outfits, wardrobe,
  shopping list) — written once in `core/`, not reimplemented per route.
- **Admin routes** (`POST /clothes`, future user/brand management) sit
  under the same `/api` prefix but require `current_user.is_admin`,
  checked by a separate dependency — never a separate unauthenticated
  path (Section 41).

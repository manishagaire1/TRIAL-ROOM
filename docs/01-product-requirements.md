# VirtualFit AI — Product Requirements Document

> Project codename: **VirtualFit AI** (easy to rename later — appears only in
> `README.md`, the frontend `<title>`, and a `PROJECT_NAME` env var, never
> scattered through logic).

## 1. Problem

Online shoppers can't tell how clothing will actually look or fit on their
own body before buying. This causes:
- High return rates for online fashion retailers.
- Shopper hesitation / abandoned carts.
- No easy way to compare outfits or get a second opinion before purchase.

## 2. Solution

A web application where a user uploads a photo (or optional body
measurements), picks clothing from a catalog, and gets:
1. **A visual approximation** of how the garment may look on them (AI
   try-on image).
2. **A size estimate** based on measurements + the product's own size chart
   (not a guess from the AI image).
3. **Style/outfit suggestions** based on stated preferences, not inferred
   personal traits.

These three outputs are kept **architecturally separate** (Section 2 of the
master spec). A try-on image is never used as evidence for a size
recommendation, and vice versa — they use different inputs and different
services. This matters because conflating them would let a bad AI image
silently produce a bad size recommendation.

## 3. Non-goals for MVP (explicitly deferred)

- Real-time video / AR try-on (Phase 15).
- Payments / subscriptions.
- AI-estimated body measurements from photos (needs a computer-vision
  model; stubbed as a future service interface only).
- Multi-tenant brand/merchant dashboards (schema supports it later via
  `brand_id`, but no admin UI for brands yet).

## 4. MVP scope (must-have, Section 52 of spec)

| Area | Included in MVP |
|---|---|
| Auth | Register, login, logout, JWT sessions, guest mode |
| Photo | Upload or camera capture, replace/delete |
| Profile | Height, weight, optional detailed measurements, usual size, fit preference |
| Catalog | Browse clothing, view product detail, size chart |
| Try-on | Submit job → async processing → result image |
| Size | Recommended size + alternative + confidence + explanation |
| Style | Basic color/occasion-based outfit suggestions |
| History | Save results, view trial history, delete |
| Security | Hashed passwords, private image storage, input validation |

## 5. Explicit product-honesty rules (do not violate in any phase)

These are hard constraints, not suggestions — they shape the API contracts
in Section 5 of `05-api-design.md`:

1. Every try-on result screen must display: *"AI visualization is an
   approximation, not a guarantee of fit."*
2. Every size recommendation response must include an `explanation` field
   and a `confidence` field, and the frontend must always render the
   disclaimer sentence from Section 11 of the master spec.
3. Style/outfit explanations must be phrased as preference-matches
   ("may be a stronger match for..."), never as objective/physical claims
   about the user's body or appearance.
4. No feature may claim to know or infer sensitive personal attributes
   (e.g. skin tone → clothing rules). Recommendations are driven only by
   data the user explicitly provided (favorite colors, occasion, style).

## 6. Target users (who the schema must support later, not who we build UI for now)

- **Shoppers** — full MVP experience.
- **Fashion stores** (future) — `Clothing.brand_id`, `merchant_id`,
  `product_url`, `affiliate_url` fields exist from day one so this doesn't
  require a schema migration later, even though there's no store-facing UI
  yet.
- **Brands** (future) — same reasoning, via `SizeChart` being reusable
  across products instead of duplicated per product.

## 7. Success criteria for MVP

- A new user can go from landing page → photo upload → try-on result →
  size recommendation → saved outfit in under 5 minutes, with zero
  required fields beyond photo + height + weight.
- No plaintext secrets anywhere in the repo (verified in Phase 12 audit).
- Every AI call is behind a `VirtualTryOnService` interface — swapping the
  provider must never require touching frontend code or route handlers.

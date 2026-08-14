# Database Design (Section 30)

## 1. Entity-relationship diagram

```mermaid
erDiagram
    USER ||--o| USER_PROFILE : has
    USER ||--o| BODY_MEASUREMENT : has
    USER ||--o| STYLE_PREFERENCE : has
    USER ||--o{ USER_PHOTO : uploads
    USER ||--o{ TRY_ON_JOB : requests
    USER ||--o{ SAVED_OUTFIT : saves
    USER ||--o{ WARDROBE_ITEM : owns
    USER ||--o{ SHOPPING_LIST : keeps
    USER ||--o{ USER_CONSENT : gives
    USER ||--o{ NOTIFICATION : receives

    CLOTHING ||--o{ CLOTHING_IMAGE : has
    CLOTHING }o--|| SIZE_CHART : "uses (by brand+category)"
    SIZE_CHART ||--o{ CLOTHING_SIZE : "defines rows for"

    USER_PHOTO ||--o{ TRY_ON_JOB : "used in"
    CLOTHING ||--o{ TRY_ON_JOB : "tried on in"
    TRY_ON_JOB ||--o| TRY_ON_RESULT : produces

    SAVED_OUTFIT ||--o{ OUTFIT_ITEM : contains
    CLOTHING ||--o{ OUTFIT_ITEM : "referenced by"
    WARDROBE_ITEM ||--o{ OUTFIT_ITEM : "referenced by"

    USER ||--o{ RECOMMENDATION : "generated for"
    TRY_ON_JOB ||--o| RECOMMENDATION : "optionally linked to"

    USER {
        uuid id PK
        string email UK
        string password_hash
        bool email_verified
        bool is_admin
        bool is_guest
        datetime created_at
    }
    USER_PROFILE {
        uuid id PK
        uuid user_id FK
        string name
        string age_range
        string gender_preference
        string country_region
        string measurement_system
        datetime updated_at
    }
    BODY_MEASUREMENT {
        uuid id PK
        uuid user_id FK
        float height_cm
        float weight_kg
        float chest_cm
        float waist_cm
        float hip_cm
        float shoulder_cm
        float inseam_cm
        float arm_length_cm
        float leg_length_cm
        float foot_size
        string usual_shirt_size
        string usual_pants_size
        string usual_dress_size
        string fit_preference
        string body_shape
        bool ai_estimated
        datetime updated_at
    }
    STYLE_PREFERENCE {
        uuid id PK
        uuid user_id FK
        json favorite_colors
        string color_group
        json styles
        json occasions
        datetime updated_at
    }
    USER_PHOTO {
        uuid id PK
        uuid user_id FK
        string storage_path
        string status
        datetime created_at
    }
    CLOTHING {
        uuid id PK
        uuid brand_id FK
        string name
        string category
        text description
        string primary_color
        json available_colors
        json available_sizes
        string material
        decimal price
        string currency
        string product_url
        string affiliate_url
        uuid size_chart_id FK
        string fit_type
        json tags
        datetime created_at
    }
    CLOTHING_IMAGE {
        uuid id PK
        uuid clothing_id FK
        string storage_path
        int sort_order
    }
    SIZE_CHART {
        uuid id PK
        uuid brand_id FK
        string category
        string name
    }
    CLOTHING_SIZE {
        uuid id PK
        uuid size_chart_id FK
        string size_label
        float chest_cm
        float waist_cm
        float hip_cm
        float length_cm
        int stock_qty
    }
    TRY_ON_JOB {
        uuid id PK
        uuid user_id FK
        uuid user_photo_id FK
        uuid clothing_id FK
        string selected_size
        string selected_color
        string status
        string ai_provider
        string failure_reason
        datetime created_at
        datetime completed_at
    }
    TRY_ON_RESULT {
        uuid id PK
        uuid try_on_job_id FK
        string result_image_path
        json metadata
        datetime created_at
    }
    SAVED_OUTFIT {
        uuid id PK
        uuid user_id FK
        string name
        string occasion
        datetime created_at
    }
    OUTFIT_ITEM {
        uuid id PK
        uuid saved_outfit_id FK
        uuid clothing_id FK
        uuid wardrobe_item_id FK
        string slot
    }
    RECOMMENDATION {
        uuid id PK
        uuid user_id FK
        uuid try_on_job_id FK
        string type
        json input_snapshot
        json output
        float confidence
        datetime created_at
    }
    WARDROBE_ITEM {
        uuid id PK
        uuid user_id FK
        string category
        string color
        string image_path
        string label
        datetime created_at
    }
    SHOPPING_LIST {
        uuid id PK
        uuid user_id FK
        uuid clothing_id FK
        string selected_size
        string note
        datetime created_at
    }
    USER_CONSENT {
        uuid id PK
        uuid user_id FK
        string consent_type
        bool granted
        datetime granted_at
    }
    NOTIFICATION {
        uuid id PK
        uuid user_id FK
        string type
        string message
        bool read
        datetime created_at
    }
```

## 2. Key design decisions

- **`UserProfile`, `BodyMeasurement`, `StylePreference` are 1-to-1 with
  `User`**, not repeating-history tables. If we ever want measurement
  history, that's an additive migration (add a `version`/`is_current`
  column) rather than a rethink — no need to over-engineer this now.
- **`SizeChart` is decoupled from `Clothing`** (many products share one
  chart per brand+category) instead of copy-pasting chest/waist/hip
  numbers onto every product row. `ClothingSize` rows are the actual
  per-size measurements belonging to a chart. This directly implements
  Section 10's "do not depend only on S/M/L/XL" — `ClothingSize.size_label`
  can be any string, and the numeric columns are what the size engine
  actually compares against.
- **`TryOnJob` and `TryOnResult` are separate** so the async flow
  (Section 32) has somewhere to live: a job can exist in `pending` /
  `processing` / `failed` state with no result row yet. One job → at most
  one result; regenerating creates a new job, preserving history instead
  of overwriting.
- **`Recommendation` is a generic table** for both size and style
  recommendations (`type` discriminates), storing the exact input
  snapshot and output — this makes "explain why you recommended this"
  (Section 11/17) auditable later instead of recomputed guesswork.
- **`OutfitItem.clothing_id` and `wardrobe_item_id` are both nullable
  FKs**, exactly one set — an outfit slot can point at a catalog product
  or a user's own wardrobe photo. Enforced at the application layer
  (service-level check), not a DB constraint, to keep the schema simple
  for a beginner to read.
- **No password column stores plaintext** — `password_hash` only, hashed
  with a strong algorithm (bcrypt/argon2) chosen in Phase 4.
- **`is_guest` on `User`** lets a guest session reuse the same table
  (with no email/password) rather than a parallel guest-data model,
  which would double the number of code paths for very little benefit.

## 3. What's intentionally NOT modeled yet

- Payments/subscriptions (Section 42) — no `Subscription`/`Plan` tables
  yet; added when Phase 15 business-model work starts.
- Brand/merchant admin accounts — `brand_id` exists on `Clothing` and
  `SizeChart` as a plain UUID FK placeholder; a full `Brand` table with
  its own auth comes with the B2B phase.

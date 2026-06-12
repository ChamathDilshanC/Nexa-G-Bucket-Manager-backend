# Nexa-G-Bucket Manager Backend

Backend service for CloudBucket built with FastAPI. It validates authenticated requests, integrates with Supabase Storage, and generates signed URLs for secure direct file transfer between mobile clients and Supabase.

**Production URL:** [https://nexa-g-bucket-manager-backend.vercel.app](https://nexa-g-bucket-manager-backend.vercel.app)

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- Supabase JWT validation
- Supabase Google OAuth
- Supabase Storage SDK
- Vercel

## Core Responsibilities

- Google login and sign-up through Supabase OAuth
- Validate Supabase JWT from mobile or web client
- Authorize bucket/file operations per authenticated user
- One user can create and manage multiple owned buckets
- Bucket CRUD (create, list, update settings, delete)
- List files and handle file delete operations
- Generate signed upload/download URLs
- Handle controlled delete operations with policy checks

## Suggested Folder Structure

```text
backend/
├─ app/
│  ├─ main.py
│  ├─ core/
│  ├─ api/
│  │  └─ routes/
│  │     ├─ auth.py
│  │     ├─ health.py
│  │     ├─ buckets.py
│  │     ├─ files.py
│  │     └─ signed_urls.py
│  ├─ db/
│  │  └─ migrations/
│  ├─ services/
│  ├─ schemas/
│  └─ tests/
├─ .env.example
├─ requirements.txt
├─ vercel.json
└─ Dockerfile
```

## Supabase Setup

### 1. Run the user bucket migration

Open the Supabase SQL Editor and run:

`app/db/migrations/001_user_buckets.sql`

### 2. Enable Google Auth

1. Go to Supabase Dashboard → Authentication → Providers
2. Enable Google
3. Add your Google OAuth client id and secret

### 3. Redirect URLs

Supabase → Authentication → URL Configuration:

| Field | Value |
|-------|-------|
| Site URL | `https://nexa-g-bucket-manager-backend.vercel.app` |
| Redirect URLs | `https://nexa-g-bucket-manager-backend.vercel.app/auth/callback` |
| Redirect URLs (local dev) | `http://127.0.0.1:8000/auth/callback` |

GCP Authorized redirect URI (unchanged):

`https://qdmwlxvbcpdsuykhxrja.supabase.co/auth/v1/callback`

## Environment Variables

### Vercel Production

Set these in Vercel → Project → Settings → Environment Variables:

```bash
APP_ENV=production
APP_PORT=8000
APP_CORS_ORIGINS=*

SUPABASE_URL=https://qdmwlxvbcpdsuykhxrja.supabase.co
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SUPABASE_DEFAULT_BUCKET=nexa-files
GOOGLE_OAUTH_REDIRECT_URL=https://nexa-g-bucket-manager-backend.vercel.app/auth/callback

SIGNED_URL_EXPIRY_SECONDS=900
MAX_UPLOAD_SIZE_MB=50
ALLOWED_MIME_TYPES=image/jpeg,image/png,application/pdf
```

### Local Development

Create `.env` from `.env.example`. For local OAuth testing, override:

```bash
GOOGLE_OAUTH_REDIRECT_URL=http://127.0.0.1:8000/auth/callback
```

`SUPABASE_SERVICE_ROLE_KEY` is required for server-side bucket and file management. Keep it secret and never expose it to clients.

## Local Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Production API

Base URL:

`https://nexa-g-bucket-manager-backend.vercel.app`

Useful links:

- API root: [https://nexa-g-bucket-manager-backend.vercel.app/](https://nexa-g-bucket-manager-backend.vercel.app/)
- Swagger docs: [https://nexa-g-bucket-manager-backend.vercel.app/docs](https://nexa-g-bucket-manager-backend.vercel.app/docs)
- System info: [https://nexa-g-bucket-manager-backend.vercel.app/info](https://nexa-g-bucket-manager-backend.vercel.app/info)
- Google login: [https://nexa-g-bucket-manager-backend.vercel.app/auth/google](https://nexa-g-bucket-manager-backend.vercel.app/auth/google)

## API Targets

- `GET /` — API welcome and endpoint links
- `GET /health`
- `GET /info` — Supabase connection, bucket list, default bucket, and runtime settings
- `GET /auth/google` — Start Google login or sign-up
- `GET /auth/callback?code=...` — Exchange OAuth code for JWT session
- `POST /auth/callback` — Exchange OAuth code from mobile/web clients
- `GET /auth/me` — Current authenticated user profile
- `POST /buckets` — Create another bucket for the logged-in user
- `GET /buckets` — List only the current user's buckets
- `PATCH /buckets/{bucket}`
- `DELETE /buckets/{bucket}`
- `GET /buckets/{bucket}/files`
- `POST /files/upload-url`
- `POST /files/download-url`
- `DELETE /buckets/{bucket}/files/{path}`

## Google Login Flow

1. Client calls `GET https://nexa-g-bucket-manager-backend.vercel.app/auth/google`
2. Open the returned `url` in a browser or WebView
3. User signs in with Google. Supabase creates the account on first login
4. Supabase redirects to `https://nexa-g-bucket-manager-backend.vercel.app/auth/callback?code=...`
5. Backend returns `access_token` and `refresh_token`
6. Send `Authorization: Bearer <access_token>` on all protected routes

## User Bucket Rules

- Each authenticated user only sees and manages their own buckets
- One user can create multiple buckets
- API bucket `name` is the friendly display name, for example `photos`
- Supabase storage bucket id is auto-generated, for example `ua1b2c3d4e5-photos`
- Use the storage bucket id returned by `GET /buckets` for file and signed URL routes

## Upload Flow (Supabase)

1. Client requests `POST /files/upload-url` with bucket, path, and content type.
2. Backend returns `url`, `token`, and `expires_in`.
3. Client uploads the file to the signed URL using the returned token.

## Milestones

1. JWT verification and auth dependencies
2. Google OAuth and `/auth/me`
3. Per-user bucket registry and access control
4. Supabase Storage service abstraction
5. Bucket CRUD and file routes
6. Signed URL issuance
7. Validation, logging, and test coverage

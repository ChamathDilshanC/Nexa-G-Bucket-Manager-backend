# Nexa-G-Bucket Manager Backend

Backend service for CloudBucket built with FastAPI. It validates authenticated requests, integrates with Google Cloud Storage, and generates presigned URLs for secure direct file transfer between mobile clients and GCP.

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic
- Supabase JWT validation
- Google Cloud Storage SDK

## Core Responsibilities

- Validate Supabase JWT from mobile client
- Authorize bucket/file operations per user context
- List buckets and files
- Generate presigned upload/download URLs
- Handle controlled delete operations

## Suggested Folder Structure

```text
backend/
├─ app/
│  ├─ main.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ security.py
│  │  └─ logging.py
│  ├─ api/
│  │  ├─ deps.py
│  │  └─ routes/
│  │     ├─ health.py
│  │     ├─ buckets.py
│  │     ├─ files.py
│  │     └─ signed_urls.py
│  ├─ services/
│  │  ├─ gcp_storage.py
│  │  └─ supabase_client.py
│  ├─ schemas/
│  └─ tests/
├─ .env.example
├─ requirements.txt
├─ vercel.json
└─ Dockerfile
```

## Environment Variables

Create `.env` from `.env.example`:

```bash
APP_ENV=development
APP_PORT=8000
SUPABASE_URL=your_supabase_project_url
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
GCP_PROJECT_ID=your_gcp_project_id
GCP_DEFAULT_BUCKET=optional_default_bucket_name
GCP_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
SIGNED_URL_EXPIRY_SECONDS=900
MAX_UPLOAD_SIZE_MB=50
ALLOWED_MIME_TYPES=image/jpeg,image/png,application/pdf
```

## Local Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## API Targets

- `GET /health`
- `GET /buckets`
- `GET /buckets/{bucket}/files`
- `POST /files/upload-url`
- `POST /files/download-url`
- `DELETE /buckets/{bucket}/files/{path}`

## Milestones

1. JWT verification and auth dependencies
2. GCS service abstraction
3. Bucket and file routes
4. Signed URL issuance
5. Validation, logging, and test coverage

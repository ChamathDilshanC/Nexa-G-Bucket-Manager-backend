# CloudBucket API (Backend)

Backend service for the **GCP Mobile File Manager (CloudBucket)** platform, built with **FastAPI** and integrated with **Supabase Auth** and **Google Cloud Storage**.

## Overview

This service handles authentication verification, authorization checks, bucket/file metadata APIs, and signed URL generation for secure direct file transfer between mobile clients and GCP.

The backend is designed to be deployable on **Vercel** (serverless) or a **VPS/container runtime**.

## Core Responsibilities

- Verify Supabase JWTs for every protected endpoint.
- Resolve user access permissions to target buckets.
- List buckets and files from Google Cloud Storage.
- Generate presigned upload/download URLs.
- Validate upload constraints (MIME types, size, expiry).
- Perform secure delete operations with audit-friendly logs.

## Suggested Tech Stack

- FastAPI
- Uvicorn
- Pydantic Settings
- google-cloud-storage
- Supabase/PyJWT auth verification helpers
- Pytest for API tests

## Suggested Folder Structure

```text
Nexa-G-Bucket-Manager-backend/
├─ app/
│  ├─ main.py                         # FastAPI app entrypoint
│  ├─ core/
│  │  ├─ config.py                    # Settings/env loading
│  │  ├─ security.py                  # JWT verification/auth guards
│  │  └─ logging.py
│  ├─ api/
│  │  ├─ deps.py                      # Shared dependencies
│  │  └─ routes/
│  │     ├─ health.py
│  │     ├─ buckets.py
│  │     ├─ files.py
│  │     └─ signed_urls.py
│  ├─ schemas/                        # Request/response models
│  ├─ services/
│  │  ├─ gcp_storage.py               # GCS operations
│  │  ├─ supabase_auth.py             # Supabase token validation
│  │  └─ permission_service.py        # Bucket access rules
│  └─ tests/
│     ├─ test_health.py
│     ├─ test_buckets.py
│     ├─ test_files.py
│     └─ test_signed_urls.py
├─ .env.example
├─ requirements.txt
├─ Dockerfile
└─ vercel.json
```

## Environment Variables

Create `.env`:

```bash
APP_ENV=development
APP_PORT=8000

SUPABASE_URL=your_supabase_url
SUPABASE_JWT_SECRET=your_supabase_jwt_secret

GCP_PROJECT_ID=your_gcp_project_id
GCP_DEFAULT_BUCKET=optional_default_bucket
GCP_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'

SIGNED_URL_EXPIRY_SECONDS=900
MAX_UPLOAD_SIZE_MB=50
ALLOWED_MIME_TYPES=image/jpeg,image/png,application/pdf
```

## Local Development

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## API Endpoints (Planned)

- `GET /health`
- `GET /buckets`
- `GET /buckets/{bucket}/files`
- `POST /files/upload-url`
- `POST /files/download-url`
- `DELETE /buckets/{bucket}/files/{path}`

## Security Guidelines

- Enforce least-privilege OAuth and IAM scopes.
- Reject any request with invalid/expired JWT.
- Use short-lived presigned URLs with strict object paths.
- Keep service account credentials in secure env/secret storage.
- Add logging for upload/delete events for traceability.

## Contribution

At present, this repository is maintained by the project owner only.

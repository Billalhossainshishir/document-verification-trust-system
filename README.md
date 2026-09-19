# Document Verification & Trust System

[![Tests](https://github.com/Billalhossainshishir/document-verification-trust-system/actions/workflows/tests.yml/badge.svg)](https://github.com/Billalhossainshishir/document-verification-trust-system/actions/workflows/tests.yml)
[![GitHub Pages](https://github.com/Billalhossainshishir/document-verification-trust-system/actions/workflows/pages.yml/badge.svg)](https://github.com/Billalhossainshishir/document-verification-trust-system/actions/workflows/pages.yml)

A document-integrity project that compares a candidate file with a registered SHA-256 fingerprint. The backend records verification attempts and signs receipt payloads with Ed25519 without storing the uploaded document body.

Read the [reviewer guide](docs/REVIEWER_GUIDE.md) for execution modes, reproducible setup, architecture, verification steps and known limitations.

## Quick recruiter view

| Explore | Link |
| --- | --- |
| **Live demo** | https://billalhossainshishir.github.io/document-verification-trust-system/ |
| **Reviewer guide** | [docs/REVIEWER_GUIDE.md](docs/REVIEWER_GUIDE.md) |
| **Architecture** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **API reference** | [docs/API.md](docs/API.md) |
| **Testing** | [docs/TESTING.md](docs/TESTING.md) |
| **Threat model** | [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) |
| **Case study** | [docs/CASE_STUDY.md](docs/CASE_STUDY.md) |

**60-second demo:** Register sample → verify same file → confirm VERIFIED → verify modified sample → confirm FAILED → inspect audit trail and receipt.

The system registers a document fingerprint using SHA-256, verifies future copies without retaining the original document bytes, records an audit trail, creates an Ed25519-signed verification receipt, and exposes public verification metadata without exposing confidential document contents.

## Portfolio strategy

This repository deliberately contains two experiences, using the same strategy as Project 3.

### 1. Full engineering project

The repository contains the actual backend implementation:

- Python + FastAPI
- SQLAlchemy models
- SQLite for low-friction local evaluation
- PostgreSQL-ready Docker Compose stack
- SHA-256 document fingerprinting
- privacy-aware processing: original bytes are discarded after hashing
- deterministic exact-copy verification
- audit logging
- Ed25519-signed canonical verification receipts
- downloadable PDF receipts
- QR public-verification endpoint
- analytics endpoints
- backend-connected HTML/CSS/JavaScript client
- automated pytest suite
- GitHub Actions CI
- architecture, API, testing, threat-model and case-study documentation

### 2. Instant recruiter demo

Live demo target:

https://billalhossainshishir.github.io/document-verification-trust-system/

The root index.html and assets directory contain a browser-only simulation of the core trust workflow.

The public demo uses the Web Crypto API for SHA-256 and localStorage for temporary browser records, so it opens instantly on GitHub Pages without a hosted Python server or database.

**Transparency:** the GitHub Pages version does not pretend to be the deployed FastAPI/PostgreSQL application. The full server-side implementation is in this repository.

## Recruiter flow

1. Download the sample document.
2. Register its fingerprint.
3. A Verification ID and SHA-256 fingerprint are created.
4. Verify the same file and get VERIFIED.
5. Download the modified sample.
6. Verify it under the same ID and get FAILED.
7. Inspect the audit trail and verification receipt.

The core interaction is designed to be understood in 30–60 seconds.

## Security principle

AI does not decide document integrity.

The source of truth is deterministic cryptographic comparison: registered file bytes are hashed with SHA-256 and the candidate file is hashed again. Identical fingerprints produce VERIFIED; different fingerprints produce FAILED.

## Privacy design

Registration reads uploaded bytes in memory, calculates SHA-256, stores selected metadata plus the fingerprint, and discards the file bytes. The application database does not store the original uploaded document.

## Backend signed receipts

Every verification attempt creates a canonical receipt payload containing the Verification ID, Document ID, filenames, status, timestamps and both SHA-256 values.

The browser demo downloads unsigned example JSON. The backend signs its canonical payload using Ed25519. The signing private key is generated outside source control and persisted at the configured signing-key path.

## Repository structure

- index.html — GitHub Pages recruiter demo
- verify.html — browser-demo public verification record
- assets/ — static demo CSS and JavaScript
- backend/ — full FastAPI implementation
- frontend/ — real backend-connected browser client
- tests/ — automated API tests
- docs/ — architecture, API, testing, threat model and case study
- .github/workflows/ — tests and GitHub Pages deployment
- docker-compose.yml — PostgreSQL + API + frontend stack

## Main API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /health | application health |
| POST | /api/documents/register | register SHA-256 fingerprint |
| POST | /api/documents/verify | verify a candidate copy |
| GET | /api/documents | registered document metadata |
| GET | /api/documents/{document_id} | one document record |
| GET | /api/public/verify/{verification_id} | privacy-safe public metadata |
| GET | /api/public/qr/{verification_id} | QR code for public verification |
| GET | /api/receipts/{receipt_id} | signed receipt |
| GET | /api/receipts/{receipt_id}/pdf | downloadable PDF receipt |
| POST | /api/receipts/{receipt_id}/verify-signature | verify receipt signature |
| GET | /api/audit | audit trail |
| GET | /api/analytics | demo metrics |
| POST | /api/reset | clear controlled demo data |

## Known public-verification limitation

The default backend QR URL opens a static page that only reads browser localStorage. It does not fetch backend records and is not a working cross-device lookup. Use the backend public-verification API for those records; see the reviewer guide for the missing integration.

## Run locally

Create a Python virtual environment, install requirements.txt, then run:

python -m uvicorn backend.app.main:app --reload --port 8000

Swagger documentation is available at http://127.0.0.1:8000/docs.

## Docker and PostgreSQL

Run:

docker compose up --build

The API is exposed on port 8000 and the backend-connected frontend on port 8080.

## Testing

Run:

python -m pytest

The suite covers registration, exact-copy verification, modified-copy failure, unknown IDs, empty uploads, audit events, signed receipts, PDF generation, QR generation, public-record privacy and analytics.

GitHub Actions runs tests automatically on pushes and pull requests.

## Trust boundary

This project proves byte-level continuity with the fingerprint that was originally registered. A successful hash match does not independently prove that the issuer is legitimate, the original was genuine, or the registrar had authority.

See docs/THREAT_MODEL.md.

## CV / portfolio wording

**Document Verification & Trust System — Sep 2026**

Built a privacy-aware Python/FastAPI document verification platform that fingerprints files with SHA-256 without retaining document contents, detects modified copies deterministically, records auditable verification events, generates Ed25519-signed JSON/PDF receipts and QR-based public verification records, supports PostgreSQL/Docker deployment, and includes an interactive GitHub Pages recruiter demo.

## Why the live demo is separate

GitHub Pages cannot execute Python/FastAPI or host PostgreSQL.

Instead of pretending a static page is a deployed backend:

- GitHub Pages demonstrates the product behaviour interactively.
- The repository proves the actual backend, database, cryptography, testing and deployment implementation.

That separation is intentional and documented.

## Limitations and scope

- A successful SHA-256 match proves byte-level continuity with the registered fingerprint; it does not independently prove issuer identity, legal authenticity or registrar authority.
- The GitHub Pages demo uses browser-side Web Crypto and localStorage and is not the FastAPI/PostgreSQL backend.
- Browser-demo receipts are illustrative; the backend implementation is where canonical receipt payloads are signed with Ed25519.
- The default backend QR target does not provide a complete cross-device browser lookup; use the public-verification API for backend records.
- Production use would require identity/authority verification, secure key management, access control, operational monitoring and deployment hardening.

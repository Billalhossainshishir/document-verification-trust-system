# Case Study

## Problem

Organisations may need to answer a narrow question: is this file exactly the same digital document that was previously registered?

Storing every original document increases privacy and retention risk. AI is also inappropriate for a byte-integrity decision because integrity should be deterministic.

## Solution

Store a SHA-256 fingerprint and selected metadata instead of the original file. Hash a candidate copy and compare it with the registered fingerprint. Record each attempt and generate a digitally signed receipt.

## Key decisions

### Deterministic cryptography before AI

SHA-256 equality is the source of truth. AI could later assist with metadata extraction, but not integrity.

### Minimise retained data

The application reads bytes only long enough to hash them.

### Separate public demo from backend deployment

GitHub Pages is a browser-only simulation because Pages cannot run FastAPI or PostgreSQL. The repository separately proves the full implementation.

### Signed evidence

Verification receipt data is canonicalised and signed with Ed25519, demonstrating the difference between verifying a document and signing evidence of that verification.

### Explicit trust boundary

A matching hash proves continuity from registered bytes. It does not prove issuer legitimacy.

## Recruiter value

The project demonstrates FastAPI, SQLAlchemy, PostgreSQL, secure hashing, digital signatures, privacy-aware architecture, audit logging, QR/PDF generation, Docker, automated testing and transparent engineering communication.

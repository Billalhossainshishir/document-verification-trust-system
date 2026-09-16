# Architecture

## Goal

Register a cryptographic fingerprint for a document, verify future copies deterministically, provide an audit trail and generate a signed receipt without retaining the original file body.

## Full backend flow

Registration:

File upload → size validation → SHA-256 → Document metadata + fingerprint → audit event → discard file bytes.

Verification:

Candidate upload → SHA-256 → constant-time comparison → VERIFIED or FAILED → VerificationAttempt → audit event → canonical receipt → Ed25519 signature → receipt record.

## Components

### FastAPI

Handles multipart uploads, registration, verification, public verification metadata, QR generation, receipt retrieval, analytics and reset operations.

### SQLAlchemy

The same model layer supports SQLite locally and PostgreSQL through Docker Compose. Core entities are Document, VerificationAttempt, AuditEvent and Receipt.

### Hashing

SHA-256 is calculated over exact file bytes. The same bytes produce the same digest; modified bytes produce a different digest with overwhelming probability.

### Receipt signing

Receipt payloads are serialised into canonical JSON and signed with Ed25519. The private key is stored outside Git and the receipt includes the Base64 public key and signature.

### PDF receipt

The PDF is a human-readable presentation of the stored verification receipt. The signed canonical JSON is the cryptographic source of truth.

### QR verification

The backend generates a QR code pointing to the public verification URL for the Verification ID.

### GitHub Pages demo

GitHub Pages cannot run Python or PostgreSQL. The root static site therefore uses Web Crypto SHA-256 and localStorage to simulate the same core registration and verification flow transparently.

## Trust boundary

The system proves integrity relative to the originally registered fingerprint. It does not independently establish issuer identity or legal authenticity.

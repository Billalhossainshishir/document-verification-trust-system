# API Reference

Local base URL: http://127.0.0.1:8000

Swagger UI: http://127.0.0.1:8000/docs

## GET /health

Returns application health.

## POST /api/documents/register

Multipart fields: file, optional registered_by and optional document_type.

The server calculates SHA-256 and stores metadata plus the fingerprint only.

## POST /api/documents/verify

Multipart fields: verification_id and candidate file.

Returns VERIFIED when candidate SHA-256 exactly matches the registered fingerprint; otherwise FAILED. Every verification creates an audit event and signed receipt.

## GET /api/documents

Returns document metadata.

## GET /api/documents/{document_id}

Returns one document record.

## GET /api/public/verify/{verification_id}

Returns IDs, filename, type, registration timestamp, SHA-256 and latest verification result without returning document contents.

## GET /api/public/qr/{verification_id}

Returns a PNG QR code for the public verification page.

## GET /api/receipts/{receipt_id}

Returns the canonical receipt payload, Base64 Ed25519 signature, Base64 public key and signature validation result.

## GET /api/receipts/{receipt_id}/pdf

Downloads a human-readable PDF receipt.

## POST /api/receipts/{receipt_id}/verify-signature

Verifies the stored receipt payload against the Ed25519 signature and public key.

## GET /api/audit

Returns audit events. Supports document_ref and limit query parameters.

## GET /api/analytics

Returns document, verification and receipt metrics.

## POST /api/reset

Clears controlled demo records. This endpoint is intended for demo use.

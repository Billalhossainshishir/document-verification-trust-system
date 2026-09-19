# Reviewing and running document verification

## What is being verified

A successful check means the candidate bytes match the previously registered SHA-256 fingerprint. It does not establish that the original document is genuine, that its issuer is authorised, or that its contents are true. This is separate from the AI-assisted product-authenticity capstone described elsewhere in the portfolio.

| Capability | GitHub Pages | Python backend |
| --- | --- | --- |
| SHA-256 comparison | Web Crypto | Python hashing |
| Record storage | Browser localStorage | SQLite or PostgreSQL |
| Receipt | Unsigned demonstration JSON | Ed25519-signed canonical JSON and a PDF representation |
| Lookup | Same browser and origin only | Database-backed public metadata API |

## Local setup

Python 3.12 matches the checked-in CI workflow. From a fresh clone:

```powershell
git clone https://github.com/Billalhossainshishir/document-verification-trust-system.git
cd document-verification-trust-system
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
```

In a second terminal, run `py -3.12 -m http.server 8080 --directory frontend`. Open `http://127.0.0.1:8080` and check the API base field points to `http://127.0.0.1:8000`. Swagger is at `http://127.0.0.1:8000/docs`.

Alternatively, `docker compose up --build` starts the API, PostgreSQL and the frontend. The ports are 8000 and 8080. Configuration in local Python uses process environment variables; copying `.env.example` to `.env` does not itself load them.

## Walkthrough and evidence

1. Register a small synthetic file; retain the returned `verification_id`.
2. Verify the same bytes under that ID; expect VERIFIED.
3. Change the file and verify again under the same ID; expect FAILED.
4. Inspect audit records and the receipt returned by the verification response.
5. In Swagger, call `/api/receipts/{receipt_id}/verify-signature`; inspect `signature_valid`.
6. Retrieve the PDF and compare its fields with the canonical JSON. The signature covers the JSON payload, not the PDF file bytes.

Run `.\.venv\Scripts\python.exe -m pytest` for the backend tests. These exercise API behaviour, receipt signing and QR/PDF generation. QR image generation alone does not test whether scanning its destination retrieves the correct record.

## Known QR and public-page limitation

The backend currently constructs a URL ending in `/verify.html?id=...` using `PUBLIC_BASE_URL`. Its default points to GitHub Pages. That page reads browser localStorage and does not fetch the backend record. A document registered through the backend therefore will not automatically appear at that URL, and another device has no copy of the original browser's storage.

For backend evidence, use `GET /api/public/verify/{verification_id}` directly in Swagger. A shared public verification page needs to call that endpoint against the appropriate API. Merely changing the base URL does not add the missing lookup logic.

## Persistence and trust

The local signing key defaults to `.data/receipt_signing_key.pem`; Docker stores it in a named signing-data volume. Preserve it for continuity and never commit the private key. Compose volume deletion removes both the database and signing-key storage.

The application does not save uploaded file bodies, but it does retain filenames, identifiers, timestamps and audit metadata. Describe this as reduced content retention, not anonymity. Public keys included in receipts also need an external trust mechanism before a recipient can associate them with an authorised issuer. See [the threat model](THREAT_MODEL.md) for the existing security boundaries.


## Recorded verification evidence

At documentation review, the existing [GitHub Actions test run](https://github.com/Billalhossainshishir/document-verification-trust-system/actions/runs/35169489302) reported `success` for `f33813f583564ffedcb59f9de58354baa1256287`. This records an existing CI result; the documentation review did not install dependencies or rerun the application locally. Commands above were checked against source files and configuration. A successful CI run does not establish production readiness or validate untested UI integrations.

# Testing Strategy

Run:

python -m pytest

The tests use SQLite for fast local and CI execution.

Covered behaviour includes:

1. Application health.
2. Registration creates IDs and a SHA-256 fingerprint.
3. The registration response documents the privacy behaviour.
4. An exact copy verifies successfully.
5. A modified copy fails.
6. Unknown Verification IDs return 404.
7. Empty files are rejected.
8. Registration, verification and receipt events appear in the audit log.
9. Ed25519 receipt signatures verify.
10. PDF receipts are generated.
11. Public verification data does not expose document contents.
12. QR generation returns PNG.
13. Analytics counters reflect verification activity.

## Manual public-demo test

Open the GitHub Pages site, download the sample file, register it, verify the same file and confirm VERIFIED. Then download the modified sample, verify it under the same Verification ID and confirm FAILED. Inspect the audit log, receipt and public record.

GitHub Actions executes the backend tests on pushes and pull requests.

# Threat Model and Trust Boundaries

## What the system proves

A successful verification proves that the candidate file bytes produce the same SHA-256 fingerprint as the bytes registered under the selected Verification ID. That is an integrity claim.

## What it does not prove

A hash match does not automatically prove the real-world issuer is legitimate, the original document was genuine, the registrar had authority, a named person is the presenter, or the document has not been revoked externally.

## Threats and controls

### Modified copy

Control: deterministic SHA-256 mismatch produces FAILED.

### Confidential-content retention

Control: uploaded bytes are hashed in memory and not stored in the application database.

### Receipt tampering

Control: canonical receipt JSON is digitally signed with Ed25519.

### Public-record overexposure

Control: the public endpoint exposes selected metadata and fingerprint, not original file contents.

### Oversized uploads

Control: configurable file-size limit. Production should additionally enforce proxy limits and streaming hashing.

### Signing-key leakage

Control: private key is generated outside source control. Production systems should use managed secrets, KMS or HSM.

## Portfolio simplifications

The recruiter demo is intentionally login-free, CORS is permissive for demo convenience and reset is exposed for controlled demonstrations. Production hardening would add authentication, RBAC, rate limiting, issuer identity, revocation, managed keys and monitoring.

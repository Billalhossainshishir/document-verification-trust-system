import os
from pathlib import Path

TEST_DB = Path("test_document_trust.db")
TEST_KEY = Path("test_receipt_key.pem")
for path in (TEST_DB, TEST_KEY):
    if path.exists():
        path.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///./{TEST_DB.name}"
os.environ["SIGNING_KEY_FILE"] = str(TEST_KEY)
os.environ["PUBLIC_BASE_URL"] = "https://example.test/document-trust"

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)
SAMPLE = b"Certificate of Completion\nStudent: Portfolio Demo\nCourse: Secure Systems\n"

def register_sample():
    r = client.post("/api/documents/register",
        files={"file": ("certificate.txt", SAMPLE, "text/plain")},
        data={"registered_by": "Test Suite", "document_type": "Certificate"})
    assert r.status_code == 200
    return r.json()

def setup_function():
    client.post("/api/reset")

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_registration():
    d = register_sample()
    assert d["verification_id"].startswith("VER-")
    assert len(d["sha256"]) == 64
    assert "not stored" in d["privacy_note"]

def test_same_document_verifies():
    d = register_sample()
    r = client.post("/api/documents/verify",
        files={"file": ("copy.txt", SAMPLE, "text/plain")},
        data={"verification_id": d["verification_id"]})
    x = r.json()
    assert r.status_code == 200 and x["status"] == "VERIFIED"
    assert x["registered_sha256"] == x["candidate_sha256"]
    assert x["receipt"]["signature_valid"] is True

def test_modified_document_fails():
    d = register_sample()
    x = client.post("/api/documents/verify",
        files={"file": ("modified.txt", SAMPLE + b"MODIFIED", "text/plain")},
        data={"verification_id": d["verification_id"]}).json()
    assert x["status"] == "FAILED"
    assert x["registered_sha256"] != x["candidate_sha256"]

def test_unknown_id():
    r = client.post("/api/documents/verify",
        files={"file": ("x.txt", b"x", "text/plain")},
        data={"verification_id": "VER-UNKNOWN"})
    assert r.status_code == 404

def test_empty_file_rejected():
    r = client.post("/api/documents/register", files={"file": ("empty.txt", b"", "text/plain")})
    assert r.status_code == 400

def test_audit_and_receipt_signature():
    d = register_sample()
    x = client.post("/api/documents/verify",
        files={"file": ("copy.txt", SAMPLE, "text/plain")},
        data={"verification_id": d["verification_id"]}).json()
    types = {e["event_type"] for e in client.get("/api/audit").json()}
    assert {"DOCUMENT_REGISTERED", "VERIFICATION_SUCCESS", "RECEIPT_GENERATED"}.issubset(types)
    rid = x["receipt"]["receipt_id"]
    assert client.post(f"/api/receipts/{rid}/verify-signature").json()["signature_valid"] is True

def test_pdf_public_qr_and_analytics():
    d = register_sample()
    x = client.post("/api/documents/verify",
        files={"file": ("copy.txt", SAMPLE, "text/plain")},
        data={"verification_id": d["verification_id"]}).json()
    rid = x["receipt"]["receipt_id"]
    pdf = client.get(f"/api/receipts/{rid}/pdf")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    public = client.get(f"/api/public/verify/{d['verification_id']}").json()
    assert "content" not in public
    qr = client.get(f"/api/public/qr/{d['verification_id']}")
    assert qr.status_code == 200 and qr.content.startswith(b"\x89PNG")
    metrics = client.get("/api/analytics").json()
    assert metrics["registered_documents"] == 1
    assert metrics["successful_verifications"] == 1
    assert metrics["signed_receipts"] == 1

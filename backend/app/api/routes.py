import io
import secrets
from datetime import datetime, timezone
import qrcode
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from ..config import MAX_FILE_SIZE_MB, PUBLIC_BASE_URL
from ..db import get_db
from ..models import AuditEvent, Document, Receipt, VerificationAttempt
from ..schemas import AuditOut, DocumentOut
from ..services.audit import record_audit
from ..services.hashing import sha256_bytes
from ..services.pdf_receipt import build_receipt_pdf
from ..services.receipts import create_receipt, receipt_to_dict
from ..services.signing import signer

router = APIRouter(prefix="/api")

def _read_upload(file: UploadFile) -> bytes:
    data = file.file.read()
    if not data:
        raise HTTPException(400, "Uploaded file is empty.")
    if len(data) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {MAX_FILE_SIZE_MB} MB limit.")
    return data

def _doc(db: Session, verification_id: str):
    document = db.query(Document).filter(Document.verification_id == verification_id).first()
    if not document:
        raise HTTPException(404, "Verification ID not found.")
    return document

@router.post("/documents/register")
def register_document(
    file: UploadFile = File(...),
    registered_by: str | None = Form(default=None),
    document_type: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    data = _read_upload(file)
    document = Document(
        document_id=f"DOC-{secrets.token_hex(5).upper()}",
        verification_id=f"VER-{secrets.token_hex(5).upper()}",
        filename=file.filename or "unnamed-document",
        content_type=file.content_type,
        size_bytes=len(data),
        sha256=sha256_bytes(data),
        registered_by=registered_by or "Portfolio Demo",
        document_type=document_type or "Unspecified",
    )
    db.add(document)
    db.flush()
    record_audit(db, "DOCUMENT_REGISTERED",
                 f"Document {document.filename} registered using SHA-256 fingerprinting.",
                 document.document_id, {"verification_id": document.verification_id})
    db.commit()
    db.refresh(document)
    return {
        **DocumentOut.model_validate(document).model_dump(),
        "privacy_note": "Original file bytes were discarded after hashing and were not stored.",
        "public_verification_url": f"{PUBLIC_BASE_URL}/verify.html?id={document.verification_id}",
    }

@router.post("/documents/verify")
def verify_document(
    verification_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    document = _doc(db, verification_id)
    data = _read_upload(file)
    candidate_hash = sha256_bytes(data)
    status = "VERIFIED" if secrets.compare_digest(document.sha256, candidate_hash) else "FAILED"
    attempt = VerificationAttempt(
        attempt_id=f"ATT-{secrets.token_hex(5).upper()}",
        document=document,
        candidate_filename=file.filename or "unnamed-document",
        candidate_sha256=candidate_hash,
        status=status,
        verified_at=datetime.now(timezone.utc),
    )
    db.add(attempt)
    db.flush()
    record_audit(
        db,
        "VERIFICATION_SUCCESS" if status == "VERIFIED" else "VERIFICATION_FAILED",
        f"Verification {status.lower()} for {verification_id}.",
        document.document_id,
        {"attempt_id": attempt.attempt_id},
    )
    receipt = create_receipt(db, document, attempt)
    db.commit()
    db.refresh(attempt)
    db.refresh(receipt)
    return {
        "attempt_id": attempt.attempt_id,
        "verification_id": document.verification_id,
        "document_id": document.document_id,
        "filename": document.filename,
        "candidate_filename": attempt.candidate_filename,
        "status": status,
        "registered_sha256": document.sha256,
        "candidate_sha256": candidate_hash,
        "verified_at": attempt.verified_at,
        "receipt": receipt_to_dict(receipt),
    }

@router.get("/documents", response_model=list[DocumentOut])
def list_documents(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    return db.query(Document).order_by(desc(Document.registered_at)).limit(limit).all()

@router.get("/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document:
        raise HTTPException(404, "Document not found.")
    return document

@router.get("/public/verify/{verification_id}")
def public_verification(verification_id: str, db: Session = Depends(get_db)):
    document = _doc(db, verification_id)
    latest = (
        db.query(VerificationAttempt)
        .filter(VerificationAttempt.document_id == document.id)
        .order_by(desc(VerificationAttempt.verified_at))
        .first()
    )
    return {
        "verification_id": document.verification_id,
        "document_id": document.document_id,
        "filename": document.filename,
        "document_type": document.document_type,
        "registered_at": document.registered_at,
        "sha256": document.sha256,
        "current_status": document.status,
        "latest_verification": None if not latest else {
            "status": latest.status, "verified_at": latest.verified_at, "attempt_id": latest.attempt_id
        },
        "privacy_note": "Document contents are not exposed by this endpoint.",
    }

@router.get("/public/qr/{verification_id}")
def verification_qr(verification_id: str, db: Session = Depends(get_db)):
    _doc(db, verification_id)
    image = qrcode.make(f"{PUBLIC_BASE_URL}/verify.html?id={verification_id}")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return Response(buffer.getvalue(), media_type="image/png")

@router.get("/receipts/{receipt_id}")
def get_receipt(receipt_id: str, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    if not receipt:
        raise HTTPException(404, "Receipt not found.")
    return receipt_to_dict(receipt)

@router.get("/receipts/{receipt_id}/pdf")
def receipt_pdf(receipt_id: str, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    if not receipt:
        raise HTTPException(404, "Receipt not found.")
    return Response(
        build_receipt_pdf(receipt),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{receipt_id}.pdf"'},
    )

@router.post("/receipts/{receipt_id}/verify-signature")
def verify_receipt_signature(receipt_id: str, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.receipt_id == receipt_id).first()
    if not receipt:
        raise HTTPException(404, "Receipt not found.")
    valid = signer.verify(receipt.payload_json.encode(), receipt.signature_b64, receipt.public_key_b64)
    return {"receipt_id": receipt_id, "signature_valid": valid, "algorithm": "Ed25519"}

@router.get("/audit", response_model=list[AuditOut])
def audit_log(document_ref: str | None = None, limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    query = db.query(AuditEvent)
    if document_ref:
        query = query.filter(AuditEvent.document_ref == document_ref)
    return query.order_by(desc(AuditEvent.created_at)).limit(limit).all()

@router.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    registered = db.query(func.count(Document.id)).scalar() or 0
    attempts = db.query(func.count(VerificationAttempt.id)).scalar() or 0
    verified = db.query(func.count(VerificationAttempt.id)).filter(VerificationAttempt.status == "VERIFIED").scalar() or 0
    failed = db.query(func.count(VerificationAttempt.id)).filter(VerificationAttempt.status == "FAILED").scalar() or 0
    receipts = db.query(func.count(Receipt.id)).scalar() or 0
    return {
        "registered_documents": registered,
        "verification_attempts": attempts,
        "successful_verifications": verified,
        "failed_verifications": failed,
        "signed_receipts": receipts,
        "success_rate": round(verified / attempts * 100, 2) if attempts else 0.0,
    }

@router.post("/reset")
def reset_demo(db: Session = Depends(get_db)):
    db.query(Receipt).delete()
    db.query(VerificationAttempt).delete()
    db.query(Document).delete()
    db.query(AuditEvent).delete()
    db.commit()
    return {"status": "reset", "message": "Demo records cleared."}

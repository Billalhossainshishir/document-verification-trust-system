import json
import secrets
from ..models import Receipt
from .audit import record_audit
from .signing import signer

def canonical_json(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def create_receipt(db, document, attempt):
    receipt_id = f"RCP-{secrets.token_hex(5).upper()}"
    payload = {
        "receipt_id": receipt_id,
        "verification_id": document.verification_id,
        "document_id": document.document_id,
        "document": document.filename,
        "candidate_document": attempt.candidate_filename,
        "status": attempt.status,
        "registered_at": document.registered_at.isoformat(),
        "verified_at": attempt.verified_at.isoformat(),
        "registered_sha256": document.sha256,
        "candidate_sha256": attempt.candidate_sha256,
        "algorithm": "SHA-256",
        "receipt_signature": "Ed25519",
    }
    payload_json = canonical_json(payload)
    receipt = Receipt(
        receipt_id=receipt_id,
        document=document,
        attempt=attempt,
        status=attempt.status,
        payload_json=payload_json,
        signature_b64=signer.sign(payload_json.encode()),
        public_key_b64=signer.public_key_b64,
    )
    db.add(receipt)
    record_audit(db, "RECEIPT_GENERATED", f"Signed receipt {receipt_id} generated.",
                 document.document_id, {"receipt_id": receipt_id, "status": attempt.status})
    return receipt

def receipt_to_dict(receipt):
    return {
        "receipt_id": receipt.receipt_id,
        "status": receipt.status,
        "payload": json.loads(receipt.payload_json),
        "signature_b64": receipt.signature_b64,
        "public_key_b64": receipt.public_key_b64,
        "signature_valid": signer.verify(
            receipt.payload_json.encode(), receipt.signature_b64, receipt.public_key_b64
        ),
        "created_at": receipt.created_at,
    }

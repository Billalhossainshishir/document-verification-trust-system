import json
from sqlalchemy.orm import Session
from ..models import AuditEvent

def record_audit(db: Session, event_type: str, message: str, document_ref=None, metadata=None):
    event = AuditEvent(
        document_ref=document_ref,
        event_type=event_type,
        message=message,
        metadata_json=json.dumps(metadata, sort_keys=True) if metadata else None,
    )
    db.add(event)
    return event

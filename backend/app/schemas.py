from pydantic import BaseModel, ConfigDict

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    document_id: str
    verification_id: str
    filename: str
    content_type: str | None
    size_bytes: int
    sha256: str
    registered_at: object
    registered_by: str | None
    document_type: str | None
    status: str

class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    document_ref: str | None
    event_type: str
    message: str
    metadata_json: str | None
    created_at: object

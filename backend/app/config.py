import os

APP_NAME = "Document Verification & Trust System"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./document_trust.db")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
SIGNING_KEY_FILE = os.getenv("SIGNING_KEY_FILE", "./.data/receipt_signing_key.pem")
PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL",
    "https://billalhossainshishir.github.io/document-verification-trust-system",
).rstrip("/")
CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]

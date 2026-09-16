from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .config import APP_NAME, CORS_ORIGINS
from .db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="Privacy-aware SHA-256 document verification with audit logging, QR verification and Ed25519-signed receipts.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

@app.get("/")
def root():
    return {
        "name": APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "privacy": "Original uploaded documents are hashed in memory and are not stored.",
    }

@app.get("/health")
def health():
    return {"status": "ok", "service": APP_NAME}

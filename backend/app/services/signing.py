import base64
from pathlib import Path
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from ..config import SIGNING_KEY_FILE

class ReceiptSigner:
    def __init__(self, key_path: str = SIGNING_KEY_FILE):
        self.key_path = Path(key_path)
        self.private_key = self._load_or_create()

    def _load_or_create(self):
        if self.key_path.exists():
            key = serialization.load_pem_private_key(self.key_path.read_bytes(), password=None)
            if not isinstance(key, Ed25519PrivateKey):
                raise ValueError("Signing key is not Ed25519")
            return key
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        key = Ed25519PrivateKey.generate()
        pem = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        self.key_path.write_bytes(pem)
        return key

    @property
    def public_key_b64(self) -> str:
        raw = self.private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
        return base64.b64encode(raw).decode("ascii")

    def sign(self, payload: bytes) -> str:
        return base64.b64encode(self.private_key.sign(payload)).decode("ascii")

    @staticmethod
    def verify(payload: bytes, signature_b64: str, public_key_b64: str) -> bool:
        try:
            public_key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64))
            public_key.verify(base64.b64decode(signature_b64), payload)
            return True
        except (ValueError, InvalidSignature):
            return False

signer = ReceiptSigner()

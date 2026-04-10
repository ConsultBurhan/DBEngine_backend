"""Crypto service for password hashing and salt generation."""
import base64
import hashlib
import secrets


class CryptoService:
    """Service for cryptographic operations like password hashing."""

    def __init__(self):
        pass

    async def generate_salt(self) -> str:
        """Generate a random 32-byte salt and return as base64 string."""
        salt_bytes = secrets.token_bytes(32)
        return base64.b64encode(salt_bytes).decode("utf-8")

    async def hash_password(self, password: str, salt: str) -> str:
        """Hash password using PBKDF2 with SHA256, 10000 iterations."""
        salt_bytes = base64.b64decode(salt)
        password_bytes = password.encode("utf-8")

        hash_bytes = hashlib.pbkdf2_hmac(
            "sha256", password_bytes, salt_bytes, 10000, dklen=32
        )
        return base64.b64encode(hash_bytes).decode("utf-8")

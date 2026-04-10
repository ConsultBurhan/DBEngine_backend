"""
JWT Token Service - Implementation matching C# JwtTokenService.
"""
import base64
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt

from config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


class JWTService:
    """Service for generating and validating JWT tokens."""

    def __init__(
        self,
        secret_key: str = SECRET_KEY,
        access_token_expiry_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expiry_days: int = 7,
    ):
        self._secret_key = secret_key
        self._access_token_expiry_minutes = access_token_expiry_minutes
        self._refresh_token_expiry_days = refresh_token_expiry_days

    def generate_access_token(
        self,
        user_id: int,
        username: str,
        client_id: Optional[str] = None,
        default_language: Optional[str] = None,
        subscriber_id: int = 0,
    ) -> str:
        """Generate access token with claims matching C# implementation."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=self._access_token_expiry_minutes)

        claims = {
            "sub": str(user_id),
            "nameid": str(user_id),
            "unique_name": username,
            "UserId": str(user_id),
            "username": username,
            "ClientId": client_id,
            "ClientLanguage": default_language,
            "SubscriberId": str(subscriber_id),
            "jti": secrets.token_hex(16),
            "iat": int(now.timestamp()),
            "exp": int(expires.timestamp()),
        }

        return jwt.encode(claims, self._secret_key, algorithm=ALGORITHM)

    def generate_refresh_token(self) -> str:
        """Generate a cryptographically secure refresh token."""
        random_bytes = secrets.token_bytes(32)
        return base64.b64encode(random_bytes).decode("utf-8")

    def get_principal_from_expired_token(self, token: str) -> dict:
        """Extract claims from expired token without validating expiration."""
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[ALGORITHM],
                options={"verify_exp": False},
            )

            # Verify algorithm matches (HMAC SHA256)
            header = jwt.get_unverified_header(token)
            if header.get("alg") != ALGORITHM:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token algorithm",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    def validate_refresh_token(self, refresh_token: str) -> bool:
        """Validate refresh token format (non-empty and minimum length)."""
        return bool(refresh_token and len(refresh_token) >= 32)

    def get_client_id_from_access_token(self, request: Request) -> int:
        """Extract ClientId from current request's access token."""
        user = getattr(request.state, "user", None)
        if user:
            client_id_str = user.get("ClientId")
            if client_id_str:
                try:
                    return int(client_id_str)
                except ValueError:
                    pass
        return 0

    def get_user_id_from_access_token(self, request: Request) -> int:
        """Extract UserId from current request's access token."""
        user = getattr(request.state, "user", None)
        if user:
            user_id_str = user.get("UserId")
            if user_id_str:
                try:
                    return int(user_id_str)
                except ValueError:
                    pass
        return 0

    def get_client_language_from_access_token(self, request: Request) -> str:
        """Extract ClientLanguage from current request's access token."""
        user = getattr(request.state, "user", None)
        if user:
            return user.get("ClientLanguage", "")
        return ""

    def get_sub_id_from_access_token(self, request: Request) -> int:
        """Extract SubscriberId from current request's access token."""
        user = getattr(request.state, "user", None)
        if user:
            subscriber_id_str = user.get("SubscriberId")
            if subscriber_id_str:
                try:
                    return int(subscriber_id_str)
                except ValueError:
                    pass
        return 0

    def decode_token(self, token: str) -> dict:
        """Decode and validate a token, returning the payload."""
        try:
            return jwt.decode(
                token,
                self._secret_key,
                algorithms=[ALGORITHM]
            )
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        except jwt.JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc



# Singleton class for JWT 
_jwt_service: Optional[JWTService] = None
import asyncio

_jwt_service: Optional[JWTService] = None
_jwt_service_lock = asyncio.Lock()

async def get_jwt_service() -> JWTService:
    """Get JWT service instance."""
    global _jwt_service
    async with _jwt_service_lock:
        if _jwt_service is None:
            _jwt_service = JWTService()
    return _jwt_service



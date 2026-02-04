"""JWT token provider for authentication."""
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings


class JWTProvider:
    """Provider for JWT token creation and validation."""

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """Create JWT access token.

        Args:
            data: Dictionary with token payload.
            expires_delta: Optional custom expiration time delta.
                           If None, uses default from application settings.

        Returns:
            Encoded JWT token string.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.jwt_access_token_expire_minutes
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )
        return encoded_jwt

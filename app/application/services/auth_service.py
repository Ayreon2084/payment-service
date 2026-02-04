"""Authentication service for user authentication and token generation."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.infrastructure.auth.jwt_provider import JWTProvider
from app.infrastructure.db.repositories.user_repo import UserRepository


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.jwt_provider = JWTProvider()

    async def authenticate_user(self, email: str, password: str):
        """Authenticate user by email and password.

        Args:
            email: User email address.
            password: Plain text password.

        Returns:
            User instance if authentication successful, False otherwise.
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

    def create_token_for_user(self, user_id: int):
        """Create JWT access token for a user.

        Args:
            user_id: ID of the user.

        Returns:
            JWT token string.
        """
        return self.jwt_provider.create_access_token(data={"sub": str(user_id)})

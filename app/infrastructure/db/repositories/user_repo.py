"""User repository for database operations on User model."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models.user_model import User
from app.infrastructure.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(model=User, session=session)

    async def delete(self, obj_id: int) -> bool:
        """Soft delete override for users."""
        updated_user = await self.update(
            obj_id, is_deleted=True, deleted_at=datetime.now(timezone.utc)
        )
        return updated_user is not None

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by their unique email address."""
        query = select(self.model).where(self.model.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Fetch a user by their unique ID."""
        query = select(self.model).where(self.model.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_accounts(
        self, user_id: int | None = None
    ) -> list[User] | User | None:
        """Get user(s) with accounts eagerly loaded.

        Args:
            user_id: Optional user ID. If None, returns all non-deleted users.

        Returns:
            User instance if user_id provided, list of users otherwise.
            Returns None if user_id provided but user not found.
        """
        query = (
            select(User)
            .options(selectinload(User.accounts))
            .where(User.is_deleted.is_(False))
        )

        if user_id is not None:
            query = query.where(User.id == user_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()

        result = await self.session.execute(query)
        return list(result.scalars().all())

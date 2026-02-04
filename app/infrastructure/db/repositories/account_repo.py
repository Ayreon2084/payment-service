"""Account repository for database operations on Account model."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.account_model import Account
from app.infrastructure.db.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """Repository for Account model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(model=Account, session=session)

    async def get_by_user_id(self, user_id: int) -> list[Account]:
        """Get all non-deleted accounts for a user.

        Args:
            user_id: ID of the user.

        Returns:
            List of Account instances for the user.
        """
        query = select(Account).where(
            Account.user_id == user_id, Account.is_deleted.is_(False)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, account_id: int) -> Account | None:
        """Get non-deleted account by ID.

        Args:
            account_id: ID of the account.

        Returns:
            Account instance if found and not deleted, None otherwise.
        """
        query = select(Account).where(
            Account.id == account_id, Account.is_deleted.is_(False)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

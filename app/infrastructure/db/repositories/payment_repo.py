"""Payment repository for database operations on Payment model."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.payment_model import Payment
from app.infrastructure.db.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Repository for Payment model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(model=Payment, session=session)

    async def get_by_user_id(self, user_id: int) -> list[Payment]:
        """Get all payments for a user.

        Args:
            user_id: ID of the user.

        Returns:
            List of Payment instances for the user.
        """
        query = select(Payment).where(Payment.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_transaction_id(self, transaction_id: str) -> Payment | None:
        """Get payment by transaction ID.

        Args:
            transaction_id: Unique transaction identifier.

        Returns:
            Payment instance if found, None otherwise.
        """
        query = select(Payment).where(Payment.transaction_id == transaction_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

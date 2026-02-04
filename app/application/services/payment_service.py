"""Payment service for business logic related to payment processing."""
from sqlalchemy.exc import IntegrityError

from app.core.enums import CurrencyEnum, PaymentStatus
from app.infrastructure.db.models import Account, Payment
from app.infrastructure.strategies.mock_webhook_strategy import MockWebhookStrategy
from app.schemas.payment import WebhookData


class PaymentService:
    """Service for payment processing operations."""

    def __init__(self, session, payment_repo, account_repo, user_repo):
        self.session = session
        self.payment_repo = payment_repo
        self.account_repo = account_repo
        self.user_repo = user_repo
        self.strategy = MockWebhookStrategy()

    async def get_user_payments(self, user_id: int) -> list[Payment]:
        """Get all payments for a user.

        Args:
            user_id: ID of the user.

        Returns:
            List of Payment instances for the user.
        """
        return await self.payment_repo.get_by_user_id(user_id)

    async def process_webhook(self, data: WebhookData):
        """Process payment webhook from external payment system.

        Args:
            data: Webhook data with transaction information.

        Returns:
            Payment instance or status message if already processed.

        Raises:
            ValueError: If signature is invalid, user doesn't exist,
                        account doesn't belong to the user,
                        or transaction processing fails.
        """
        if not self.strategy.verify_signature(data):
            raise ValueError("Invalid signature")

        user = await self.user_repo.get_by_id(data.user_id)
        if not user:
            raise ValueError("User does not exist")

        existing_payment = await self.payment_repo.get_by_transaction_id(
            data.transaction_id
        )
        if existing_payment and existing_payment.status == PaymentStatus.SUCCESS:
            return {"status": "success", "message": "Already processed"}

        try:
            account = await self.account_repo.get_by_id(data.account_id)
            if account:
                if account.user_id != data.user_id:
                    raise ValueError("Account does not belong to the user")
            else:
                account = Account(
                    user_id=data.user_id, balance=0, currency=CurrencyEnum.USD.value
                )
                await self.account_repo.create(account)
                await self.session.flush()

            amount_in_minor_unit = int(data.amount)
            account.balance += amount_in_minor_unit

            payment = Payment(
                transaction_id=data.transaction_id,
                account_id=account.id,
                user_id=data.user_id,
                amount=amount_in_minor_unit,
                status=PaymentStatus.SUCCESS,
            )
            await self.payment_repo.create(payment)
            await self.session.commit()
            await self.session.refresh(payment)
            return payment

        except IntegrityError as e:
            await self.session.rollback()
            existing = await self.payment_repo.get_by_transaction_id(
                data.transaction_id
            )
            if existing and existing.status == PaymentStatus.SUCCESS:
                return {"status": "success", "message": "Already processed"}
            raise ValueError("Transaction processing failed") from e

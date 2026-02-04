"""Webhook signature verification strategy."""
import hashlib

from app.core.config import settings
from app.schemas.payment import WebhookData


class MockWebhookStrategy:
    """Strategy for verifying webhook signatures from payment system."""

    def verify_signature(self, data: WebhookData) -> bool:
        """Verify webhook signature.

        Args:
            data: Webhook data with signature to verify.

        Returns:
            True if signature is valid, False otherwise.
        """
        secret_key = settings.payment_secret_key.get_secret_value()
        raw_str = f"{data.account_id}{int(data.amount)}{data.transaction_id}{data.user_id}{secret_key}"
        expected_sig = hashlib.sha256(raw_str.encode()).hexdigest()
        return data.signature == expected_sig

    def generate_signature(
        self, account_id: int, amount: int, transaction_id: str, user_id: int
    ) -> str:
        """Generate webhook signature for testing.

        Args:
            account_id: Account ID.
            amount: Payment amount in minor currency units.
            transaction_id: Transaction identifier.
            user_id: User ID.

        Returns:
            SHA256 hash signature string.
        """
        secret_key = settings.payment_secret_key.get_secret_value()
        raw_str = f"{account_id}{amount}{transaction_id}{user_id}{secret_key}"
        return hashlib.sha256(raw_str.encode()).hexdigest()

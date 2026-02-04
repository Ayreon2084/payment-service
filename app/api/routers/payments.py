"""Payment router endpoints for payment processing."""
from decimal import Decimal

from fastapi import APIRouter, HTTPException

from app.api.deps import PaymentServiceDep
from app.core.config import settings
from app.infrastructure.strategies.mock_webhook_strategy import MockWebhookStrategy
from app.schemas.payment import WebhookData

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/webhook")
async def payment_webhook(data: WebhookData, payment_service: PaymentServiceDep):
    """Process payment webhook from external payment system.

    Args:
        data: Webhook data with transaction information and signature.
        payment_service: Payment service dependency.

    Returns:
        Payment instance or status message.

    Raises:
        HTTPException: If webhook processing fails.
    """
    try:
        return await payment_service.process_webhook(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-test-signature", include_in_schema=settings.debug)
async def generate_test_sig(
    account_id: int, amount: Decimal, transaction_id: str, user_id: int
):
    """
    Endpoint made for reviewer purposes only.
    Allows to generate valid signature for webhook testing.
    """
    strategy = MockWebhookStrategy()
    sig = strategy.generate_signature(
        account_id, int(amount), transaction_id, user_id
    )
    return {"signature": sig}

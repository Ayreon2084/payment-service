from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.core.enums import PaymentStatus


class PaymentBase(BaseModel):
    """
    Base schema for payment data with shared attributes.
    """
    amount: int = Field(
        gt=0,
        description="Amount in cents/eurocents/smallest units etc"
    )
    account_id: int


class PaymentCreate(PaymentBase):
    """
    Schema for creating a new payment. 
    Status is set by the system.
    """
    pass


class PaymentRead(PaymentBase):
    """Full representation of a payment record."""
    id: int
    transaction_id: str
    user_id: int
    status: PaymentStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentUpdate(BaseModel):
    """
    Schema for updating payment status 
    (e.g., by a payment gateway callback).
    """
    status: PaymentStatus

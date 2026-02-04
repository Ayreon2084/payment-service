from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.core.enums import CurrencyEnum


class AccountBase(BaseModel):
    """Base schema for account data with shared attributes."""

    currency: CurrencyEnum


class AccountCreate(AccountBase):
    """Schema for creating a new account."""

    pass


class AccountRead(AccountBase):
    """Schema for reading account data in API responses."""

    id: int
    balance: int = Field(ge=0, description="Balance in the minor currency unit")
    user_id: int
    created_at: datetime

    @computed_field
    @property
    def balance_in_major_currency_unit(self) -> float:
        return self.balance / 100

    model_config = ConfigDict(from_attributes=True)


class AccountUpdate(BaseModel):
    """
    Schema for account updates.
    Direct balance and currency updates are prohibited.
    Included here primarily for administrative status changes if needed.
    """

    is_deleted: bool | None = None

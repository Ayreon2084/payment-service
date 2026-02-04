from enum import Enum


class CurrencyEnum(str, Enum):
    """Supported currency types for accounts."""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    RUB = "RUB"
    CNY = "CNY"
    CHF = "CHF"


class PaymentStatus(str, Enum):
    """Payment transaction status values."""

    PENDING = "pending"
    SUCCESS = "success"
    FAIL = "fail"

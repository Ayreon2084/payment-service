from enum import Enum


class CurrencyEnum(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    RUB = "RUB"
    CNY = "CNY"
    CHF = "CHF"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAIL = "fail"

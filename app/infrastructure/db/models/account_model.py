"""Account model for database representation."""
from sqlalchemy import CheckConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import CurrencyEnum
from app.infrastructure.db.database import Base
from app.infrastructure.db.mixins import LifecycleWithDeleteMixin


class Account(LifecycleWithDeleteMixin, Base):
    """Account model representing user's payment account."""

    balance: Mapped[int] = mapped_column(Integer, default=0)
    currency: Mapped[CurrencyEnum] = mapped_column(
        SQLEnum(
            CurrencyEnum,
            name="currency_type",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
        default=CurrencyEnum.USD,
        server_default=CurrencyEnum.USD.value,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="accounts")
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="account"
    )

    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_balance_non_negative"),
    )

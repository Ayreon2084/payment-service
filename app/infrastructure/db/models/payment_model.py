from sqlalchemy import String, ForeignKey, BigInteger
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PaymentStatus
from app.infrastructure.db.database import Base
from app.infrastructure.db.mixins import LifecycleMixin


class Payment(LifecycleMixin, Base):
    transaction_id: Mapped[str] = mapped_column(
        String(255), 
        unique=True,   
        index=True,
        nullable=False
    )
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus, name="payment_status"),
        nullable=False,
        default=PaymentStatus.PENDING,
        server_default=PaymentStatus.PENDING.value
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="payments"
    )

    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id"),
        nullable=False
    )
    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="payments"
    )

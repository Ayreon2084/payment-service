"""User model for database representation."""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.database import Base
from app.infrastructure.db.mixins import LifecycleWithDeleteMixin


class User(LifecycleWithDeleteMixin, Base):
    """User model representing application user."""

    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(100))
    is_admin: Mapped[bool] = mapped_column(default=False)

    accounts: Mapped[list["Account"]] = relationship("Account", back_populates="user")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="user")

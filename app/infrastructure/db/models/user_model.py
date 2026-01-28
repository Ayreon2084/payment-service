from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from app.infrastructure.db.database import Base
from infrastructure.db.mixins import LifecycleMixin


class User(LifecycleMixin, Base):
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False)
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    full_name: Mapped[str | None] = mapped_column(String(100))
    is_admin: Mapped[bool] = mapped_column(default=False)

    accounts: Mapped[list["Account"]]  = relationship(
        "Account",
        back_populates="user"
    )

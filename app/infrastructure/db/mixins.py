from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, func


class LifecycleMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

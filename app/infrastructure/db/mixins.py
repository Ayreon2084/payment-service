"""SQLAlchemy mixins for common model fields."""
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class LifecycleMixin:
    """Mixin adding created_at timestamp to models."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class LifecycleWithDeleteMixin(LifecycleMixin):
    """
    Mixin adding soft delete functionality to models.

    Extends LifecycleMixin with is_deleted flag and deleted_at timestamp.
    """

    is_deleted: Mapped[bool] = mapped_column(default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

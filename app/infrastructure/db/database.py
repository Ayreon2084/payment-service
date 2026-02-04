"""Database configuration and base model."""
import re
from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Automatically generates table names from class names by converting
    CamelCase to snake_case and adding 's' suffix.
    """


    @declared_attr
    def __tablename__(cls) -> Any:
        """Generate table name from class name.

        Converts CamelCase to snake_case and adds 's' suffix.
        Example: User -> users, PaymentAccount -> payment_accounts

        Returns:
            Table name string.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower() + "s"

    id: Mapped[int] = mapped_column(primary_key=True)


engine = create_async_engine(settings.database_url, echo=settings.debug)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    """FastAPI dependency for database session.

    Yields:
        Async database session instance.
    """
    async with AsyncSessionLocal() as async_session:
        yield async_session

import re

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase, Mapped,
    mapped_column, declared_attr,
    async_sessionmaker
)

from app.core.config import settings


class Base(DeclarativeBase):

    @declared_attr
    def __tablename__(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower() + "s"
    
    id: Mapped[int] = mapped_column(primary_key=True)


engine = create_async_engine(settings.database_url, echo=settings.debug)

AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False
)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session

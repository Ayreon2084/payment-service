"""Base repository with common CRUD operations."""
from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository providing common database operations."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, obj_id: int) -> ModelType | None:
        """Fetch a single record by its primary key."""
        return await self.session.get(self.model, obj_id)

    async def list_(self) -> Sequence[ModelType]:
        """Fetch all records of this model."""
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, obj: ModelType) -> ModelType:
        """Add a new record to the session."""
        self.session.add(obj)
        return obj

    async def update(self, obj_id: Any, **kwargs) -> ModelType | None:
        """
        Update specific fields of a record using the criteria.
        Returns the updated object or None if not found.
        """
        query = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, obj_id: Any) -> bool:
        """Hard delete a record from the database."""
        query = delete(self.model).where(self.model.id == obj_id)
        result = await self.session.execute(query)
        return result.rowcount > 0

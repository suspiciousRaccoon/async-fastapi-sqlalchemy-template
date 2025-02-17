from abc import ABC
from typing import Generic, Mapping, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.database.core import Base

SAModel = TypeVar("SAModel", bound=Base)


class BaseRepository(ABC, Generic[SAModel]):
    model: type[SAModel]

    def __init__(self, session: AsyncSession):
        """
        Base Repository class with database CRUD methods

        Usage:
        class YourModelRepository(BaseRepository[YourModel]):
            model = YourModel


        """
        self.session = session

    def _validate_keys(self, kwargs: Mapping[str, object]) -> None:
        valid_keys = {attr.key for attr in self.model.__table__.columns}
        invalid_keys = [key for key in kwargs.keys() if key not in valid_keys]

        if invalid_keys:
            raise AttributeError(
                f"Invalid attribute(s) for {self.model.__name__}: {', '.join(invalid_keys)}"
            )

    async def get(self, model_id: int | None) -> SAModel | None:
        statement = select(self.model)

        if model_id is not None:
            statement = statement.where(self.model.id == model_id)

        result = await self.session.scalars(statement)

        return result.first()

    async def get_all(self) -> Sequence[SAModel]:
        statement = select(self.model)

        result = await self.session.scalars(statement)

        return result.all()

    async def get_by_attributes(self, **kwargs: object) -> SAModel | None:
        self._validate_keys(kwargs)

        statement = select(self.model)

        for attribute_key in kwargs:
            model_attribute = getattr(self.model, attribute_key)
            statement = statement.where(model_attribute == kwargs[attribute_key])

        result = await self.session.scalars(statement)

        return result.first()

    async def get_all_by_attributes(
        self, **kwargs: Mapping[str, object]
    ) -> Sequence[SAModel]:
        self._validate_keys(kwargs)

        statement = select(self.model)
        for attribute_key in kwargs:
            model_attribute = getattr(self.model, attribute_key)
            statement = statement.where(model_attribute == kwargs[attribute_key])

        result = await self.session.scalars(statement)
        return result.all()

    async def create(self, data: Mapping[str, object]) -> SAModel:
        try:
            new_instance = self.model(**data)
        except TypeError as e:
            raise ValueError(f"Invalid fields for model {self.model.__name__}: {e}")

        self.session.add(new_instance)

        await self.session.commit()
        await self.session.refresh(new_instance)

        return new_instance

    async def update(self, model_id: int, data: Mapping[str, object]) -> SAModel:
        if not data:
            raise ValueError("No data provided for update.")

        self._validate_keys(data)

        statement = (
            select(self.model).where(self.model.id == model_id).with_for_update()
        )
        result = await self.session.scalars(statement)
        instance = result.first()

        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
            await self.session.commit()
            await self.session.refresh(instance)
            return instance
        else:
            raise ValueError(f"Instance with id {model_id} not found")

    async def update_instance(
        self, instance: SAModel, data: Mapping[str, object]
    ) -> SAModel:
        """Updates an existing instance without querying it again.

        Args:
            instance (SAModel): The existing instance to be updated.
            data (Mapping[str, object]): The fields to update.

        Returns:
            SAModel: The updated instance.
        """
        if not data:
            raise ValueError("No data provided for update.")

        self._validate_keys(data)

        for key, value in data.items():
            setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, model_id: int) -> None:
        statement = select(self.model).where(self.model.id == model_id)
        result = await self.session.scalars(statement)

        instance = result.first()

        if instance:
            await self.session.delete(instance)

            await self.session.commit()
        else:
            raise ValueError(f"Instance with id {model_id} not found")

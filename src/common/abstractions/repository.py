from abc import ABC
from typing import AsyncGenerator, Generic, Sequence, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .dto import BaseDTOModel
from .model import BaseDBModel

DBModel = TypeVar("DBModel", bound=BaseDBModel)
CreateDTO = TypeVar("CreateDTO", bound=BaseDTOModel)
UpdateDTO = TypeVar("UpdateDTO", bound=BaseDTOModel)
GetDTO = TypeVar("GetDTO", bound=BaseDTOModel)


class BaseRepository(ABC, Generic[DBModel, CreateDTO, UpdateDTO, GetDTO]):
    def __init__(self, model: type[DBModel], session: AsyncSession):
        self.model: type[DBModel] = model
        self._session: AsyncSession = session

    async def find_one(self, **kwargs) -> DBModel:
        return (
            await self._session.execute(select(self.model).filter_by(**kwargs))
        ).scalar_one()

    async def find_one_or_none(self, **kwargs) -> DBModel | None:
        return (
            await self._session.execute(select(self.model).filter_by(**kwargs))
        ).scalar_one_or_none()

    async def find_all(self, **kwargs) -> AsyncGenerator[DBModel, None]:
        models: Sequence[DBModel] = (
            (await self._session.execute(select().filter_by(**kwargs))).scalars().all()
        )

        for model in models:
            yield model

    async def insert_one(self, create_dto: CreateDTO) -> DBModel:
        return (
            await self._session.execute(
                insert(self.model).values(create_dto.model_dump()).returning(self.model)
            )
        ).scalar_one()

    async def insert_many(
        self, create_dtos: list[CreateDTO]
    ) -> AsyncGenerator[DBModel, None]:
        models: Sequence[DBModel] = (
            (
                await self._session.execute(
                    insert(self.model)
                    .values([dto.model_dump() for dto in create_dtos])
                    .returning(self.model)
                )
            )
            .scalars()
            .all()
        )

        for model in models:
            yield model

    async def update_one(self, update_dto: UpdateDTO, **kwargs) -> DBModel:
        return (
            await self._session.execute(
                update(self.model)
                .where(**kwargs)
                .values(update_dto.model_dump())
                .returning(self.model)
            )
        ).scalar_one()

    async def update_many(
        self, update_dtos: list[UpdateDTO], **kwargs
    ) -> AsyncGenerator[DBModel, None]:
        models: Sequence[DBModel] = (
            (
                await self._session.execute(
                    update(self.model)
                    .filter_by(**kwargs)
                    .values([dto.model_dump() for dto in update_dtos])
                    .returning(self.model)
                )
            )
            .scalars()
            .all()
        )

        for model in models:
            yield model

    async def delete(self, **kwargs) -> None:
        await self._session.execute(delete(self.model).filter_by(**kwargs))

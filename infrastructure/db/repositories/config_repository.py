"""
Config Repository의 PostgreSQL 구현체.
set()은 key 기준 upsert로 처리하여 중복 키 에러를 방지한다.
"""

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.config_repository import ConfigRepository
from infrastructure.db.models import Config as ConfigModel


class PostgresConfigRepository(ConfigRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, key: str) -> str | None:
        result = await self._session.execute(
            select(ConfigModel).where(ConfigModel.key == key)
        )
        row = result.scalar_one_or_none()
        return row.value if row else None

    async def set(self, key: str, value: str) -> None:
        """
        key 기준 upsert.
        신규 key면 INSERT, 기존 key면 value와 updated_at을 업데이트한다.
        """
        from sqlalchemy import func

        stmt = (
            insert(ConfigModel)
            .values(key=key, value=value)
            .on_conflict_do_update(
                index_elements=["key"],
                set_={"value": value, "updated_at": func.now()},
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()

    async def get_all(self) -> dict[str, str]:
        result = await self._session.execute(select(ConfigModel))
        return {row.key: row.value for row in result.scalars().all()}

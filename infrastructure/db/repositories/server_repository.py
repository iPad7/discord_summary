"""
Server, Channel Repository의 PostgreSQL 구현체.
discord_id를 PK로 사용하므로 save()는 upsert로 처리한다.
"""

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.server import Channel, Server
from domain.repositories.server_repository import ChannelRepository, ServerRepository
from infrastructure.db.mapper import (
    channel_to_entity,
    channel_to_model,
    server_to_entity,
    server_to_model,
)
from infrastructure.db.models import Channel as ChannelModel
from infrastructure.db.models import Server as ServerModel


class PostgresServerRepository(ServerRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, server: Server) -> Server:
        """
        discord_id 기준 upsert.
        신규면 INSERT, 기존이면 name/is_active 업데이트한다.
        """
        stmt = (
            insert(ServerModel)
            .values(
                discord_id=server.discord_id,
                name=server.name,
                is_active=server.is_active,
                created_at=server.created_at,
            )
            .on_conflict_do_update(
                index_elements=["discord_id"],
                set_={"name": server.name, "is_active": server.is_active},
            )
            .returning(ServerModel)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return server_to_entity(result.scalar_one())

    async def get_by_discord_id(self, discord_id: int) -> Server | None:
        result = await self._session.execute(
            select(ServerModel).where(ServerModel.discord_id == discord_id)
        )
        row = result.scalar_one_or_none()
        return server_to_entity(row) if row else None

    async def get_all_active(self) -> list[Server]:
        result = await self._session.execute(
            select(ServerModel).where(ServerModel.is_active == True)
        )
        return [server_to_entity(r) for r in result.scalars().all()]


class PostgresChannelRepository(ChannelRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, channel: Channel) -> Channel:
        """
        discord_id 기준 upsert.
        신규면 INSERT, 기존이면 name/is_watched 업데이트한다.
        """
        stmt = (
            insert(ChannelModel)
            .values(
                discord_id=channel.discord_id,
                server_id=channel.server_id,
                name=channel.name,
                is_watched=channel.is_watched,
                created_at=channel.created_at,
            )
            .on_conflict_do_update(
                index_elements=["discord_id"],
                set_={"name": channel.name, "is_watched": channel.is_watched},
            )
            .returning(ChannelModel)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return channel_to_entity(result.scalar_one())

    async def get_by_discord_id(self, discord_id: int) -> Channel | None:
        result = await self._session.execute(
            select(ChannelModel).where(ChannelModel.discord_id == discord_id)
        )
        row = result.scalar_one_or_none()
        return channel_to_entity(row) if row else None

    async def get_watched(self) -> list[Channel]:
        result = await self._session.execute(
            select(ChannelModel).where(ChannelModel.is_watched == True)
        )
        return [channel_to_entity(r) for r in result.scalars().all()]

    async def update_watched(self, discord_id: int, is_watched: bool) -> None:
        await self._session.execute(
            update(ChannelModel)
            .where(ChannelModel.discord_id == discord_id)
            .values(is_watched=is_watched)
        )
        await self._session.commit()

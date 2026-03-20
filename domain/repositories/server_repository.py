from abc import ABC, abstractmethod

from domain.entities.server import Server, Channel


class ServerRepository(ABC):
    @abstractmethod
    async def save(self, server: Server) -> Server: ...

    @abstractmethod
    async def get_by_discord_id(self, discord_id: int) -> Server | None: ...

    @abstractmethod
    async def get_all_active(self) -> list[Server]: ...


class ChannelRepository(ABC):
    @abstractmethod
    async def save(self, channel: Channel) -> Channel: ...

    @abstractmethod
    async def get_by_discord_id(self, discord_id: int) -> Channel | None: ...

    @abstractmethod
    async def get_watched(self) -> list[Channel]: ...

    @abstractmethod
    async def update_watched(self, discord_id: int, is_watched: bool) -> None: ...

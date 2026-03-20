from abc import ABC, abstractmethod

from domain.entities.server import Server, Channel


class ServerRepository(ABC):

    @abstractmethod
    async def save(self, server: Server) -> Server:
        """
        서버 정보를 저장한다.
        신규 서버 감시 등록 시 호출된다.
        이미 존재하는 discord_id면 업데이트, 없으면 INSERT한다.
        """
        ...

    @abstractmethod
    async def get_by_discord_id(self, discord_id: int) -> Server | None:
        """
        Discord 서버 ID로 서버를 조회한다.
        봇이 메시지 수신 시 해당 서버가 감시 대상인지 확인할 때 호출된다.
        존재하지 않으면 None을 반환한다.
        """
        ...

    @abstractmethod
    async def get_all_active(self) -> list[Server]:
        """
        현재 감시 중인 모든 서버 목록을 반환한다.
        봇 시작 시 감시 대상 서버 목록을 초기화할 때 호출된다.
        """
        ...


class ChannelRepository(ABC):

    @abstractmethod
    async def save(self, channel: Channel) -> Channel:
        """
        채널 정보를 저장한다.
        신규 채널 감시 등록 또는 채널 정보 갱신 시 호출된다.
        이미 존재하는 discord_id면 업데이트, 없으면 INSERT한다.
        """
        ...

    @abstractmethod
    async def get_by_discord_id(self, discord_id: int) -> Channel | None:
        """
        Discord 채널 ID로 채널을 조회한다.
        봇이 메시지 수신 시 해당 채널이 감시 대상인지 확인할 때 호출된다.
        존재하지 않으면 None을 반환한다.
        """
        ...

    @abstractmethod
    async def get_watched(self) -> list[Channel]:
        """
        현재 감시 중인 모든 채널 목록을 반환한다.
        봇 시작 시 감시 대상 채널 목록을 초기화할 때 호출된다.
        """
        ...

    @abstractmethod
    async def update_watched(self, discord_id: int, is_watched: bool) -> None:
        """
        채널의 감시 여부를 변경한다.
        대시보드에서 채널 감시 ON/OFF 설정 시 호출된다.
        """
        ...

from abc import ABC, abstractmethod


class ConfigRepository(ABC):

    @abstractmethod
    async def get(self, key: str) -> str | None:
        """
        설정 키에 해당하는 값을 조회한다.
        봇 또는 API에서 특정 설정값을 읽을 때 호출된다.
        존재하지 않는 키면 None을 반환한다.
        """
        ...

    @abstractmethod
    async def set(self, key: str, value: str) -> None:
        """
        설정 키-값 쌍을 저장한다.
        대시보드에서 설정 변경 시 호출된다.
        이미 존재하는 키면 값을 업데이트(upsert)한다.
        """
        ...

    @abstractmethod
    async def get_all(self) -> dict[str, str]:
        """
        모든 설정 키-값 쌍을 딕셔너리로 반환한다.
        대시보드 설정 페이지 초기 로드 시 전체 설정을 한 번에 가져올 때 호출된다.
        """
        ...

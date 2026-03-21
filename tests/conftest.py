import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from infrastructure.db.database import Base

TEST_DB_URL = "postgresql+asyncpg://discord_summary:password@localhost:5432/discord_summary_test"

_engine = create_async_engine(TEST_DB_URL)
_SessionFactory = async_sessionmaker(
    bind=_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
async def setup_tables():
    """테스트 세션 시작 시 테이블 생성, 종료 시 전체 삭제."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session():
    """테스트마다 독립된 DB 세션 제공."""
    async with _SessionFactory() as s:
        yield s


@pytest.fixture(autouse=True)
async def clean_tables():
    """각 테스트 후 모든 테이블 데이터 초기화. 테스트 세션과 별도 커넥션 사용."""
    yield
    async with _engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE TABLE configs, alerts, feedbacks, ai_logs,"
                " message_batches, messages, channels, servers"
                " RESTART IDENTITY CASCADE"
            )
        )

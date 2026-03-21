import pytest

from infrastructure.db.repositories.config_repository import PostgresConfigRepository


@pytest.fixture
def repo(session):
    return PostgresConfigRepository(session)


async def test_get_missing_key_returns_none(repo):
    result = await repo.get("nonexistent")
    assert result is None


async def test_set_and_get(repo):
    await repo.set("theme", "dark")
    result = await repo.get("theme")
    assert result == "dark"


async def test_set_upsert_overwrites_value(repo):
    await repo.set("lang", "ko")
    await repo.set("lang", "en")
    result = await repo.get("lang")
    assert result == "en"


async def test_get_all_empty(repo):
    result = await repo.get_all()
    assert result == {}


async def test_get_all_returns_all_pairs(repo):
    await repo.set("a", "1")
    await repo.set("b", "2")
    result = await repo.get_all()
    assert result == {"a": "1", "b": "2"}

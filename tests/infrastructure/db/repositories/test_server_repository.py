import pytest

from domain.entities.server import Channel, Server
from infrastructure.db.repositories.server_repository import (
    PostgresChannelRepository,
    PostgresServerRepository,
)


@pytest.fixture
def server_repo(session):
    return PostgresServerRepository(session)


@pytest.fixture
def channel_repo(session):
    return PostgresChannelRepository(session)


@pytest.fixture
async def saved_server(server_repo):
    """채널 테스트에서 FK 충족용 기본 서버."""
    return await server_repo.save(Server(discord_id=1, name="Base Server"))


# ── ServerRepository ─────────────────────────────────────────────────────────

async def test_server_save_returns_correct_values(server_repo):
    server = await server_repo.save(Server(discord_id=100, name="My Server", is_active=True))
    assert server.discord_id == 100
    assert server.name == "My Server"
    assert server.is_active is True


async def test_server_upsert_updates_name(server_repo):
    await server_repo.save(Server(discord_id=100, name="Old Name"))
    updated = await server_repo.save(Server(discord_id=100, name="New Name"))
    assert updated.name == "New Name"


async def test_server_upsert_updates_is_active(server_repo):
    await server_repo.save(Server(discord_id=100, name="S", is_active=True))
    updated = await server_repo.save(Server(discord_id=100, name="S", is_active=False))
    assert updated.is_active is False


async def test_server_get_by_discord_id_not_found(server_repo):
    result = await server_repo.get_by_discord_id(99999)
    assert result is None


async def test_server_get_all_active_excludes_inactive(server_repo):
    await server_repo.save(Server(discord_id=1, name="Active", is_active=True))
    await server_repo.save(Server(discord_id=2, name="Inactive", is_active=False))
    result = await server_repo.get_all_active()
    ids = [s.discord_id for s in result]
    assert 1 in ids
    assert 2 not in ids


# ── ChannelRepository ────────────────────────────────────────────────────────

async def test_channel_save_returns_correct_values(channel_repo, saved_server):
    channel = await channel_repo.save(Channel(discord_id=200, server_id=1, name="general", is_watched=False))
    assert channel.discord_id == 200
    assert channel.name == "general"
    assert channel.is_watched is False


async def test_channel_upsert_updates_name(channel_repo, saved_server):
    await channel_repo.save(Channel(discord_id=200, server_id=1, name="old"))
    updated = await channel_repo.save(Channel(discord_id=200, server_id=1, name="new"))
    assert updated.name == "new"


async def test_channel_get_by_discord_id_not_found(channel_repo):
    result = await channel_repo.get_by_discord_id(99999)
    assert result is None


async def test_channel_get_watched_excludes_unwatched(channel_repo, saved_server):
    await channel_repo.save(Channel(discord_id=201, server_id=1, name="watched", is_watched=True))
    await channel_repo.save(Channel(discord_id=202, server_id=1, name="silent", is_watched=False))
    result = await channel_repo.get_watched()
    ids = [c.discord_id for c in result]
    assert 201 in ids
    assert 202 not in ids


async def test_channel_update_watched(channel_repo, saved_server):
    await channel_repo.save(Channel(discord_id=200, server_id=1, name="general", is_watched=False))
    await channel_repo.update_watched(200, True)
    channel = await channel_repo.get_by_discord_id(200)
    assert channel.is_watched is True

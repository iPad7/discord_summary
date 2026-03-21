from datetime import datetime, timedelta, timezone

import pytest

from domain.entities.ai_log import AILog
from domain.entities.alert import Alert
from domain.entities.message import Message, MessageBatch
from domain.entities.server import Channel, Server
from infrastructure.db.repositories.ai_log_repository import PostgresAILogRepository
from infrastructure.db.repositories.alert_repository import PostgresAlertRepository
from infrastructure.db.repositories.message_repository import (
    PostgresMessageBatchRepository,
    PostgresMessageRepository,
)
from infrastructure.db.repositories.server_repository import (
    PostgresChannelRepository,
    PostgresServerRepository,
)

NOW = datetime.now(timezone.utc)


@pytest.fixture
async def chain(session):
    """
    Alert 저장에 필요한 전체 선행 데이터를 구성한다.
    Server → Channel → Message → MessageBatch → AILog 순으로 생성하고
    각 ID를 dict로 반환한다.
    """
    server = await PostgresServerRepository(session).save(
        Server(discord_id=1, name="S")
    )
    channel = await PostgresChannelRepository(session).save(
        Channel(discord_id=10, server_id=server.discord_id, name="general")
    )
    message = await PostgresMessageRepository(session).save(
        Message(discord_msg_id=999, channel_id=channel.discord_id, author_id=1, author_name="U", content="hi")
    )
    batch = await PostgresMessageBatchRepository(session).save(
        MessageBatch(trigger_msg_id=message.id, context_msg_ids=[message.id], context_text="hi")
    )
    ai_log = await PostgresAILogRepository(session).save(
        AILog(batch_id=batch.id, answer=True, reason="test", latency_ms=100)
    )
    return {"channel_id": channel.discord_id, "ai_log_id": ai_log.id}


@pytest.fixture
def alert_repo(session):
    return PostgresAlertRepository(session)


async def test_alert_save_assigns_id(alert_repo, chain):
    alert = await alert_repo.save(Alert(ai_log_id=chain["ai_log_id"], sent_at=NOW))
    assert alert.id is not None


async def test_exists_recent_returns_true(alert_repo, chain):
    await alert_repo.save(Alert(ai_log_id=chain["ai_log_id"], sent_at=NOW))
    since = NOW - timedelta(minutes=30)
    result = await alert_repo.exists_recent_by_channel(chain["channel_id"], since)
    assert result is True


async def test_exists_recent_returns_false_when_alert_is_old(alert_repo, chain):
    old_time = NOW - timedelta(hours=2)
    await alert_repo.save(Alert(ai_log_id=chain["ai_log_id"], sent_at=old_time))
    since = NOW - timedelta(minutes=30)
    result = await alert_repo.exists_recent_by_channel(chain["channel_id"], since)
    assert result is False


async def test_exists_recent_returns_false_for_different_channel(alert_repo, chain, session):
    # channel_id=10 의 Alert를 저장하고 channel_id=99 로 조회하면 False여야 함
    await alert_repo.save(Alert(ai_log_id=chain["ai_log_id"], sent_at=NOW))
    since = NOW - timedelta(minutes=30)
    result = await alert_repo.exists_recent_by_channel(99, since)
    assert result is False

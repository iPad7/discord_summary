from datetime import datetime

from domain.entities.ai_log import AILog
from domain.entities.alert import Alert
from domain.entities.feedback import Feedback
from domain.entities.message import Message, MessageBatch
from domain.entities.server import Channel, Server
from infrastructure.db.mapper import (
    ai_log_to_entity,
    ai_log_to_model,
    alert_to_entity,
    alert_to_model,
    batch_to_entity,
    batch_to_model,
    channel_to_entity,
    channel_to_model,
    feedback_to_entity,
    feedback_to_model,
    message_to_entity,
    message_to_model,
    server_to_entity,
    server_to_model,
)

NOW = datetime(2026, 1, 1, 12, 0, 0)


# ── Message ─────────────────────────────────────────────────────────────────

def test_message_to_model_excludes_id():
    entity = Message(discord_msg_id=111, channel_id=1, author_id=9, author_name="A", content="hi", created_at=NOW)
    model = message_to_model(entity)
    assert model.id is None


def test_message_roundtrip():
    entity = Message(id=5, discord_msg_id=111, channel_id=1, author_id=9, author_name="Alice", content="hello", created_at=NOW)
    from infrastructure.db.models import Message as M
    model = M(id=5, discord_msg_id=111, channel_id=1, author_id=9, author_name="Alice", content="hello", created_at=NOW)
    result = message_to_entity(model)
    assert result.id == entity.id
    assert result.discord_msg_id == entity.discord_msg_id
    assert result.channel_id == entity.channel_id
    assert result.author_id == entity.author_id
    assert result.author_name == entity.author_name
    assert result.content == entity.content
    assert result.created_at == entity.created_at


# ── MessageBatch ─────────────────────────────────────────────────────────────

def test_batch_to_model_excludes_id():
    entity = MessageBatch(trigger_msg_id=1, context_msg_ids=[1, 2, 3], context_text="ctx", created_at=NOW)
    model = batch_to_model(entity)
    assert model.id is None


def test_batch_roundtrip():
    from infrastructure.db.models import MessageBatch as M
    model = M(id=7, trigger_msg_id=1, context_msg_ids=[1, 2, 3], context_text="ctx", created_at=NOW)
    result = batch_to_entity(model)
    assert result.id == 7
    assert result.trigger_msg_id == 1
    assert result.context_msg_ids == [1, 2, 3]
    assert result.context_text == "ctx"


# ── AILog ────────────────────────────────────────────────────────────────────

def test_ai_log_to_model_excludes_id():
    entity = AILog(batch_id=1, answer=True, reason="r", latency_ms=100, created_at=NOW)
    model = ai_log_to_model(entity)
    assert model.id is None


def test_ai_log_roundtrip():
    from infrastructure.db.models import AILog as M
    model = M(id=3, batch_id=1, answer=True, reason="because", latency_ms=200, created_at=NOW)
    result = ai_log_to_entity(model)
    assert result.id == 3
    assert result.answer is True
    assert result.reason == "because"
    assert result.latency_ms == 200


# ── Alert ────────────────────────────────────────────────────────────────────

def test_alert_to_model_excludes_id():
    entity = Alert(ai_log_id=1, sent_at=NOW)
    model = alert_to_model(entity)
    assert model.id is None


def test_alert_roundtrip():
    from infrastructure.db.models import Alert as M
    model = M(id=2, ai_log_id=1, sent_at=NOW)
    result = alert_to_entity(model)
    assert result.id == 2
    assert result.ai_log_id == 1
    assert result.sent_at == NOW


# ── Feedback ─────────────────────────────────────────────────────────────────

def test_feedback_to_model_excludes_id():
    entity = Feedback(ai_log_id=1, is_correct=True, note="good", created_at=NOW)
    model = feedback_to_model(entity)
    assert model.id is None


def test_feedback_roundtrip_with_note():
    from infrastructure.db.models import Feedback as M
    model = M(id=4, ai_log_id=1, is_correct=True, note="good job", created_at=NOW)
    result = feedback_to_entity(model)
    assert result.id == 4
    assert result.is_correct is True
    assert result.note == "good job"


def test_feedback_roundtrip_none_note():
    from infrastructure.db.models import Feedback as M
    model = M(id=4, ai_log_id=1, is_correct=False, note=None, created_at=NOW)
    result = feedback_to_entity(model)
    assert result.note is None


# ── Server ───────────────────────────────────────────────────────────────────

def test_server_roundtrip():
    from infrastructure.db.models import Server as M
    model = M(discord_id=100, name="Test Server", is_active=True, created_at=NOW)
    result = server_to_entity(model)
    assert result.discord_id == 100
    assert result.name == "Test Server"
    assert result.is_active is True


# ── Channel ──────────────────────────────────────────────────────────────────

def test_channel_roundtrip():
    from infrastructure.db.models import Channel as M
    model = M(discord_id=200, server_id=100, name="general", is_watched=False, created_at=NOW)
    result = channel_to_entity(model)
    assert result.discord_id == 200
    assert result.server_id == 100
    assert result.name == "general"
    assert result.is_watched is False

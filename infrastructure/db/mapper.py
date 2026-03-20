"""
domain 엔티티 ↔ SQLAlchemy 모델 간 변환 함수 모음.
infrastructure 레이어 내부에서만 사용한다.
"""

from domain.entities.ai_log import AILog
from domain.entities.alert import Alert
from domain.entities.feedback import Feedback
from domain.entities.message import Message, MessageBatch
from domain.entities.server import Channel, Server
from infrastructure.db.models import (
    AILog as AILogModel,
    Alert as AlertModel,
    Channel as ChannelModel,
    Feedback as FeedbackModel,
    Message as MessageModel,
    MessageBatch as MessageBatchModel,
    Server as ServerModel,
)


# ── Server ──────────────────────────────────────────────
def server_to_entity(model: ServerModel) -> Server:
    return Server(
        discord_id=model.discord_id,
        name=model.name,
        is_active=model.is_active,
        created_at=model.created_at,
    )


def server_to_model(entity: Server) -> ServerModel:
    return ServerModel(
        discord_id=entity.discord_id,
        name=entity.name,
        is_active=entity.is_active,
        created_at=entity.created_at,
    )


# ── Channel ─────────────────────────────────────────────
def channel_to_entity(model: ChannelModel) -> Channel:
    return Channel(
        discord_id=model.discord_id,
        server_id=model.server_id,
        name=model.name,
        is_watched=model.is_watched,
        created_at=model.created_at,
    )


def channel_to_model(entity: Channel) -> ChannelModel:
    return ChannelModel(
        discord_id=entity.discord_id,
        server_id=entity.server_id,
        name=entity.name,
        is_watched=entity.is_watched,
        created_at=entity.created_at,
    )


# ── Message ─────────────────────────────────────────────
def message_to_entity(model: MessageModel) -> Message:
    return Message(
        id=model.id,
        discord_msg_id=model.discord_msg_id,
        channel_id=model.channel_id,
        author_id=model.author_id,
        author_name=model.author_name,
        content=model.content,
        created_at=model.created_at,
    )


def message_to_model(entity: Message) -> MessageModel:
    return MessageModel(
        discord_msg_id=entity.discord_msg_id,
        channel_id=entity.channel_id,
        author_id=entity.author_id,
        author_name=entity.author_name,
        content=entity.content,
        created_at=entity.created_at,
    )


# ── MessageBatch ─────────────────────────────────────────
def batch_to_entity(model: MessageBatchModel) -> MessageBatch:
    return MessageBatch(
        id=model.id,
        trigger_msg_id=model.trigger_msg_id,
        context_msg_ids=model.context_msg_ids,
        context_text=model.context_text,
        created_at=model.created_at,
    )


def batch_to_model(entity: MessageBatch) -> MessageBatchModel:
    return MessageBatchModel(
        trigger_msg_id=entity.trigger_msg_id,
        context_msg_ids=entity.context_msg_ids,
        context_text=entity.context_text,
        created_at=entity.created_at,
    )


# ── AILog ────────────────────────────────────────────────
def ai_log_to_entity(model: AILogModel) -> AILog:
    return AILog(
        id=model.id,
        batch_id=model.batch_id,
        answer=model.answer,
        reason=model.reason,
        latency_ms=model.latency_ms,
        created_at=model.created_at,
    )


def ai_log_to_model(entity: AILog) -> AILogModel:
    return AILogModel(
        batch_id=entity.batch_id,
        answer=entity.answer,
        reason=entity.reason,
        latency_ms=entity.latency_ms,
        created_at=entity.created_at,
    )


# ── Alert ────────────────────────────────────────────────
def alert_to_entity(model: AlertModel) -> Alert:
    return Alert(
        id=model.id,
        ai_log_id=model.ai_log_id,
        sent_at=model.sent_at,
    )


def alert_to_model(entity: Alert) -> AlertModel:
    return AlertModel(
        ai_log_id=entity.ai_log_id,
        sent_at=entity.sent_at,
    )


# ── Feedback ─────────────────────────────────────────────
def feedback_to_entity(model: FeedbackModel) -> Feedback:
    return Feedback(
        id=model.id,
        ai_log_id=model.ai_log_id,
        is_correct=model.is_correct,
        note=model.note,
        created_at=model.created_at,
    )


def feedback_to_model(entity: Feedback) -> FeedbackModel:
    return FeedbackModel(
        ai_log_id=entity.ai_log_id,
        is_correct=entity.is_correct,
        note=entity.note,
        created_at=entity.created_at,
    )

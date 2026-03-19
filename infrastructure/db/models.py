from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    func,
    ARRAY,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.database import Base


class Server(Base):
    __tablename__ = "servers"

    discord_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    channels: Mapped[list["Channel"]] = relationship(back_populates="server")


class Channel(Base):
    __tablename__ = "channels"

    discord_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    server_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("servers.discord_id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    is_watched: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    server: Mapped["Server"] = relationship(back_populates="channels")
    messages: Mapped[list["Message"]] = relationship(back_populates="channel")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    discord_msg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    channel_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("channels.discord_id"), nullable=False
    )
    author_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    author_name: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    channel: Mapped["Channel"] = relationship(back_populates="messages")
    batches: Mapped[list["MessageBatch"]] = relationship(
        back_populates="trigger_message",
        foreign_keys="MessageBatch.trigger_msg_id",
    )


class MessageBatch(Base):
    __tablename__ = "message_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trigger_msg_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("messages.id"), nullable=False
    )
    context_msg_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    context_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    trigger_message: Mapped["Message"] = relationship(
        back_populates="batches",
        foreign_keys=[trigger_msg_id],
    )
    ai_logs: Mapped[list["AILog"]] = relationship(back_populates="batch")


class AILog(Base):
    __tablename__ = "ai_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("message_batches.id"), nullable=False
    )
    answer: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    batch: Mapped["MessageBatch"] = relationship(back_populates="ai_logs")
    alert: Mapped[Optional["Alert"]] = relationship(back_populates="ai_log")
    feedback: Mapped[Optional["Feedback"]] = relationship(back_populates="ai_log")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ai_log_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ai_logs.id"), nullable=False
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    ai_log: Mapped["AILog"] = relationship(back_populates="alert")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ai_log_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ai_logs.id"), nullable=False
    )
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    ai_log: Mapped["AILog"] = relationship(back_populates="feedback")


class Config(Base):
    __tablename__ = "configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

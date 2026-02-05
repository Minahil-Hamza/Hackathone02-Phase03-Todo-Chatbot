"""Message model for conversation history."""

from datetime import datetime
from enum import Enum
from typing import Optional, Any
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class MessageRole(str, Enum):
    """Role of the message author."""

    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation.

    Attributes:
        id: Unique identifier for the message.
        conversation_id: Parent conversation reference.
        role: Whether this is a user or assistant message.
        content: The message text content.
        tool_calls: Tool calls made by assistant (JSON).
        created_at: When the message was created.
    """

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True, nullable=False)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False)
    tool_calls: Optional[list[dict[str, Any]]] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

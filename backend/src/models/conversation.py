"""Conversation model for chat sessions."""

from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Conversation(SQLModel, table=True):
    """
    Represents a chat session between user and assistant.

    Attributes:
        id: Unique identifier for the conversation.
        user_id: Owner identifier (stores user UUID as string).
        created_at: When the conversation was started.
        updated_at: When the conversation was last active.
    """

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    def touch(self) -> None:
        """Update the last activity timestamp."""
        self.updated_at = datetime.utcnow()

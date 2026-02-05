"""Task model for user todos."""

from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    """
    Represents a user's todo item.

    Attributes:
        id: Unique identifier for the task.
        user_id: Owner identifier (stores user UUID as string).
        title: Task description (max 500 characters).
        is_completed: Whether the task is complete.
        created_at: When the task was created.
        updated_at: When the task was last modified.
    """

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=500, nullable=False)
    is_completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True
        self.updated_at = datetime.utcnow()

    def update_title(self, new_title: str) -> None:
        """Update the task title."""
        self.title = new_title
        self.updated_at = datetime.utcnow()

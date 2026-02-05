"""Shared utilities for MCP tools."""

import logging
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Task

logger = logging.getLogger(__name__)


async def find_tasks_by_identifier(
    session: AsyncSession, user_id: str, task_identifier: str
) -> list[Task]:
    """
    Find tasks matching the identifier using fuzzy matching.

    Args:
        session: Database session.
        user_id: The user ID.
        task_identifier: The task title or partial match.

    Returns:
        List of matching tasks.
    """
    # Try case-insensitive LIKE query for fuzzy matching
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.title.ilike(f"%{task_identifier}%"))
    )
    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_available_tasks_message(session: AsyncSession, user_id: str) -> str:
    """
    Get a formatted list of available tasks for error messages.

    Args:
        session: Database session.
        user_id: The user ID.

    Returns:
        Formatted string with task list or empty message.
    """
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.asc())
    )
    result = await session.execute(statement)
    tasks = result.scalars().all()

    if not tasks:
        return "You don't have any tasks yet."

    task_list = "\n".join(f"- {t.title}" for t in tasks)
    return f"Here are your available tasks:\n{task_list}"

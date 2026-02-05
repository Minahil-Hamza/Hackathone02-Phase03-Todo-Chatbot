"""MCP tool for completing tasks."""

import logging
from datetime import datetime

from sqlmodel import select

from src.mcp.server import register_tool
from src.db import async_session_factory
from src.models import Task

logger = logging.getLogger(__name__)


async def find_tasks_by_identifier(
    session, user_id: str, task_identifier: str
) -> list[Task]:
    """
    Find tasks matching the identifier using fuzzy matching.

    Args:
        session: Database session.
        user_id: The user ID (UUID as string).
        task_identifier: The task title or partial match.

    Returns:
        List of matching tasks.
    """
    # Query tasks by user_id with title filter
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.title.ilike(f"%{task_identifier}%"))
    )

    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_available_tasks_message(session, user_id: str) -> str:
    """Get a formatted list of available tasks for error messages."""
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


@register_tool("complete_task")
async def complete_task(user_id: str, task_identifier: str) -> str:
    """
    Mark a task as completed.

    Args:
        user_id: The ID of the user.
        task_identifier: The task title or partial match to identify the task.

    Returns:
        Confirmation message or error with available tasks.
    """
    task_identifier = task_identifier.strip()
    if not task_identifier:
        return "I need to know which task you want to complete. Could you tell me the task name?"

    async with async_session_factory() as session:
        try:
            # Find matching tasks
            matching_tasks = await find_tasks_by_identifier(
                session, user_id, task_identifier
            )

            if not matching_tasks:
                # Task not found - show available tasks
                available = await get_available_tasks_message(session, user_id)
                return f"I couldn't find a task matching '{task_identifier}'. {available}"

            if len(matching_tasks) > 1:
                # Ambiguous match - ask for clarification
                task_list = "\n".join(f"- {t.title}" for t in matching_tasks)
                return (
                    f"I found multiple tasks matching '{task_identifier}'. "
                    f"Which one did you mean?\n{task_list}"
                )

            # Single match - complete the task
            task = matching_tasks[0]

            if task.is_completed:
                return f"Task '{task.title}' is already completed!"

            task.is_completed = True
            task.updated_at = datetime.utcnow()
            session.add(task)
            await session.commit()

            logger.info(f"Completed task '{task.title}' for user {user_id}")
            return f"Great job! Task '{task.title}' has been marked as complete."

        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            await session.rollback()
            return "I had trouble completing that task. Please try again."

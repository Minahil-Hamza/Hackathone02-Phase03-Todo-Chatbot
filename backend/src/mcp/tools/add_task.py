"""MCP tool for adding tasks."""

import logging

from src.mcp.server import register_tool
from src.db import async_session_factory
from src.models import Task

logger = logging.getLogger(__name__)


@register_tool("add_task")
async def add_task(user_id: str, title: str) -> str:
    """
    Create a new task for the user.

    Args:
        user_id: The ID of the user (UUID as string).
        title: The title of the task to create.

    Returns:
        Confirmation message with task details.
    """
    # Validate title
    title = title.strip()
    if not title:
        return "I couldn't create a task without a title. What would you like to call this task?"

    if len(title) > 500:
        return "That task title is too long. Could you make it shorter (under 500 characters)?"

    async with async_session_factory() as session:
        try:
            # Create the task with user_id
            task = Task(user_id=user_id, title=title)
            session.add(task)
            await session.commit()
            await session.refresh(task)

            logger.info(f"Created task '{title}' for user {user_id} (ID: {task.id})")

            return f"Task '{title}' created successfully (ID: {task.id})"

        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            await session.rollback()
            return "I had trouble creating that task. Please try again."

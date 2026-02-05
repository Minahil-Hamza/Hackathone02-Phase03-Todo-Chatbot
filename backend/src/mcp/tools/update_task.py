"""MCP tool for updating tasks."""

import logging
from datetime import datetime
from sqlmodel import select

from src.mcp.server import register_tool
from src.db import async_session_factory
from src.models import Task
from src.mcp.tools.complete_task import find_tasks_by_identifier, get_available_tasks_message

logger = logging.getLogger(__name__)


@register_tool("update_task")
async def update_task(user_id: str, task_identifier: str, new_title: str) -> str:
    """
    Update an existing task's title.

    Args:
        user_id: The ID of the user.
        task_identifier: The current task title or partial match.
        new_title: The new title for the task.

    Returns:
        Confirmation message or error with available tasks.
    """
    task_identifier = task_identifier.strip()
    new_title = new_title.strip()

    if not task_identifier:
        return "I need to know which task you want to update. Could you tell me the task name?"

    if not new_title:
        return "I need to know what to update the task to. What should the new title be?"

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

            # Single match - update the task
            task = matching_tasks[0]
            old_title = task.title

            task.title = new_title
            task.updated_at = datetime.utcnow()
            session.add(task)
            await session.commit()

            logger.info(f"Updated task '{old_title}' -> '{new_title}' for user {user_id}")
            return f"Done! I've updated '{old_title}' to '{new_title}'."

        except Exception as e:
            logger.error(f"Failed to update task: {e}")
            await session.rollback()
            return "I had trouble updating that task. Please try again."

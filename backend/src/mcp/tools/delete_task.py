"""MCP tool for deleting tasks."""

import logging
from sqlmodel import select

from src.mcp.server import register_tool
from src.db import async_session_factory
from src.models import Task
from src.mcp.tools.complete_task import find_tasks_by_identifier, get_available_tasks_message

logger = logging.getLogger(__name__)


@register_tool("delete_task")
async def delete_task(user_id: str, task_identifier: str) -> str:
    """
    Remove a task from the list.

    Args:
        user_id: The ID of the user.
        task_identifier: The task title or partial match to identify the task.

    Returns:
        Confirmation message or error with available tasks.
    """
    task_identifier = task_identifier.strip()
    if not task_identifier:
        return "I need to know which task you want to delete. Could you tell me the task name?"

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
                    f"Which one did you want to delete?\n{task_list}"
                )

            # Single match - delete the task
            task = matching_tasks[0]
            task_title = task.title

            await session.delete(task)
            await session.commit()

            logger.info(f"Deleted task '{task_title}' for user {user_id}")
            return f"Done! I've removed '{task_title}' from your task list."

        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            await session.rollback()
            return "I had trouble deleting that task. Please try again."

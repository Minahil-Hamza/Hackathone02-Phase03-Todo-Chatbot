"""MCP tool for listing tasks."""

import logging

from sqlmodel import select

from src.mcp.server import register_tool
from src.db import async_session_factory
from src.models import Task

logger = logging.getLogger(__name__)


@register_tool("list_tasks")
async def list_tasks(user_id: str) -> str:
    """
    List all tasks for the user.

    Args:
        user_id: The ID of the user (UUID as string).

    Returns:
        Formatted task list or friendly message if empty.
    """
    async with async_session_factory() as session:
        try:
            # Query tasks by user_id
            statement = (
                select(Task)
                .where(Task.user_id == user_id)
                .order_by(Task.created_at.asc())
            )

            result = await session.execute(statement)
            tasks = result.scalars().all()

            if not tasks:
                return "You don't have any tasks yet. Would you like to create one?"

            # Format tasks with completion status
            task_lines = []
            for task in tasks:
                status = "[x]" if task.is_completed else "[ ]"
                task_lines.append(f"{status} {task.title} (ID: {task.id})")

            # Count completed vs pending
            completed = sum(1 for t in tasks if t.is_completed)
            pending = len(tasks) - completed

            header = f"Here are your tasks ({completed} completed, {pending} pending):\n"
            return header + "\n".join(task_lines)

        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return "I had trouble fetching your tasks. Please try again."

"""MCP tools for task operations."""

# Import tools to register them with the MCP server
from src.mcp.tools.add_task import add_task
from src.mcp.tools.list_tasks import list_tasks
from src.mcp.tools.complete_task import complete_task
from src.mcp.tools.update_task import update_task
from src.mcp.tools.delete_task import delete_task

__all__ = ["add_task", "list_tasks", "complete_task", "update_task", "delete_task"]

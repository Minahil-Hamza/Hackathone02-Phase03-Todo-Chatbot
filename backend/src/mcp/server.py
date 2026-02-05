"""MCP Server setup for task operations."""

from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

# Registry for MCP tools
_tools: dict[str, Callable[..., Any]] = {}


def register_tool(name: str) -> Callable:
    """
    Decorator to register a function as an MCP tool.

    Args:
        name: The name of the tool.

    Returns:
        Decorator function.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        _tools[name] = func
        logger.info(f"Registered MCP tool: {name}")
        return func

    return decorator


def get_tools() -> dict[str, Callable[..., Any]]:
    """Get all registered MCP tools."""
    return _tools.copy()


def get_tool(name: str) -> Callable[..., Any] | None:
    """Get a specific tool by name."""
    return _tools.get(name)


class MCPServer:
    """
    MCP Server that manages task operation tools.

    This server runs in-process with FastAPI and provides
    tools for the OpenAI agent to interact with tasks.
    """

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the MCP server and load tools."""
        if self._initialized:
            return

        # Import tools to register them
        from src.mcp.tools import (  # noqa: F401
            add_task,
            list_tasks,
            complete_task,
            update_task,
            delete_task,
        )

        self._initialized = True
        logger.info(f"MCP Server initialized with {len(_tools)} tools")

    @property
    def tools(self) -> dict[str, Callable[..., Any]]:
        """Get all registered tools."""
        return get_tools()

    async def call_tool(self, name: str, **kwargs: Any) -> Any:
        """
        Call a tool by name with the given arguments.

        Args:
            name: The name of the tool to call.
            **kwargs: Arguments to pass to the tool.

        Returns:
            The result of the tool execution.

        Raises:
            ValueError: If the tool is not found.
        """
        tool = get_tool(name)
        if tool is None:
            raise ValueError(f"Tool not found: {name}")

        return await tool(**kwargs)


# Singleton instance
mcp_server = MCPServer()

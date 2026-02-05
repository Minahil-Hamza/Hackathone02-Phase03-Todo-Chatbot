"""Todo Agent implementation using OpenAI Agents SDK."""

import os
import json
import logging
import asyncio
from typing import Any
from dataclasses import dataclass

from openai import AsyncOpenAI, APITimeoutError, APIConnectionError, APIError
import httpx
from dotenv import load_dotenv

from src.mcp.server import get_tools

load_dotenv()
logger = logging.getLogger(__name__)

# API timeout in seconds
API_TIMEOUT = 30.0

# System prompt for the Todo agent
SYSTEM_PROMPT = """You are a helpful AI assistant that helps users manage their todo tasks through natural conversation.

Your capabilities:
- Create new tasks when users ask to add, create, or remember something
- List tasks when users ask to show, see, or display their todos
- Mark tasks as complete when users say they finished or completed something
- Update tasks when users want to change or modify a task
- Delete tasks when users want to remove something from their list

Guidelines:
1. Always confirm actions with friendly, conversational messages
2. When listing tasks, format them clearly with completion status
3. If a task reference is ambiguous, ask for clarification
4. If a task is not found, show the available tasks
5. Be helpful and encourage users to stay organized
6. Never expose technical details or error messages

Remember: You can ONLY manage tasks through the provided tools. Do not pretend to remember tasks or create them without using tools."""

# OpenAI client with timeout
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=httpx.Timeout(API_TIMEOUT, connect=10.0),
)


@dataclass
class ToolCall:
    """Represents a tool call made by the agent."""

    tool_name: str
    arguments: dict[str, Any]
    result: str


@dataclass
class AgentResponse:
    """Response from the agent."""

    content: str
    tool_calls: list[ToolCall]


class TodoAgent:
    """
    AI Agent for managing todos through natural language.

    Uses OpenAI's function calling to invoke MCP tools.
    """

    def __init__(self, user_id: str) -> None:
        """
        Initialize the agent for a specific user.

        Args:
            user_id: The user ID for task operations.
        """
        self.user_id = user_id
        self._tools_schema: list[dict[str, Any]] | None = None

    def _get_tools_schema(self) -> list[dict[str, Any]]:
        """Get OpenAI function definitions for available tools."""
        if self._tools_schema is not None:
            return self._tools_schema

        self._tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The title or description of the task",
                            }
                        },
                        "required": ["title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all tasks for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {
                                "type": "string",
                                "description": "The task title or a partial match to identify the task",
                            }
                        },
                        "required": ["task_identifier"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task's title",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {
                                "type": "string",
                                "description": "The current task title or partial match",
                            },
                            "new_title": {
                                "type": "string",
                                "description": "The new title for the task",
                            },
                        },
                        "required": ["task_identifier", "new_title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Remove a task from the list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_identifier": {
                                "type": "string",
                                "description": "The task title or partial match to identify the task",
                            }
                        },
                        "required": ["task_identifier"],
                    },
                },
            },
        ]
        return self._tools_schema

    async def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """
        Execute an MCP tool.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Arguments for the tool.

        Returns:
            Result string from the tool.
        """
        tools = get_tools()
        tool = tools.get(tool_name)

        if tool is None:
            return f"Error: Tool '{tool_name}' not found"

        try:
            # Add user_id to arguments
            arguments["user_id"] = self.user_id
            result = await tool(**arguments)
            return result
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return f"Error executing tool: {str(e)}"

    async def run(
        self, message: str, conversation_history: list[dict[str, str]] | None = None
    ) -> AgentResponse:
        """
        Run the agent with a user message.

        Args:
            message: The user's message.
            conversation_history: Previous messages in the conversation.

        Returns:
            AgentResponse with content and tool calls.
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add current message
        messages.append({"role": "user", "content": message})

        tool_calls_made: list[ToolCall] = []
        max_iterations = 5  # Prevent infinite loops

        # Run agent loop
        for iteration in range(max_iterations):
            try:
                logger.info(f"Calling OpenAI API (iteration {iteration + 1})")
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=self._get_tools_schema(),
                    tool_choice="auto",
                )
                logger.info("OpenAI API response received")

            except APITimeoutError:
                logger.error("OpenAI API timeout")
                return AgentResponse(
                    content="I'm sorry, the request took too long. Please try again.",
                    tool_calls=tool_calls_made,
                )
            except APIConnectionError as e:
                logger.error(f"OpenAI API connection error: {e}")
                return AgentResponse(
                    content="I'm having trouble connecting to my AI service. Please try again.",
                    tool_calls=tool_calls_made,
                )
            except APIError as e:
                logger.error(f"OpenAI API error: {e}")
                return AgentResponse(
                    content="I encountered an error. Please try again.",
                    tool_calls=tool_calls_made,
                )

            assistant_message = response.choices[0].message

            # Check if there are tool calls
            if assistant_message.tool_calls:
                # Add assistant message with tool calls to history
                messages.append(assistant_message.model_dump())

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    logger.info(f"Executing tool: {tool_name} with args: {arguments}")
                    result = await self._execute_tool(tool_name, arguments)

                    tool_calls_made.append(
                        ToolCall(tool_name=tool_name, arguments=arguments, result=result)
                    )

                    # Add tool result to messages
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )
            else:
                # No tool calls, return the response
                return AgentResponse(
                    content=assistant_message.content or "",
                    tool_calls=tool_calls_made,
                )

        # Max iterations reached
        logger.warning("Max iterations reached in agent loop")
        return AgentResponse(
            content="I completed your request but reached my processing limit.",
            tool_calls=tool_calls_made,
        )


async def run_agent(
    user_id: str,
    message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> AgentResponse:
    """
    Convenience function to run the agent.

    Args:
        user_id: The user ID for task operations.
        message: The user's message.
        conversation_history: Previous messages in the conversation.

    Returns:
        AgentResponse with content and tool calls.
    """
    agent = TodoAgent(user_id)
    return await agent.run(message, conversation_history)

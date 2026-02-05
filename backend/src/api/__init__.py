"""API models and utilities for the Todo Chatbot."""

from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Existing conversation ID. If omitted, creates new conversation",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's message text",
    )


class ToolCallResponse(BaseModel):
    """Represents a tool call made during the chat."""

    tool_name: str = Field(..., description="Name of the MCP tool invoked")
    arguments: dict[str, Any] = Field(..., description="Arguments passed to the tool")
    result: str = Field(..., description="Result returned by the tool")


class ChatResponse(BaseModel):
    """Response body for the chat endpoint."""

    conversation_id: UUID = Field(..., description="ID of the conversation (new or existing)")
    response: str = Field(..., description="AI assistant's response message")
    tool_calls: list[ToolCallResponse] = Field(
        default_factory=list,
        description="List of MCP tools invoked (may be empty)",
    )


__all__ = ["ChatRequest", "ChatResponse", "ToolCallResponse"]

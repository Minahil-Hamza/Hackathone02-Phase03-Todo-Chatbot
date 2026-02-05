"""Chat endpoint and conversation history for the AI Todo Chatbot."""

import logging
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from sqlmodel import select, col

from src.api import ChatRequest, ChatResponse, ToolCallResponse
from src.api.deps import CurrentUser
from src.db import async_session_factory
from src.models import Conversation, Message, MessageRole
from src.agent.todo_agent import run_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


# --- Response models for conversation history ---

class MessageResponse(BaseModel):
    """Response model for a message."""
    id: str
    role: str
    content: str
    tool_calls: Optional[list] = None
    created_at: str


class ConversationResponse(BaseModel):
    """Response model for a conversation."""
    id: str
    created_at: str
    updated_at: str
    preview: str


class ConversationMessagesResponse(BaseModel):
    """Response model for conversation messages."""
    conversation_id: str
    messages: List[MessageResponse]


# --- Helper functions ---

async def get_or_create_conversation(
    user_id: str, conversation_id: Optional[UUID]
) -> Conversation:
    """Get an existing conversation or create a new one."""
    async with async_session_factory() as session:
        if conversation_id:
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            result = await session.execute(statement)
            conversation = result.scalar_one_or_none()

            if conversation:
                return conversation

            logger.warning(
                f"Conversation {conversation_id} not found for user {user_id}, creating new"
            )

        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

        logger.info(f"Created conversation {conversation.id} for user {user_id}")
        return conversation


async def load_conversation_history(conversation_id: UUID) -> list[dict[str, str]]:
    """Load all messages for a conversation."""
    async with async_session_factory() as session:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        result = await session.execute(statement)
        messages = result.scalars().all()

        return [{"role": msg.role.value, "content": msg.content} for msg in messages]


async def save_message(
    conversation_id: UUID,
    role: MessageRole,
    content: str,
    tool_calls: Optional[list[dict]] = None,
) -> Message:
    """Save a message to the database."""
    async with async_session_factory() as session:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
        )
        session.add(message)

        statement = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.execute(statement)
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.touch()
            session.add(conversation)

        await session.commit()
        await session.refresh(message)

        return message


# --- Chat endpoint ---

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: CurrentUser,
) -> ChatResponse:
    """Send a message to the AI chatbot and receive a response."""
    user_id = str(current_user.id)

    message = request.message.strip()
    if not message:
        raise HTTPException(
            status_code=400,
            detail="I didn't catch that. Could you tell me what you'd like to do with your tasks?",
        )

    try:
        conversation = await get_or_create_conversation(
            user_id, request.conversation_id
        )

        history = await load_conversation_history(conversation.id)
        await save_message(conversation.id, MessageRole.USER, message)

        logger.info(f"Running agent for user {user_id}, message: {message[:50]}...")
        agent_response = await run_agent(user_id, message, history)

        tool_calls_response = [
            ToolCallResponse(
                tool_name=tc.tool_name,
                arguments=tc.arguments,
                result=tc.result,
            )
            for tc in agent_response.tool_calls
        ]

        tool_calls_data = (
            [
                {"tool_name": tc.tool_name, "arguments": tc.arguments, "result": tc.result}
                for tc in agent_response.tool_calls
            ]
            if agent_response.tool_calls
            else None
        )

        await save_message(
            conversation.id,
            MessageRole.ASSISTANT,
            agent_response.content,
            tool_calls_data,
        )

        return ChatResponse(
            conversation_id=conversation.id,
            response=agent_response.content,
            tool_calls=tool_calls_response,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="I'm having trouble processing your request right now. Please try again.",
        )


# --- Conversation history endpoints ---

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(current_user: CurrentUser) -> List[ConversationResponse]:
    """List all conversations for the authenticated user."""
    user_id = str(current_user.id)

    async with async_session_factory() as session:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        result = await session.execute(statement)
        conversations = result.scalars().all()

        responses = []
        for conv in conversations:
            # Get first user message as preview
            msg_statement = (
                select(Message)
                .where(
                    Message.conversation_id == conv.id,
                    Message.role == MessageRole.USER,
                )
                .order_by(Message.created_at.asc())
                .limit(1)
            )
            msg_result = await session.execute(msg_statement)
            first_msg = msg_result.scalar_one_or_none()

            preview = first_msg.content[:80] if first_msg else "New conversation"

            responses.append(ConversationResponse(
                id=str(conv.id),
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                preview=preview,
            ))

        return responses


@router.get("/conversations/{conversation_id}/messages", response_model=ConversationMessagesResponse)
async def get_conversation_messages(
    conversation_id: str,
    current_user: CurrentUser,
) -> ConversationMessagesResponse:
    """Get all messages for a conversation."""
    user_id = str(current_user.id)

    async with async_session_factory() as session:
        # Verify conversation belongs to user
        conv_statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        conv_result = await session.execute(conv_statement)
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found.")

        # Get all messages
        msg_statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        msg_result = await session.execute(msg_statement)
        messages = msg_result.scalars().all()

        message_responses = [
            MessageResponse(
                id=str(msg.id),
                role=msg.role.value,
                content=msg.content,
                tool_calls=msg.tool_calls,
                created_at=msg.created_at.isoformat(),
            )
            for msg in messages
        ]

        return ConversationMessagesResponse(
            conversation_id=str(conversation_id),
            messages=message_responses,
        )


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser,
) -> None:
    """Delete a conversation and all its messages."""
    user_id = str(current_user.id)

    async with async_session_factory() as session:
        conv_statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        conv_result = await session.execute(conv_statement)
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found.")

        # Delete all messages first
        msg_statement = select(Message).where(Message.conversation_id == conversation_id)
        msg_result = await session.execute(msg_statement)
        messages = msg_result.scalars().all()
        for msg in messages:
            await session.delete(msg)

        await session.delete(conversation)
        await session.commit()

        logger.info(f"Deleted conversation {conversation_id} for user {user_id}")

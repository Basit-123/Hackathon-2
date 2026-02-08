"""Database utility functions for chat operations."""

from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from models import Conversation, Message, ToolCall, MessageRead, ToolCallCreate
from sqlalchemy import desc


def get_or_create_conversation(session: Session, user_id: str, conversation_id: Optional[int] = None) -> Conversation:
    """
    Get existing conversation or create a new one.

    Args:
        session: Database session
        user_id: User identifier
        conversation_id: Optional conversation ID (if None, creates new)

    Returns:
        Conversation object
    """
    if conversation_id:
        # Fetch existing conversation
        statement = select(Conversation).where(
            (Conversation.id == conversation_id) & (Conversation.user_id == user_id)
        )
        conversation = session.exec(statement).first()
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found or unauthorized")
        # Update timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()
        return conversation
    else:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation


def create_message(
    session: Session,
    user_id: str,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """
    Create and store a new message.

    Args:
        session: Database session
        user_id: User identifier
        conversation_id: Conversation ID
        role: Message role ("user" or "assistant")
        content: Message content

    Returns:
        Created Message object
    """
    if role not in ["user", "assistant"]:
        raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'")

    message = Message(
        user_id=user_id,
        conversation_id=conversation_id,
        role=role,
        content=content,
        created_at=datetime.utcnow()
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def get_conversation_history(
    session: Session,
    user_id: str,
    conversation_id: int,
    limit: int = 50,
    offset: int = 0
) -> List[MessageRead]:
    """
    Fetch conversation history with pagination.

    Args:
        session: Database session
        user_id: User identifier
        conversation_id: Conversation ID
        limit: Maximum number of messages to fetch
        offset: Number of messages to skip

    Returns:
        List of Message objects ordered by creation time
    """
    statement = select(Message).where(
        (Message.conversation_id == conversation_id) &
        (Message.user_id == user_id)
    ).order_by(Message.created_at).offset(offset).limit(limit)

    messages = session.exec(statement).all()
    return messages


def store_tool_calls(
    session: Session,
    message_id: int,
    tool_calls: List[dict]
) -> List[ToolCall]:
    """
    Store tool call records for a message.

    Args:
        session: Database session
        message_id: Message ID that triggered the tool calls
        tool_calls: List of tool call dictionaries with tool_name, parameters, result

    Returns:
        List of created ToolCall objects
    """
    import json

    stored_calls = []
    for call in tool_calls:
        tool_call = ToolCall(
            message_id=message_id,
            tool_name=call.get("tool_name", "unknown"),
            parameters=json.dumps(call.get("parameters", {})),
            result=json.dumps(call.get("result", {})),
            created_at=datetime.utcnow()
        )
        session.add(tool_call)
        stored_calls.append(tool_call)

    session.commit()
    return stored_calls


def get_tool_calls_for_message(
    session: Session,
    message_id: int
) -> List[ToolCall]:
    """
    Fetch all tool calls for a specific message.

    Args:
        session: Database session
        message_id: Message ID

    Returns:
        List of ToolCall objects
    """
    statement = select(ToolCall).where(
        ToolCall.message_id == message_id
    ).order_by(ToolCall.created_at)

    tool_calls = session.exec(statement).all()
    return tool_calls

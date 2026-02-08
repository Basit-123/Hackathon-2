"""
Database Models
User and Task models using SQLModel
"""

from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


# User Model (for Better Auth integration)
class User(SQLModel, table=True):
    """
    User model managed by Better Auth
    Note: Better Auth handles user table creation and management
    """
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Task Models
class Task(SQLModel, table=True):
    """
    Task model for user todo items
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    title: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


# Task Schemas for API
class TaskCreate(SQLModel):
    """Schema for creating a new task"""
    title: str
    description: Optional[str] = None


class TaskUpdate(SQLModel):
    """Schema for updating a task"""
    title: str
    description: Optional[str] = None


class TaskRead(SQLModel):
    """Schema for reading a task"""
    id: int
    user_id: str
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# User Schemas for Auth
class UserSignup(SQLModel):
    """Schema for user signup"""
    email: str
    password: str


class UserSignin(SQLModel):
    """Schema for user signin"""
    email: str
    password: str


class UserResponse(SQLModel):
    """Schema for user response (no password)"""
    id: str
    email: str
    created_at: datetime


class TokenResponse(SQLModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


# Chat Models for AI Chatbot
class Conversation(SQLModel, table=True):
    """
    Conversation model for tracking chat sessions
    Each user can have multiple conversations (e.g., different topics)
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Message(SQLModel, table=True):
    """
    Message model for storing chat history
    Maintains user isolation and conversation context
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str = Field(index=True)  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ToolCall(SQLModel, table=True):
    """
    Tool call logging model for auditing MCP tool invocations
    Tracks what tools were invoked, their parameters, and results
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="message.id")
    tool_name: str = Field(index=True)
    parameters: str  # JSON string of parameters
    result: str  # JSON string of result
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Chat Schemas for API
class ConversationCreate(SQLModel):
    """Schema for creating a new conversation"""
    pass  # No fields needed - server generates


class ConversationRead(SQLModel):
    """Schema for reading a conversation"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime


class MessageCreate(SQLModel):
    """Schema for creating a new message"""
    role: str  # "user" or "assistant"
    content: str


class MessageRead(SQLModel):
    """Schema for reading a message"""
    id: int
    user_id: str
    conversation_id: int
    role: str
    content: str
    created_at: datetime


class ToolCallCreate(SQLModel):
    """Schema for creating a tool call record"""
    tool_name: str
    parameters: str  # JSON string
    result: str  # JSON string


class ToolCallRead(SQLModel):
    """Schema for reading a tool call record"""
    id: int
    message_id: int
    tool_name: str
    parameters: str
    result: str
    created_at: datetime


class ChatRequest(SQLModel):
    """Schema for chat API request"""
    conversation_id: Optional[int] = None  # None = create new conversation
    message: str  # User's message


class ChatResponse(SQLModel):
    """Schema for chat API response"""
    conversation_id: int
    response: str  # Assistant's response
    tool_calls: list = []  # List of tool calls made

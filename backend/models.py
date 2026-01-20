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

"""
Task CRUD Routes
All task management endpoints with user isolation and JWT verification
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from sqlmodel import Session, select
from datetime import datetime

from models import Task, TaskCreate, TaskUpdate, TaskRead
from db import get_session
from middleware import verify_user_id_match

router = APIRouter()


@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    request: Request = None,  # Will be populated by middleware
):
    """
    Create a new task for the specified user

    - Validates title is not empty
    - Sets user_id from token (must match URL)
    - Sets completed=False by default
    """
    # Verify user_id matches JWT token
    verify_user_id_match(request, user_id)

    # Validate title
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required",
        )

    # Create new task
    new_task = Task(
        user_id=user_id,
        title=task_data.title.strip(),
        description=task_data.description.strip() if task_data.description else None,
        completed=False,
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return new_task


@router.get("/{user_id}/tasks", response_model=List[TaskRead])
async def get_tasks(
    user_id: str,
    status: Optional[str] = Query(None, description="Filter by status: 'active' or 'completed'"),
    sort_by: Optional[str] = Query("created_at", description="Sort by: 'created_at' or 'title'"),
    session: Session = Depends(get_session),
    request: Request = None,
):
    """
    Get all tasks for the specified user

    - Supports filtering by status (active/completed)
    - Supports sorting by created_at or title
    - Enforces user isolation (only returns user's own tasks)
    """
    # Verify user_id matches JWT token
    verify_user_id_match(request, user_id)

    # Build query
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status == "active":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)
    elif status is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status value. Must be 'active' or 'completed'",
        )

    # Apply sorting
    if sort_by == "title":
        query = query.order_by(Task.title)
    elif sort_by == "created_at":
        query = query.order_by(Task.created_at.desc())
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sort_by value. Must be 'created_at' or 'title'",
        )

    # Execute query
    tasks = session.exec(query).all()

    return list(tasks)


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    request: Request = None,
):
    """
    Get a specific task by ID

    - Returns task only if it belongs to the user
    - Returns 404 if task doesn't exist
    """
    # Verify user_id matches JWT token
    verify_user_id_match(request, user_id)

    # Find task
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Verify task belongs to user
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: str,
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    request: Request = None,
):
    """
    Update a task

    - Updates title and/or description
    - Returns 404 if task doesn't exist
    - Only owner can update their own tasks
    """
    # Verify user_id matches JWT token
    verify_user_id_match(request, user_id)

    # Find task
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Verify task belongs to user
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Validate title
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required",
        )

    # Update task fields
    task.title = task_data.title.strip()
    task.description = task_data.description.strip() if task_data.description else None
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    request: Request = None,
):
    """
    Delete a task

    - Returns 404 if task doesn't exist
    - Only owner can delete their own tasks
    """
    # Verify user_id matches JWT token
    verify_user_id_match(request, user_id)

    # Find task
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Verify task belongs to user
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Delete task
    session.delete(task)
    session.commit()

    return None


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_complete_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    request: Request = None,
):
    """
    Toggle task completion status

    - Flips completed field (true -> false, false -> true)
    - Returns 404 if task doesn't exist
    - Only owner can update their own tasks
    """

    # Verify user_id matches JWT token
    verify_user_id_match(request, user_id)

    # Find task
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Verify task belongs to user
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task

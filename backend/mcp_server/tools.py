"""MCP Tool implementations for task management operations.

These tools are exposed to the OpenAI Agents SDK via the MCP Server.
Each tool handler queries/updates the database and returns standardized responses.
"""

import json
import logging
from typing import Any, Dict, Optional
from sqlmodel import Session, select
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolHandlers:
    """Collection of MCP tool handler functions."""

    def __init__(self, db_session: Session):
        """Initialize tool handlers with database session.

        Args:
            db_session: SQLModel database session
        """
        self.db = db_session

    async def add_task(
        self, user_id: str, title: str, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new task.

        Args:
            user_id: User identifier
            title: Task title (required)
            description: Task description (optional)

        Returns:
            Dict with task_id, status, title
        """
        try:
            # Import here to avoid circular imports
            from models import Task

            # Validate inputs
            if not user_id:
                raise ValueError("user_id is required")
            if not title or not title.strip():
                raise ValueError("title is required and cannot be empty")

            # Create task
            task = Task(
                user_id=user_id,
                title=title.strip(),
                description=description.strip() if description else None,
                completed=False,
                created_at=datetime.utcnow(),
            )

            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)

            logger.info(f"Task created: {task.id} for user {user_id}")

            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title,
            }
        except Exception as e:
            logger.error(f"Error in add_task: {str(e)}")
            return {"error": str(e), "status": "failed"}

    async def list_tasks(
        self, user_id: str, status: str = "all"
    ) -> Dict[str, Any]:
        """List tasks for a user with optional filtering.

        Args:
            user_id: User identifier
            status: Filter by status - "all", "pending", "completed"

        Returns:
            Dict with tasks array
        """
        try:
            from models import Task

            # Validate inputs
            if not user_id:
                raise ValueError("user_id is required")

            status = status.lower() if status else "all"
            if status not in ["all", "pending", "completed"]:
                raise ValueError("status must be 'all', 'pending', or 'completed'")

            # Build query
            query = select(Task).where(Task.user_id == user_id)

            if status == "pending":
                query = query.where(Task.completed == False)
            elif status == "completed":
                query = query.where(Task.completed == True)

            # Add ordering
            query = query.order_by(Task.created_at.desc())

            tasks = self.db.exec(query).all()

            # Format response
            formatted_tasks = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                }
                for task in tasks
            ]

            logger.info(f"Listed {len(formatted_tasks)} tasks for user {user_id}")

            return {
                "tasks": formatted_tasks,
                "count": len(formatted_tasks),
                "status": "success",
            }
        except Exception as e:
            logger.error(f"Error in list_tasks: {str(e)}")
            return {"error": str(e), "status": "failed"}

    async def complete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """Mark a task as completed.

        Args:
            user_id: User identifier
            task_id: Task ID to mark complete

        Returns:
            Dict with task_id, status, title
        """
        try:
            from models import Task

            # Validate inputs
            if not user_id:
                raise ValueError("user_id is required")
            if not task_id:
                raise ValueError("task_id is required")

            # Find task with user isolation
            query = select(Task).where(
                (Task.id == task_id) & (Task.user_id == user_id)
            )
            task = self.db.exec(query).first()

            if not task:
                raise ValueError(f"Task {task_id} not found or unauthorized")

            # Update task
            task.completed = True
            task.updated_at = datetime.utcnow()

            self.db.add(task)
            self.db.commit()

            logger.info(f"Task {task_id} marked as completed for user {user_id}")

            return {
                "task_id": task.id,
                "status": "completed",
                "title": task.title,
            }
        except Exception as e:
            logger.error(f"Error in complete_task: {str(e)}")
            return {"error": str(e), "status": "failed"}

    async def delete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """Delete a task.

        Args:
            user_id: User identifier
            task_id: Task ID to delete

        Returns:
            Dict with task_id, status, title
        """
        try:
            from models import Task

            # Validate inputs
            if not user_id:
                raise ValueError("user_id is required")
            if not task_id:
                raise ValueError("task_id is required")

            # Find task with user isolation
            query = select(Task).where(
                (Task.id == task_id) & (Task.user_id == user_id)
            )
            task = self.db.exec(query).first()

            if not task:
                raise ValueError(f"Task {task_id} not found or unauthorized")

            # Store title before deletion
            title = task.title

            # Delete task
            self.db.delete(task)
            self.db.commit()

            logger.info(f"Task {task_id} deleted for user {user_id}")

            return {
                "task_id": task_id,
                "status": "deleted",
                "title": title,
            }
        except Exception as e:
            logger.error(f"Error in delete_task: {str(e)}")
            return {"error": str(e), "status": "failed"}

    async def update_task(
        self,
        user_id: str,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a task's title and/or description.

        Args:
            user_id: User identifier
            task_id: Task ID to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            Dict with task_id, status, title
        """
        try:
            from models import Task

            # Validate inputs
            if not user_id:
                raise ValueError("user_id is required")
            if not task_id:
                raise ValueError("task_id is required")
            if not title and description is None:
                raise ValueError("At least title or description must be provided")

            # Find task with user isolation
            query = select(Task).where(
                (Task.id == task_id) & (Task.user_id == user_id)
            )
            task = self.db.exec(query).first()

            if not task:
                raise ValueError(f"Task {task_id} not found or unauthorized")

            # Update fields
            if title:
                task.title = title.strip()
            if description is not None:
                task.description = description.strip() if description else None

            task.updated_at = datetime.utcnow()

            self.db.add(task)
            self.db.commit()

            logger.info(f"Task {task_id} updated for user {user_id}")

            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title,
            }
        except Exception as e:
            logger.error(f"Error in update_task: {str(e)}")
            return {"error": str(e), "status": "failed"}

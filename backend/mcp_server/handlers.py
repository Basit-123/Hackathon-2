"""MCP Tool registration and handler setup."""

import logging
from typing import Any, Dict
from sqlmodel import Session
from .server import MCPTool, MCPToolParameter, create_mcp_server
from .tools import ToolHandlers

logger = logging.getLogger(__name__)


def register_task_tools(db_session: Session) -> None:
    """Register all task management tools with the MCP server.

    Args:
        db_session: SQLModel database session for tool handlers
    """
    server = create_mcp_server()
    handlers = ToolHandlers(db_session)

    # Tool 1: add_task
    add_task_tool = MCPTool(
        name="add_task",
        description="Create a new task for the user",
        parameters=[
            MCPToolParameter(
                name="user_id",
                type_="string",
                required=True,
                description="User identifier (email or user ID)",
            ),
            MCPToolParameter(
                name="title",
                type_="string",
                required=True,
                description="Task title (required, must not be empty)",
            ),
            MCPToolParameter(
                name="description",
                type_="string",
                required=False,
                description="Task description (optional)",
            ),
        ],
        handler=handlers.add_task,
    )
    server.register_tool(add_task_tool)
    logger.info("Registered tool: add_task")

    # Tool 2: list_tasks
    list_tasks_tool = MCPTool(
        name="list_tasks",
        description="Retrieve tasks for the user with optional filtering by status",
        parameters=[
            MCPToolParameter(
                name="user_id",
                type_="string",
                required=True,
                description="User identifier (email or user ID)",
            ),
            MCPToolParameter(
                name="status",
                type_="string",
                required=False,
                description="Filter tasks by status: 'all' (default), 'pending', or 'completed'",
            ),
        ],
        handler=handlers.list_tasks,
    )
    server.register_tool(list_tasks_tool)
    logger.info("Registered tool: list_tasks")

    # Tool 3: complete_task
    complete_task_tool = MCPTool(
        name="complete_task",
        description="Mark a task as completed",
        parameters=[
            MCPToolParameter(
                name="user_id",
                type_="string",
                required=True,
                description="User identifier (email or user ID)",
            ),
            MCPToolParameter(
                name="task_id",
                type_="integer",
                required=True,
                description="Task ID to mark as completed",
            ),
        ],
        handler=handlers.complete_task,
    )
    server.register_tool(complete_task_tool)
    logger.info("Registered tool: complete_task")

    # Tool 4: delete_task
    delete_task_tool = MCPTool(
        name="delete_task",
        description="Delete a task from the list",
        parameters=[
            MCPToolParameter(
                name="user_id",
                type_="string",
                required=True,
                description="User identifier (email or user ID)",
            ),
            MCPToolParameter(
                name="task_id",
                type_="integer",
                required=True,
                description="Task ID to delete",
            ),
        ],
        handler=handlers.delete_task,
    )
    server.register_tool(delete_task_tool)
    logger.info("Registered tool: delete_task")

    # Tool 5: update_task
    update_task_tool = MCPTool(
        name="update_task",
        description="Update a task's title and/or description",
        parameters=[
            MCPToolParameter(
                name="user_id",
                type_="string",
                required=True,
                description="User identifier (email or user ID)",
            ),
            MCPToolParameter(
                name="task_id",
                type_="integer",
                required=True,
                description="Task ID to update",
            ),
            MCPToolParameter(
                name="title",
                type_="string",
                required=False,
                description="New task title (optional)",
            ),
            MCPToolParameter(
                name="description",
                type_="string",
                required=False,
                description="New task description (optional)",
            ),
        ],
        handler=handlers.update_task,
    )
    server.register_tool(update_task_tool)
    logger.info("Registered tool: update_task")

    logger.info(f"Successfully registered {len(server.tools)} MCP tools")

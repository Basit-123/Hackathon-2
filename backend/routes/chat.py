"""
Chat Routes - AI Chatbot endpoint for natural language task management
Supports Cohere API (primary) with mock fallback for testing
"""

import json
import logging
import os
import re
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlmodel import Session, select
from datetime import datetime

from models import ChatRequest, ChatResponse, Conversation, Message, Task
from db import get_session
from middleware import verify_user_id_match
from db_utils import (
    get_or_create_conversation,
    create_message,
    get_conversation_history,
    store_tool_calls,
)
from agents.config import is_cohere_available

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

# Use mock if explicitly set or if no AI provider is configured
USE_MOCK = os.getenv("USE_MOCK_CHATBOT", "false").lower() == "true"


def get_ai_agent():
    """Get the AI agent (Cohere) if available, otherwise return None for mock mode."""
    if USE_MOCK:
        logger.info("Using mock AI (USE_MOCK_CHATBOT=true)")
        return None

    if is_cohere_available():
        try:
            from agents.client import get_agent
            agent = get_agent()
            logger.info("Using Cohere AI agent")
            return agent
        except Exception as e:
            logger.warning(f"Failed to initialize Cohere agent: {e}")
            return None

    logger.info("No AI provider configured, using mock AI")
    return None


def mock_ai_response(message: str) -> tuple[Optional[Dict], str]:
    """
    Mock AI that parses user intent and returns action + response.
    Returns (action_dict, response_text)
    """
    message_lower = message.lower().strip()

    # Greetings
    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    if any(message_lower.startswith(g) for g in greetings):
        return None, "Hello! I'm your task management assistant. I can help you:\n- Add tasks: 'add task [title]'\n- List tasks: 'show my tasks' or 'list tasks'\n- Complete tasks: 'complete task [id]' or 'mark task [id] as done'\n- Delete tasks: 'delete task [id]'\n\nWhat would you like to do?"

    # Help
    if "help" in message_lower or "what can you do" in message_lower:
        return None, "I can help you manage your tasks! Here's what I can do:\n\n**Add a task**: 'add task buy groceries' or 'create task finish report'\n**List tasks**: 'show my tasks', 'list all tasks', 'show pending tasks'\n**Complete a task**: 'complete task 1' or 'mark task 2 as done'\n**Delete a task**: 'delete task 3' or 'remove task 1'\n\nJust tell me what you'd like to do!"

    # Add task
    add_patterns = [
        r"add (?:a )?task[:\s]+(.+)",
        r"create (?:a )?task[:\s]+(.+)",
        r"new task[:\s]+(.+)",
        r"add[:\s]+(.+)",
        r"create[:\s]+(.+)",
    ]
    for pattern in add_patterns:
        match = re.search(pattern, message_lower)
        if match:
            title = match.group(1).strip()
            # Clean up the title
            title = re.sub(r"^(to |for )", "", title)
            if title:
                return {"action": "add_task", "params": {"title": title.title()}}, f"I'll add that task for you!"

    # List tasks
    list_patterns = [
        r"(show|list|display|get|view).*tasks?",
        r"what.*tasks?.*have",
        r"my tasks?",
        r"all tasks?",
        r"pending tasks?",
        r"completed tasks?",
    ]
    for pattern in list_patterns:
        if re.search(pattern, message_lower):
            status_filter = "all"
            if "pending" in message_lower or "active" in message_lower or "incomplete" in message_lower:
                status_filter = "pending"
            elif "completed" in message_lower or "done" in message_lower or "finished" in message_lower:
                status_filter = "completed"
            return {"action": "list_tasks", "params": {"status": status_filter}}, ""

    # Complete task
    complete_patterns = [
        r"(?:complete|finish|done|mark).*task[:\s#]*(\d+)",
        r"task[:\s#]*(\d+).*(?:complete|done|finish)",
        r"mark[:\s#]*(\d+).*(?:complete|done)",
        r"complete[:\s#]*(\d+)",
        r"finish[:\s#]*(\d+)",
    ]
    for pattern in complete_patterns:
        match = re.search(pattern, message_lower)
        if match:
            task_id = int(match.group(1))
            return {"action": "complete_task", "params": {"task_id": task_id}}, ""

    # Delete task
    delete_patterns = [
        r"(?:delete|remove|cancel).*task[:\s#]*(\d+)",
        r"task[:\s#]*(\d+).*(?:delete|remove)",
        r"delete[:\s#]*(\d+)",
        r"remove[:\s#]*(\d+)",
    ]
    for pattern in delete_patterns:
        match = re.search(pattern, message_lower)
        if match:
            task_id = int(match.group(1))
            return {"action": "delete_task", "params": {"task_id": task_id}}, ""

    # Update task
    update_patterns = [
        r"(?:update|change|edit|rename).*task[:\s#]*(\d+).*(?:to|as|with)[:\s]+(.+)",
        r"task[:\s#]*(\d+).*(?:rename|change).*(?:to|as)[:\s]+(.+)",
    ]
    for pattern in update_patterns:
        match = re.search(pattern, message_lower)
        if match:
            task_id = int(match.group(1))
            new_title = match.group(2).strip()
            return {"action": "update_task", "params": {"task_id": task_id, "title": new_title.title()}}, ""

    # Default response
    return None, "I'm not sure what you'd like to do. Try:\n- 'add task [title]' to create a new task\n- 'show my tasks' to see all tasks\n- 'complete task [id]' to mark a task as done\n- 'delete task [id]' to remove a task\n\nOr say 'help' for more information!"


def execute_tool(
    tool_name: str,
    params: Dict[str, Any],
    user_id: str,
    session: Session
) -> Dict[str, Any]:
    """Execute a task tool and return the result."""

    try:
        if tool_name == "add_task":
            title = params.get("title", "").strip()
            description = params.get("description", "")

            if not title:
                return {"error": "Title is required", "status": "failed"}

            task = Task(
                user_id=user_id,
                title=title,
                description=description.strip() if description else None,
                completed=False,
                created_at=datetime.utcnow()
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "action": "add_task",
                "task_id": task.id,
                "title": task.title,
                "status": "created",
                "message": f"Task '{task.title}' created successfully! (ID: {task.id})"
            }

        elif tool_name == "list_tasks":
            status_filter = params.get("status", "all").lower()

            query = select(Task).where(Task.user_id == user_id)

            if status_filter == "pending":
                query = query.where(Task.completed == False)
            elif status_filter == "completed":
                query = query.where(Task.completed == True)

            query = query.order_by(Task.created_at.desc())
            tasks = session.exec(query).all()

            task_list = [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed
                }
                for t in tasks
            ]

            return {
                "action": "list_tasks",
                "tasks": task_list,
                "count": len(task_list),
                "filter": status_filter,
                "status": "success"
            }

        elif tool_name == "complete_task":
            task_id = params.get("task_id")
            if not task_id:
                return {"error": "task_id is required", "status": "failed"}

            task = session.exec(
                select(Task).where(
                    (Task.id == int(task_id)) & (Task.user_id == user_id)
                )
            ).first()

            if not task:
                return {"error": f"Task {task_id} not found", "status": "failed", "message": f"Task {task_id} not found. Use 'show my tasks' to see available tasks."}

            task.completed = True
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()

            return {
                "action": "complete_task",
                "task_id": task.id,
                "title": task.title,
                "completed": True,
                "status": "completed",
                "message": f"Task '{task.title}' marked as complete! Great job!"
            }

        elif tool_name == "delete_task":
            task_id = params.get("task_id")
            if not task_id:
                return {"error": "task_id is required", "status": "failed"}

            task = session.exec(
                select(Task).where(
                    (Task.id == int(task_id)) & (Task.user_id == user_id)
                )
            ).first()

            if not task:
                return {"error": f"Task {task_id} not found", "status": "failed", "message": f"Task {task_id} not found. Use 'show my tasks' to see available tasks."}

            title = task.title
            session.delete(task)
            session.commit()

            return {
                "action": "delete_task",
                "task_id": task_id,
                "title": title,
                "status": "deleted",
                "message": f"Task '{title}' has been deleted."
            }

        elif tool_name == "update_task":
            task_id = params.get("task_id")
            if not task_id:
                return {"error": "task_id is required", "status": "failed"}

            task = session.exec(
                select(Task).where(
                    (Task.id == int(task_id)) & (Task.user_id == user_id)
                )
            ).first()

            if not task:
                return {"error": f"Task {task_id} not found", "status": "failed", "message": f"Task {task_id} not found."}

            new_title = params.get("title")
            new_description = params.get("description")

            if new_title:
                task.title = new_title.strip()
            if new_description is not None:
                task.description = new_description.strip() if new_description else None

            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()

            return {
                "action": "update_task",
                "task_id": task.id,
                "title": task.title,
                "status": "updated",
                "message": f"Task updated to '{task.title}'."
            }

        else:
            return {"error": f"Unknown tool: {tool_name}", "status": "failed"}

    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        return {"error": str(e), "status": "failed"}


def format_list_tasks_response(result: Dict[str, Any]) -> str:
    """Format the list_tasks result into a readable message."""
    tasks = result.get("tasks", [])
    if not tasks:
        return "You don't have any tasks yet. Would you like to add one? Just say 'add task [title]'!"

    task_lines = []
    for t in tasks:
        status_emoji = "Done" if t['completed'] else "Pending"
        task_lines.append(f"[{t['id']}] {t['title']} - {status_emoji}")

    filter_text = result.get("filter", "all")
    header = f"Here are your {filter_text} tasks:\n\n"
    footer = f"\n\nTotal: {len(tasks)} task(s)"

    return header + "\n".join(task_lines) + footer


@router.post("/{user_id}", response_model=ChatResponse)
async def chat(
    user_id: str,
    chat_request: ChatRequest,
    session: Session = Depends(get_session),
    request: Request = None,
):
    """
    Chat with the AI assistant for task management.

    Uses Cohere AI for natural language understanding and tool calling.
    Falls back to mock pattern matching if Cohere is not configured.
    """
    # Verify user_id matches JWT token
    verify_user_id_match(request, user_id)

    try:
        # Get or create conversation
        conversation = get_or_create_conversation(
            session, user_id, chat_request.conversation_id
        )

        # Store user message
        user_message = create_message(
            session, user_id, conversation.id, "user", chat_request.message
        )

        # Get AI agent (Cohere or None for mock)
        agent = get_ai_agent()

        tool_calls_made = []
        final_response = ""

        if agent is not None:
            # Use Cohere agent with tool calling
            logger.info(f"Processing chat with Cohere for user {user_id}")

            # Get conversation history for context
            history = get_conversation_history(session, user_id, conversation.id)
            chat_history = [
                {"role": m.role, "content": m.content}
                for m in history[:-1]  # Exclude the current message we just added
            ]

            # Create tool executor that captures user_id and session
            def tool_executor(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
                return execute_tool(tool_name, parameters, user_id, session)

            # Execute with Cohere agent
            result = agent.execute_with_tools(
                message=chat_request.message,
                chat_history=chat_history,
                tool_executor=tool_executor,
                max_iterations=5
            )

            tool_calls_made = result.get("tool_calls", [])
            final_response = result.get("response", "")

            # If Cohere returned tool calls but no response, format results
            if tool_calls_made and not final_response:
                # Format response based on tool results
                for tc in tool_calls_made:
                    tool_result = tc.get("result", {})
                    if tc["tool_name"] == "list_tasks" and tool_result.get("status") == "success":
                        final_response = format_list_tasks_response(tool_result)
                    else:
                        final_response = tool_result.get("message", "Action completed.")
                        break

        else:
            # Use mock AI for pattern matching
            logger.info(f"Processing chat with mock AI for user {user_id}")

            action_data, response_text = mock_ai_response(chat_request.message)
            final_response = response_text

            # Execute action if found
            if action_data:
                action = action_data.get("action")
                params = action_data.get("params", {})

                logger.info(f"Mock AI executing tool: {action} with params: {params}")

                result = execute_tool(action, params, user_id, session)
                tool_calls_made.append({
                    "tool_name": action,
                    "parameters": params,
                    "result": result
                })

                # Format response based on action
                if action == "list_tasks" and result.get("status") == "success":
                    final_response = format_list_tasks_response(result)
                else:
                    # Use the message from the result
                    final_response = result.get("message", response_text)

        # Ensure we have a response
        if not final_response:
            final_response = "I processed your request. Is there anything else I can help you with?"

        # Store assistant message
        assistant_msg = create_message(
            session, user_id, conversation.id, "assistant", final_response
        )

        # Store tool calls if any
        if tool_calls_made:
            store_tool_calls(session, assistant_msg.id, tool_calls_made)

        logger.info(f"Chat completed for user {user_id}, conversation {conversation.id}")

        return ChatResponse(
            conversation_id=conversation.id,
            response=final_response,
            tool_calls=tool_calls_made
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing error: {str(e)}"
        )


@router.get("/{user_id}/conversations")
async def list_conversations(
    user_id: str,
    session: Session = Depends(get_session),
    request: Request = None,
):
    """List all conversations for a user."""
    verify_user_id_match(request, user_id)

    conversations = session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    ).all()

    return {
        "conversations": [
            {
                "id": c.id,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat()
            }
            for c in conversations
        ],
        "count": len(conversations)
    }


@router.get("/{user_id}/conversations/{conversation_id}/messages")
async def get_messages(
    user_id: str,
    conversation_id: int,
    session: Session = Depends(get_session),
    request: Request = None,
):
    """Get all messages in a conversation."""
    verify_user_id_match(request, user_id)

    # Verify conversation belongs to user
    conversation = session.exec(
        select(Conversation).where(
            (Conversation.id == conversation_id) &
            (Conversation.user_id == user_id)
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_id} not found"
        )

    messages = get_conversation_history(session, user_id, conversation_id)

    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ],
        "count": len(messages)
    }

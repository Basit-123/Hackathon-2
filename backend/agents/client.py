"""AI Agent client initialization - Cohere and OpenAI support."""

import logging
from typing import Optional, List, Dict, Any
import cohere
from openai import OpenAI
from .config import get_cohere_config, is_cohere_available, is_openai_available, get_agent_config

logger = logging.getLogger(__name__)

# Global client instances
_cohere_client: Optional[cohere.Client] = None
_openai_client: Optional[OpenAI] = None


def get_cohere_client() -> cohere.Client:
    """Get or initialize the Cohere client.

    Returns:
        cohere.Client: Initialized Cohere client

    Raises:
        ValueError: If COHERE_API_KEY is not set
    """
    global _cohere_client

    if _cohere_client is None:
        config = get_cohere_config()
        _cohere_client = cohere.Client(api_key=config["api_key"])
        logger.info(f"Cohere client initialized with model: {config['model']}")

    return _cohere_client


def get_openai_client() -> OpenAI:
    """Get or initialize the OpenAI client (legacy fallback).

    Returns:
        OpenAI: Initialized OpenAI client
    """
    global _openai_client

    if _openai_client is None:
        config = get_agent_config()
        if config.get("provider") != "openai":
            raise ValueError("OpenAI is not configured")
        _openai_client = OpenAI(api_key=config["api_key"])
        logger.info(f"OpenAI client initialized with model: {config['model']}")

    return _openai_client


# MCP Tool definitions for Cohere's tool calling format
TASK_TOOLS = [
    {
        "name": "add_task",
        "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something as a task.",
        "parameter_definitions": {
            "title": {
                "type": "str",
                "description": "The title or name of the task to create",
                "required": True
            },
            "description": {
                "type": "str",
                "description": "Optional description with more details about the task",
                "required": False
            }
        }
    },
    {
        "name": "list_tasks",
        "description": "List the user's tasks. Use this when the user wants to see, view, show, or check their tasks.",
        "parameter_definitions": {
            "status": {
                "type": "str",
                "description": "Filter tasks by status: 'all' (default), 'pending' (incomplete), or 'completed' (done)",
                "required": False
            }
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed. Use this when the user says they finished, completed, or done with a task.",
        "parameter_definitions": {
            "task_id": {
                "type": "int",
                "description": "The ID number of the task to mark as complete",
                "required": True
            }
        }
    },
    {
        "name": "delete_task",
        "description": "Delete a task permanently. Use this when the user wants to remove, delete, or cancel a task.",
        "parameter_definitions": {
            "task_id": {
                "type": "int",
                "description": "The ID number of the task to delete",
                "required": True
            }
        }
    },
    {
        "name": "update_task",
        "description": "Update a task's title or description. Use this when the user wants to change, edit, rename, or modify a task.",
        "parameter_definitions": {
            "task_id": {
                "type": "int",
                "description": "The ID number of the task to update",
                "required": True
            },
            "title": {
                "type": "str",
                "description": "The new title for the task",
                "required": False
            },
            "description": {
                "type": "str",
                "description": "The new description for the task",
                "required": False
            }
        }
    }
]

# System preamble for Cohere
SYSTEM_PREAMBLE = """You are a helpful task management assistant. Your job is to help users manage their todo tasks through natural conversation.

You can perform these actions:
- Add new tasks when users want to create or remember something
- List tasks (all, pending only, or completed only)
- Mark tasks as complete when users finish them
- Delete tasks when users want to remove them
- Update tasks when users want to change their title or description

Guidelines:
1. Always use the appropriate tool when the user wants to perform a task action
2. Be friendly and confirm actions after completing them
3. When listing tasks, format them clearly
4. If a task ID is mentioned, use it; if not and context is unclear, ask for clarification
5. Use emojis sparingly to make responses more engaging

Examples of user intents:
- "add task buy groceries" -> use add_task with title "Buy groceries"
- "show my tasks" -> use list_tasks with status "all"
- "what's pending?" -> use list_tasks with status "pending"
- "mark task 3 as done" -> use complete_task with task_id 3
- "delete task 5" -> use delete_task with task_id 5
- "change task 2 to call mom" -> use update_task with task_id 2 and title "Call mom"
"""


class CohereAgent:
    """Cohere-powered task management agent with tool calling support."""

    def __init__(self):
        """Initialize the Cohere agent."""
        self.client = get_cohere_client()
        self.config = get_cohere_config()
        self.model = self.config["model"]
        self.tools = TASK_TOOLS
        self.preamble = SYSTEM_PREAMBLE

    def chat(
        self,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        tool_results: Optional[List[Dict[str, Any]]] = None
    ) -> cohere.ChatResponse:
        """Send a message to Cohere and get a response.

        Args:
            message: The user's message
            chat_history: Previous conversation messages
            tool_results: Results from previously called tools

        Returns:
            cohere.ChatResponse: The model's response
        """
        # Build chat history in Cohere format
        formatted_history = []
        if chat_history:
            for msg in chat_history:
                role = "USER" if msg.get("role") == "user" else "CHATBOT"
                formatted_history.append({
                    "role": role,
                    "message": msg.get("content", "")
                })

        # Make API call
        response = self.client.chat(
            model=self.model,
            message=message,
            preamble=self.preamble,
            tools=self.tools,
            chat_history=formatted_history if formatted_history else None,
            tool_results=tool_results,
        )

        return response

    def execute_with_tools(
        self,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        tool_executor: Optional[callable] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """Execute a chat with automatic tool calling loop.

        Args:
            message: The user's message
            chat_history: Previous conversation messages
            tool_executor: Function to execute tools (receives tool_name, parameters)
            max_iterations: Maximum number of tool calling iterations

        Returns:
            dict: Contains 'response' (final text) and 'tool_calls' (list of executed tools)
        """
        tool_calls_made = []
        current_message = message
        tool_results = None
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            # Get response from Cohere
            response = self.chat(
                message=current_message,
                chat_history=chat_history,
                tool_results=tool_results
            )

            # Check if there are tool calls to execute
            if response.tool_calls:
                tool_results = []

                for tool_call in response.tool_calls:
                    tool_name = tool_call.name
                    parameters = tool_call.parameters or {}

                    logger.info(f"Executing tool: {tool_name} with params: {parameters}")

                    # Execute the tool
                    if tool_executor:
                        result = tool_executor(tool_name, parameters)
                    else:
                        result = {"error": "No tool executor provided"}

                    tool_calls_made.append({
                        "tool_name": tool_name,
                        "parameters": dict(parameters),
                        "result": result
                    })

                    # Format result for Cohere
                    tool_results.append({
                        "call": tool_call,
                        "outputs": [result]
                    })

                # Continue the conversation with tool results
                current_message = ""
            else:
                # No more tool calls, return final response
                return {
                    "response": response.text,
                    "tool_calls": tool_calls_made,
                    "finish_reason": response.finish_reason
                }

        # Max iterations reached
        return {
            "response": response.text if response else "I couldn't complete your request. Please try again.",
            "tool_calls": tool_calls_made,
            "finish_reason": "max_iterations"
        }


def get_agent() -> CohereAgent:
    """Get an initialized agent instance.

    Returns:
        CohereAgent: Initialized Cohere agent

    Raises:
        ValueError: If no API keys are configured
    """
    if is_cohere_available():
        return CohereAgent()
    elif is_openai_available():
        # Could implement OpenAI agent here as fallback
        raise NotImplementedError("OpenAI agent not implemented - use Cohere")
    else:
        raise ValueError("No AI provider configured. Set COHERE_API_KEY environment variable.")


# Legacy function for backward compatibility
def initialize_agent():
    """Legacy function - returns CohereAgent if available."""
    return get_agent()

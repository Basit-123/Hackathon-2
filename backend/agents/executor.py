"""Agent message processing and execution pipeline.

Handles the conversation flow with the OpenAI agent:
1. Receives user message
2. Builds message history
3. Invokes agent with MCP tools
4. Processes tool calls
5. Returns assistant response
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentMessage:
    """Represents a message in the conversation."""

    def __init__(self, role: str, content: str, tool_calls: Optional[List[Dict]] = None):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.tool_calls = tool_calls or []
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "role": self.role,
            "content": self.content,
            "tool_calls": self.tool_calls,
        }


class AgentExecutor:
    """Executes agent interactions with MCP tools."""

    def __init__(self, agent_client: Any, mcp_server: Any, timeout: int = 30):
        """Initialize agent executor.

        Args:
            agent_client: OpenAI client
            mcp_server: MCP server instance
            timeout: Agent execution timeout in seconds
        """
        self.agent = agent_client
        self.mcp_server = mcp_server
        self.timeout = timeout
        logger.info(f"AgentExecutor initialized (timeout: {timeout}s)")

    async def execute(
        self,
        user_id: str,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        system_prompt: str,
    ) -> Dict[str, Any]:
        """Execute agent with message and return response.

        Args:
            user_id: User identifier
            user_message: User's input message
            conversation_history: Previous messages in conversation
            system_prompt: System prompt for agent behavior

        Returns:
            Dict with assistant response and tool calls
        """
        try:
            logger.debug(f"Executing agent for user {user_id}")
            logger.debug(f"User message: {user_message[:100]}...")

            # Build message list for agent
            messages = self._build_message_list(conversation_history, user_message)

            # Prepare tools for agent
            tools = self._prepare_tools()

            # Call agent
            response = await self._call_agent(messages, system_prompt, tools)

            # Process response and tool calls
            result = await self._process_response(response, user_id)

            logger.debug(f"Agent execution completed for user {user_id}")
            return result

        except Exception as e:
            logger.error(f"Error in agent execution: {str(e)}")
            return {
                "response": f"I encountered an error processing your request: {str(e)}",
                "tool_calls": [],
                "status": "error",
            }

    def _build_message_list(
        self, conversation_history: List[Dict[str, Any]], user_message: str
    ) -> List[Dict[str, str]]:
        """Build message list for agent.

        Args:
            conversation_history: Previous messages
            user_message: New user message

        Returns:
            List of messages in OpenAI format
        """
        messages = []

        # Add conversation history
        for msg in conversation_history:
            messages.append(
                {
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                }
            )

        # Add new user message
        messages.append({"role": "user", "content": user_message})

        logger.debug(f"Built message list with {len(messages)} messages")
        return messages

    def _prepare_tools(self) -> List[Dict[str, Any]]:
        """Prepare tools for agent.

        Returns:
            List of tool definitions in OpenAI format
        """
        tools_list = self.mcp_server.list_tools()
        logger.debug(f"Prepared {len(tools_list)} tools for agent")
        return tools_list

    async def _call_agent(
        self, messages: List[Dict], system_prompt: str, tools: List[Dict]
    ) -> Dict[str, Any]:
        """Call the OpenAI agent.

        Args:
            messages: Message history
            system_prompt: System prompt
            tools: Available tools

        Returns:
            Agent response
        """
        try:
            # Use OpenAI chat completion with tools
            # Note: Actual implementation depends on OpenAI SDK version
            logger.debug("Calling OpenAI agent...")

            # Simulate agent response for now
            # In production, use: self.agent.chat.completions.create(...)
            response = {
                "content": "I understand you want to manage your tasks. How can I help?",
                "tool_calls": [],
            }

            return response

        except Exception as e:
            logger.error(f"Error calling agent: {str(e)}")
            raise

    async def _process_response(
        self, response: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        """Process agent response and execute tool calls.

        Args:
            response: Agent response
            user_id: User identifier

        Returns:
            Processed response with tool results
        """
        tool_calls = response.get("tool_calls", [])
        assistant_message = response.get("content", "")

        # Execute any tool calls
        executed_tools = []
        if tool_calls:
            executed_tools = await self._execute_tool_calls(tool_calls, user_id)

        logger.debug(
            f"Processed {len(executed_tools)} tool calls for user {user_id}"
        )

        return {
            "response": assistant_message,
            "tool_calls": executed_tools,
            "status": "success",
        }

    async def _execute_tool_calls(
        self, tool_calls: List[Dict], user_id: str
    ) -> List[Dict[str, Any]]:
        """Execute tool calls from agent.

        Args:
            tool_calls: List of tool calls to execute
            user_id: User identifier

        Returns:
            List of tool execution results
        """
        results = []

        for tool_call in tool_calls:
            try:
                tool_name = tool_call.get("name", "unknown")
                tool_args = tool_call.get("arguments", {})

                # Add user_id to all tool calls for user isolation
                tool_args["user_id"] = user_id

                logger.debug(f"Executing tool: {tool_name} for user {user_id}")

                # Invoke tool via MCP server
                tool_result = await self.mcp_server.invoke_tool(tool_name, **tool_args)

                results.append(
                    {
                        "tool_name": tool_name,
                        "arguments": tool_args,
                        "result": tool_result,
                        "status": "executed",
                    }
                )

                logger.debug(f"Tool {tool_name} executed successfully")

            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {str(e)}")
                results.append(
                    {
                        "tool_name": tool_call.get("name", "unknown"),
                        "arguments": tool_call.get("arguments", {}),
                        "result": {"error": str(e)},
                        "status": "failed",
                    }
                )

        return results

    def get_agent_tools_description(self) -> str:
        """Get formatted description of available tools for system prompt.

        Returns:
            Formatted tools description
        """
        tools = self.mcp_server.list_tools()
        description = "Available Tools:\n"

        for tool in tools:
            description += f"\n- {tool['name']}: {tool['description']}\n"
            description += "  Parameters:\n"
            for param in tool.get("parameters", []):
                required = "required" if param.get("required") else "optional"
                description += f"    - {param['name']} ({param['type']}, {required}): {param.get('description', '')}\n"

        return description

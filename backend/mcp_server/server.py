"""MCP Server implementation for task management tools.

This server exposes MCP tools for the OpenAI Agents SDK to manage tasks.
Tools are invoked by the AI agent based on natural language intent.
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class MCPToolParameter:
    """Represents a parameter for an MCP tool."""

    def __init__(self, name: str, type_: str, required: bool = True, description: str = ""):
        self.name = name
        self.type = type_
        self.required = required
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "description": self.description,
        }


class MCPTool:
    """Represents an MCP tool that can be invoked by the agent."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: List[MCPToolParameter],
        handler: Callable,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
        }

    async def invoke(self, **kwargs) -> Dict[str, Any]:
        """Invoke the tool with the given parameters."""
        return await self.handler(**kwargs)


class MCPServer:
    """MCP Server for exposing task management tools to AI agents."""

    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.db_session = None
        logger.info("MCP Server initialized")

    def register_tool(self, tool: MCPTool) -> None:
        """Register an MCP tool with the server."""
        self.tools[tool.name] = tool
        logger.info(f"Registered MCP tool: {tool.name}")

    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools."""
        return [tool.to_dict() for tool in self.tools.values()]

    async def invoke_tool(self, tool_name: str, **params) -> Dict[str, Any]:
        """Invoke a tool by name with the given parameters.

        Args:
            tool_name: Name of the tool to invoke
            **params: Tool parameters

        Returns:
            Tool result dictionary
        """
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found", "status": "error"}

        tool = self.tools[tool_name]
        try:
            logger.debug(f"Invoking tool '{tool_name}' with params: {params}")
            result = await tool.invoke(**params)
            logger.debug(f"Tool '{tool_name}' result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error invoking tool {tool_name}: {str(e)}")
            return {
                "error": str(e),
                "tool": tool_name,
                "status": "error"
            }

    def set_db_session(self, session: Any) -> None:
        """Set the database session for tool handlers."""
        self.db_session = session
        logger.info("Database session configured for MCP Server")

    async def initialize(self) -> None:
        """Initialize MCP server (setup hooks)."""
        logger.info("MCP Server initializing")

    async def shutdown(self) -> None:
        """Shutdown MCP server (cleanup hooks)."""
        if self.db_session:
            self.db_session.close()
        logger.info("MCP Server shutdown")


# Global MCP server instance
_mcp_server: Optional[MCPServer] = None


def create_mcp_server() -> MCPServer:
    """Create and return the global MCP server instance."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server


def get_mcp_server() -> MCPServer:
    """Get the global MCP server instance."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = create_mcp_server()
    return _mcp_server

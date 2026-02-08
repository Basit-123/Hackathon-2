"""Factory for creating configured agent instances."""

import logging
from typing import Optional
from sqlmodel import Session

from .client import get_agent
from .executor import AgentExecutor
from .prompts import get_system_prompt
from .config import get_agent_config
from mcp_server.server import get_mcp_server
from mcp_server.handlers import register_task_tools

logger = logging.getLogger(__name__)


def create_agent_executor(
    db_session: Session, timeout: Optional[int] = None
) -> AgentExecutor:
    """Create a fully configured agent executor.

    This factory function:
    1. Initializes the OpenAI agent client
    2. Creates/gets the MCP server
    3. Registers MCP tools with database session
    4. Creates and returns an AgentExecutor

    Args:
        db_session: SQLModel database session
        timeout: Optional timeout override (seconds)

    Returns:
        Configured AgentExecutor instance
    """
    logger.info("Creating agent executor...")

    # Get OpenAI agent
    agent = get_agent()
    logger.debug("OpenAI agent initialized")

    # Get MCP server
    mcp_server = get_mcp_server()
    logger.debug("MCP server retrieved")

    # Register tools if not already registered
    if len(mcp_server.tools) == 0:
        register_task_tools(db_session)
        logger.info(f"Registered {len(mcp_server.tools)} MCP tools")
    else:
        logger.debug(f"Tools already registered: {len(mcp_server.tools)}")

    # Set database session
    mcp_server.set_db_session(db_session)
    logger.debug("Database session configured in MCP server")

    # Get timeout from config or use override
    config = get_agent_config()
    final_timeout = timeout or config.get("timeout", 30)

    # Create executor
    executor = AgentExecutor(agent, mcp_server, timeout=final_timeout)
    logger.info(f"Agent executor created (timeout: {final_timeout}s)")

    return executor


def get_system_configuration() -> dict:
    """Get complete system configuration for agent setup.

    Returns:
        Dict with agent configuration, system prompt, and tools info
    """
    config = get_agent_config()
    mcp_server = get_mcp_server()
    system_prompt = get_system_prompt()

    return {
        "agent_model": config.get("model"),
        "agent_timeout": config.get("timeout"),
        "agent_max_iterations": config.get("max_iterations"),
        "system_prompt": system_prompt,
        "tools_available": len(mcp_server.tools),
        "tools": [tool["name"] for tool in mcp_server.list_tools()],
    }


def verify_agent_setup() -> bool:
    """Verify that the agent is properly configured.

    Returns:
        True if all components are ready, False otherwise
    """
    try:
        # Check agent client
        agent = get_agent()
        if not agent:
            logger.error("Agent client not initialized")
            return False
        logger.debug("Agent client verified")

        # Check MCP server
        mcp_server = get_mcp_server()
        if not mcp_server:
            logger.error("MCP server not initialized")
            return False
        logger.debug("MCP server verified")

        # Check system prompt
        prompt = get_system_prompt()
        if not prompt or len(prompt) == 0:
            logger.error("System prompt not loaded")
            return False
        logger.debug(f"System prompt verified ({len(prompt)} characters)")

        logger.info("Agent setup verification complete - all systems ready")
        return True

    except Exception as e:
        logger.error(f"Agent setup verification failed: {str(e)}")
        return False

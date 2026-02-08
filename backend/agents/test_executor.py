"""Unit tests for agent executor.

Tests the message processing and tool invocation pipeline.
Run with: pytest backend/agents/test_executor.py -v
"""

import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime
from .executor import AgentExecutor, AgentMessage


@pytest.fixture
def mock_agent_client():
    """Create a mock OpenAI agent client."""
    return Mock()


@pytest.fixture
def mock_mcp_server():
    """Create a mock MCP server."""
    server = Mock()
    server.list_tools.return_value = [
        {
            "name": "add_task",
            "description": "Create a new task",
            "parameters": [
                {"name": "user_id", "type": "string", "required": True},
                {"name": "title", "type": "string", "required": True},
            ],
        }
    ]
    server.invoke_tool = AsyncMock()
    return server


@pytest.fixture
def agent_executor(mock_agent_client, mock_mcp_server):
    """Create an agent executor with mocks."""
    return AgentExecutor(mock_agent_client, mock_mcp_server, timeout=30)


class TestAgentMessage:
    """Tests for AgentMessage class."""

    def test_agent_message_creation(self):
        """Test creating an agent message."""
        msg = AgentMessage("user", "Hello, assistant!")
        assert msg.role == "user"
        assert msg.content == "Hello, assistant!"
        assert msg.tool_calls == []
        assert isinstance(msg.timestamp, datetime)

    def test_agent_message_with_tool_calls(self):
        """Test agent message with tool calls."""
        tool_calls = [{"name": "add_task", "arguments": {"title": "Test"}}]
        msg = AgentMessage("assistant", "Creating task", tool_calls)
        assert msg.role == "assistant"
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0]["name"] == "add_task"

    def test_agent_message_to_dict(self):
        """Test converting message to dictionary."""
        msg = AgentMessage("user", "Test message")
        msg_dict = msg.to_dict()
        assert msg_dict["role"] == "user"
        assert msg_dict["content"] == "Test message"
        assert msg_dict["tool_calls"] == []


class TestAgentExecutorInit:
    """Tests for AgentExecutor initialization."""

    def test_executor_initialization(self, agent_executor):
        """Test executor initializes with correct values."""
        assert agent_executor.agent is not None
        assert agent_executor.mcp_server is not None
        assert agent_executor.timeout == 30

    def test_executor_custom_timeout(self, mock_agent_client, mock_mcp_server):
        """Test executor with custom timeout."""
        executor = AgentExecutor(mock_agent_client, mock_mcp_server, timeout=60)
        assert executor.timeout == 60


class TestBuildMessageList:
    """Tests for message list building."""

    def test_build_empty_history(self, agent_executor):
        """Test building message list with empty history."""
        messages = agent_executor._build_message_list([], "Hello")
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"

    def test_build_with_history(self, agent_executor):
        """Test building message list with conversation history."""
        history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "Response"},
        ]
        messages = agent_executor._build_message_list(history, "Second message")
        assert len(messages) == 3
        assert messages[-1]["content"] == "Second message"

    def test_build_preserves_roles(self, agent_executor):
        """Test that roles are preserved in message list."""
        history = [
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant message"},
        ]
        messages = agent_executor._build_message_list(history, "Another user message")
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["role"] == "user"


class TestPrepareTools:
    """Tests for tool preparation."""

    def test_prepare_tools(self, agent_executor):
        """Test preparing tools for agent."""
        tools = agent_executor._prepare_tools()
        assert len(tools) > 0
        assert "name" in tools[0]
        assert "description" in tools[0]
        assert "parameters" in tools[0]

    def test_tools_have_parameters(self, agent_executor):
        """Test that tools include parameter information."""
        tools = agent_executor._prepare_tools()
        assert len(tools[0]["parameters"]) > 0


class TestGetToolsDescription:
    """Tests for tools description generation."""

    def test_get_tools_description(self, agent_executor):
        """Test generating tools description."""
        description = agent_executor.get_agent_tools_description()
        assert "Available Tools:" in description
        assert "add_task" in description
        assert "Parameters:" in description

    def test_description_includes_parameters(self, agent_executor):
        """Test that description includes parameter details."""
        description = agent_executor.get_agent_tools_description()
        assert "user_id" in description
        assert "title" in description
        assert "required" in description or "optional" in description


class TestExecuteToolCalls:
    """Tests for tool call execution."""

    @pytest.mark.asyncio
    async def test_execute_single_tool_call(self, agent_executor, mock_mcp_server):
        """Test executing a single tool call."""
        mock_mcp_server.invoke_tool.return_value = {"task_id": 1, "status": "created"}

        tool_calls = [
            {
                "name": "add_task",
                "arguments": {"title": "Test Task"},
            }
        ]

        results = await agent_executor._execute_tool_calls(tool_calls, "user123")

        assert len(results) == 1
        assert results[0]["tool_name"] == "add_task"
        assert results[0]["status"] == "executed"
        assert mock_mcp_server.invoke_tool.called

    @pytest.mark.asyncio
    async def test_execute_multiple_tool_calls(self, agent_executor, mock_mcp_server):
        """Test executing multiple tool calls."""
        mock_mcp_server.invoke_tool.return_value = {"status": "success"}

        tool_calls = [
            {"name": "add_task", "arguments": {"title": "Task 1"}},
            {"name": "list_tasks", "arguments": {"status": "all"}},
        ]

        results = await agent_executor._execute_tool_calls(tool_calls, "user123")

        assert len(results) == 2
        assert results[0]["tool_name"] == "add_task"
        assert results[1]["tool_name"] == "list_tasks"

    @pytest.mark.asyncio
    async def test_execute_tool_call_adds_user_id(self, agent_executor, mock_mcp_server):
        """Test that user_id is added to tool arguments."""
        mock_mcp_server.invoke_tool.return_value = {"status": "success"}

        tool_calls = [
            {
                "name": "add_task",
                "arguments": {"title": "Test"},
            }
        ]

        await agent_executor._execute_tool_calls(tool_calls, "test_user")

        # Verify invoke_tool was called with user_id
        call_args = mock_mcp_server.invoke_tool.call_args
        assert "user_id" in call_args.kwargs
        assert call_args.kwargs["user_id"] == "test_user"

    @pytest.mark.asyncio
    async def test_execute_tool_call_error_handling(
        self, agent_executor, mock_mcp_server
    ):
        """Test error handling during tool execution."""
        mock_mcp_server.invoke_tool.side_effect = Exception("Tool error")

        tool_calls = [
            {
                "name": "add_task",
                "arguments": {"title": "Test"},
            }
        ]

        results = await agent_executor._execute_tool_calls(tool_calls, "user123")

        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert "error" in results[0]["result"]


class TestProcessResponse:
    """Tests for response processing."""

    @pytest.mark.asyncio
    async def test_process_response_without_tool_calls(self, agent_executor):
        """Test processing response without tool calls."""
        response = {"content": "Hello, how can I help?", "tool_calls": []}

        result = await agent_executor._process_response(response, "user123")

        assert result["status"] == "success"
        assert result["response"] == "Hello, how can I help?"
        assert result["tool_calls"] == []

    @pytest.mark.asyncio
    async def test_process_response_missing_content(self, agent_executor):
        """Test processing response with missing content."""
        response = {"tool_calls": []}

        result = await agent_executor._process_response(response, "user123")

        assert result["response"] == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

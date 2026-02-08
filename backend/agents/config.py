"""Configuration for AI Agents - Cohere API."""

import os
from typing import Optional

# Cohere configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-a-03-2025")

# Agent configuration
AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "30"))
AGENT_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))

# Legacy OpenAI configuration (kept for backward compatibility)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4-turbo")


def get_cohere_config() -> dict:
    """Get the Cohere agent configuration dictionary.

    Returns:
        dict: Configuration with api_key, model, timeout, and max_iterations

    Raises:
        ValueError: If COHERE_API_KEY environment variable is not set
    """
    if not COHERE_API_KEY:
        raise ValueError("COHERE_API_KEY environment variable is required")

    return {
        "api_key": COHERE_API_KEY,
        "model": COHERE_MODEL,
        "timeout": AGENT_TIMEOUT,
        "max_iterations": AGENT_MAX_ITERATIONS,
    }


def get_agent_config() -> dict:
    """Get the agent configuration dictionary.

    Prefers Cohere if available, falls back to OpenAI.

    Returns:
        dict: Configuration with api_key, model, timeout, and max_iterations
    """
    # Try Cohere first
    if COHERE_API_KEY:
        return {
            "provider": "cohere",
            "api_key": COHERE_API_KEY,
            "model": COHERE_MODEL,
            "timeout": AGENT_TIMEOUT,
            "max_iterations": AGENT_MAX_ITERATIONS,
        }

    # Fall back to OpenAI
    if OPENAI_API_KEY:
        return {
            "provider": "openai",
            "api_key": OPENAI_API_KEY,
            "model": AGENT_MODEL,
            "timeout": AGENT_TIMEOUT,
            "max_iterations": AGENT_MAX_ITERATIONS,
        }

    raise ValueError("Either COHERE_API_KEY or OPENAI_API_KEY environment variable is required")


def is_cohere_available() -> bool:
    """Check if Cohere API is configured."""
    return bool(COHERE_API_KEY)


def is_openai_available() -> bool:
    """Check if OpenAI API is configured."""
    return bool(OPENAI_API_KEY)

"""
Platform agent implementation with tool calling capabilities
"""

import json
from typing import Any, Optional

from loguru import logger

from app.agent.toolcall import ToolCallAgent
from app.schema import Function, Message, ToolCall, ToolDefinition
from app.tools.collection import ToolCollection
from app.prompts import PLATFORM_AGENT_SYSTEM_PROMPT


class PlatformAgent(ToolCallAgent):
    """
    Main platform agent with tool calling capabilities

    Features:
    - Autonomous task execution
    - Tool/function calling
    - Multi-step reasoning
    - Memory management
    """

    max_observation_length: int = 10000

    def __init__(self, **data):
        # Set default system prompt if not provided
        if "system_prompt" not in data:
            data["system_prompt"] = PLATFORM_AGENT_SYSTEM_PROMPT

        # Initialize with all available tools
        if "tool_collection" not in data:
            from app.tools import get_all_tools

            data["tool_collection"] = ToolCollection()
            for tool in get_all_tools():
                data["tool_collection"].add_tool(tool)

        super().__init__(**data)

    @classmethod
    async def create(
        cls,
        name: str = "PlatformAgent",
        description: str = "General-purpose autonomous AI agent",
        system_prompt: Optional[str] = None,
        max_steps: int = 20,
    ) -> "PlatformAgent":
        """
        Factory method to create a platform agent

        Args:
            name: Agent name
            description: Agent description
            system_prompt: Custom system prompt
            max_steps: Maximum execution steps

        Returns:
            Initialized PlatformAgent
        """
        if system_prompt is None:
            system_prompt = PLATFORM_AGENT_SYSTEM_PROMPT

        agent = cls(
            name=name,
            description=description,
            system_prompt=system_prompt,
            max_steps=max_steps,
        )

        logger.info(f"Created {name} with {len(agent.tool_collection.tools)} tools")
        return agent

    # Platform agent now inherits all functionality from ToolCallAgent
    # No need to override methods unless we want specialized behavior

"""
Platform agent implementation with tool calling capabilities
"""

import json
from typing import Any, Optional

from loguru import logger

from app.agent.base import Agent
from app.schema import Function, Message, ToolCall, ToolDefinition
from app.tools.collection import ToolCollection


class PlatformAgent(Agent):
    """
    Main platform agent with tool calling capabilities

    Features:
    - Autonomous task execution
    - Tool/function calling
    - Multi-step reasoning
    - Memory management
    """

    tool_collection: Optional[ToolCollection] = None
    max_observation_length: int = 10000

    def __init__(self, **data):
        super().__init__(**data)
        # Initialize tool collection
        from app.tools.collection import get_tool_collection

        self.tool_collection = get_tool_collection()

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
            system_prompt = cls._get_default_system_prompt()

        agent = cls(
            name=name,
            description=description,
            system_prompt=system_prompt,
            max_steps=max_steps,
        )

        logger.info(f"Created {name} with {len(agent.tool_collection.tools)} tools")
        return agent

    @staticmethod
    def _get_default_system_prompt() -> str:
        """Get default system prompt for the agent"""
        return """You are a capable AI assistant that can help users accomplish various tasks.

You have access to various tools that you can use to complete tasks. When you need to perform an action, call the appropriate tool with the required parameters.

Key principles:
1. Break down complex tasks into smaller steps
2. Use tools when needed to accomplish tasks
3. Provide clear explanations of what you're doing
4. Ask for clarification if something is unclear
5. Be thorough and accurate in your work

When you complete a task, provide a clear summary of what was accomplished."""

    async def step(self) -> dict[str, Any]:
        """
        Execute one reasoning step

        Returns:
            Dictionary with execution results
        """
        try:
            # Get tool definitions
            tool_defs = self._get_tool_definitions()

            # Call LLM with tools
            llm = self.get_llm()
            messages = self.memory.get_messages()

            response = llm.ask(
                messages=messages,
                tools=tool_defs if tool_defs else None,
                tool_choice="auto" if tool_defs else None,
            )

            # Add response to memory
            self.memory.add_message(response)

            # Check if there are tool calls
            if response.tool_calls:
                logger.info(
                    f"Agent calling {len(response.tool_calls)} tool(s): {[tc.function.name for tc in response.tool_calls]}"
                )
                await self._execute_tool_calls(response.tool_calls)
                return {"done": False, "action": "tool_calls"}

            # No tool calls - check if we have a final response
            if response.content:
                logger.info("Agent provided final response")
                return {"done": True, "response": response.content}

            # Should not reach here
            logger.warning("Agent response has no content or tool calls")
            return {"done": True, "response": "I'm not sure how to proceed."}

        except Exception as e:
            logger.error(f"Error in agent step: {str(e)}")
            self.update_memory(
                "system", f"An error occurred: {str(e)}. Please try again."
            )
            return {"done": False, "action": "error", "error": str(e)}

    def _get_tool_definitions(self) -> list[ToolDefinition]:
        """Get tool definitions for LLM"""
        if not self.tool_collection:
            return []

        definitions = []
        for tool in self.tool_collection.tools:
            definitions.append(
                ToolDefinition(
                    type="function",
                    function={
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                )
            )

        return definitions

    async def _execute_tool_calls(self, tool_calls: list[ToolCall]) -> None:
        """Execute tool calls and add results to memory"""
        for tool_call in tool_calls:
            try:
                # Parse arguments
                args = json.loads(tool_call.function.arguments)

                # Execute tool
                logger.debug(
                    f"Executing tool: {tool_call.function.name} with args: {args}"
                )
                result = await self.tool_collection.execute_tool(
                    tool_call.function.name, args
                )

                # Truncate long observations
                result_str = str(result)
                if len(result_str) > self.max_observation_length:
                    result_str = (
                        result_str[: self.max_observation_length]
                        + f"\n... (truncated {len(result_str) - self.max_observation_length} characters)"
                    )

                # Add tool result to memory
                self.update_memory(
                    "tool",
                    content=result_str,
                    tool_call_id=tool_call.id,
                    name=tool_call.function.name,
                )

                logger.info(f"Tool {tool_call.function.name} executed successfully")

            except Exception as e:
                logger.error(f"Error executing tool {tool_call.function.name}: {str(e)}")
                # Add error to memory
                self.update_memory(
                    "tool",
                    content=f"Error: {str(e)}",
                    tool_call_id=tool_call.id,
                    name=tool_call.function.name,
                )

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.tool_collection:
            await self.tool_collection.cleanup()
        logger.info(f"Agent {self.name} cleaned up")

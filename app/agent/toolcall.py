"""
ToolCall agent implementation with function calling capabilities
"""

import json
from typing import Any, Optional

from loguru import logger

from app.agent.react import ReActAgent
from app.exceptions import ToolExecutionError, TokenLimitExceeded
from app.schema import AgentState, Message, ToolChoice, ToolDefinition
from app.tools.collection import ToolCollection


class ToolCallAgent(ReActAgent):
    """
    Agent that uses tool/function calling to accomplish tasks

    Extends ReAct agent to use LLM function calling for tool selection
    """

    tool_collection: Optional[ToolCollection] = None
    tool_choice: ToolChoice = ToolChoice.AUTO
    max_observation_length: int = 10000

    def __init__(self, **data):
        super().__init__(**data)
        # Initialize tool collection if not provided
        if self.tool_collection is None:
            from app.tools.collection import get_tool_collection

            self.tool_collection = get_tool_collection()

    async def think(self) -> dict[str, Any]:
        """
        Use LLM with tool calling to decide next action

        Returns:
            Thought with tool calls or final response
        """
        try:
            # Get tool definitions
            tool_defs = self._get_tool_definitions()

            # Get LLM response with tools
            llm = self.get_llm()
            messages = self.memory.get_messages()

            # Determine tool choice
            tool_choice_str = None
            if self.tool_choice == ToolChoice.NONE:
                tool_choice_str = "none"
            elif self.tool_choice == ToolChoice.REQUIRED:
                tool_choice_str = "required"
            elif self.tool_choice == ToolChoice.AUTO:
                tool_choice_str = "auto"

            response = llm.ask(
                messages=messages,
                tools=tool_defs if tool_defs else None,
                tool_choice=tool_choice_str if tool_defs else None,
            )

            # Add response to memory
            self.memory.add_message(response)

            # Check if there are tool calls
            if response.tool_calls:
                logger.info(
                    f"Agent decided to call {len(response.tool_calls)} tool(s): "
                    f"{[tc.function.name for tc in response.tool_calls]}"
                )
                return {
                    "done": False,
                    "tool_calls": response.tool_calls,
                    "action": "tool_calls",
                }

            # No tool calls - check for final response
            if response.content:
                logger.info("Agent provided final response")
                return {"done": True, "response": response.content, "action": "response"}

            # No content or tool calls
            logger.warning("Agent response has no content or tool calls")
            return {"done": True, "response": "No response generated", "action": "empty"}

        except TokenLimitExceeded as e:
            logger.error(f"Token limit exceeded: {str(e)}")
            self.state = AgentState.ERROR
            return {"done": True, "response": f"Token limit exceeded: {str(e)}", "error": True}
        except Exception as e:
            logger.error(f"Error in think phase: {str(e)}")
            raise

    async def act(self, thought: dict[str, Any]) -> dict[str, Any]:
        """
        Execute tool calls decided in think phase

        Args:
            thought: Thought containing tool calls

        Returns:
            Action result with observations
        """
        tool_calls = thought.get("tool_calls", [])
        if not tool_calls:
            return {"done": False, "observation": "No tools to execute", "action": "none"}

        observations = []

        for tool_call in tool_calls:
            try:
                # Execute tool
                observation = await self.execute_tool(tool_call)
                observations.append(observation)

                # Add tool result to memory
                self.update_memory(
                    "tool",
                    content=observation,
                    tool_call_id=tool_call.id,
                    name=tool_call.function.name,
                )

                # Check if this is a special tool (like terminate)
                if await self._handle_special_tool(tool_call.function.name, observation):
                    return {
                        "done": True,
                        "response": observation,
                        "action": f"special_tool:{tool_call.function.name}",
                    }

            except Exception as e:
                error_msg = f"Error executing tool {tool_call.function.name}: {str(e)}"
                logger.error(error_msg)
                self.update_memory(
                    "tool",
                    content=error_msg,
                    tool_call_id=tool_call.id,
                    name=tool_call.function.name,
                )
                observations.append(error_msg)

        return {
            "done": False,
            "observation": "\n".join(observations),
            "action": "tool_execution",
        }

    async def execute_tool(self, tool_call: Any) -> str:
        """
        Execute a single tool call

        Args:
            tool_call: ToolCall object

        Returns:
            Observation string
        """
        try:
            # Parse arguments
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in tool arguments: {str(e)}")
                return f"Error: Invalid JSON arguments - {str(e)}"

            # Execute tool
            logger.info(f"Executing tool: {tool_call.function.name} with args: {args}")
            result = await self.tool_collection.execute_tool(tool_call.function.name, args)

            # Convert result to string and truncate if needed
            observation = str(result)
            if self.max_observation_length and len(observation) > self.max_observation_length:
                truncated = len(observation) - self.max_observation_length
                observation = (
                    observation[: self.max_observation_length]
                    + f"\n... (truncated {truncated} characters)"
                )

            return observation

        except ToolExecutionError as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return f"Tool execution error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error executing tool: {str(e)}")
            return f"Error: {str(e)}"

    async def _handle_special_tool(self, tool_name: str, observation: str) -> bool:
        """
        Handle special tools that may terminate agent execution

        Args:
            tool_name: Name of the tool
            observation: Tool execution result

        Returns:
            True if agent should terminate
        """
        # Check for terminate tool
        if tool_name.lower() in ["terminate", "finish", "done", "complete"]:
            logger.info(f"Special tool '{tool_name}' called - terminating agent")
            self.state = AgentState.FINISHED
            return True

        return False

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

    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.tool_collection:
            await self.tool_collection.cleanup()
        await super().cleanup()

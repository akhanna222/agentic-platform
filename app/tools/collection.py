"""
Tool collection and management
"""

from typing import Any, Optional

from loguru import logger

from app.exceptions import ToolExecutionError
from app.tools.base import Tool
from app.tools.builtin import get_builtin_tools


class ToolCollection:
    """
    Manages a collection of tools available to agents
    """

    def __init__(self):
        self.tools: list[Tool] = []
        self._tool_map: dict[str, Tool] = {}

    def add_tool(self, tool: Tool) -> None:
        """Add a tool to the collection"""
        if tool.name in self._tool_map:
            logger.warning(f"Tool {tool.name} already exists, replacing")

        self.tools.append(tool)
        self._tool_map[tool.name] = tool
        logger.debug(f"Added tool: {tool.name}")

    def remove_tool(self, name: str) -> None:
        """Remove a tool from the collection"""
        if name in self._tool_map:
            tool = self._tool_map[name]
            self.tools.remove(tool)
            del self._tool_map[name]
            logger.debug(f"Removed tool: {name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tool_map.get(name)

    async def execute_tool(self, name: str, args: dict[str, Any]) -> Any:
        """
        Execute a tool by name

        Args:
            name: Tool name
            args: Tool arguments

        Returns:
            Tool execution result

        Raises:
            ToolExecutionError: If tool not found or execution fails
        """
        tool = self.get_tool(name)
        if tool is None:
            raise ToolExecutionError(f"Tool not found: {name}")

        try:
            logger.info(f"Executing tool: {name}")
            result = await tool.execute(**args)
            return result
        except Exception as e:
            logger.error(f"Tool execution failed for {name}: {str(e)}")
            raise ToolExecutionError(f"Tool {name} failed: {str(e)}") from e

    async def cleanup(self) -> None:
        """Cleanup all tools"""
        logger.debug("Cleaning up tool collection")
        # Add cleanup logic for tools that need it
        pass

    def list_tools(self) -> list[str]:
        """Get list of available tool names"""
        return list(self._tool_map.keys())

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Get tool definitions for LLM"""
        return [tool.to_dict() for tool in self.tools]


# Global tool collection
_tool_collection: Optional[ToolCollection] = None


def get_tool_collection() -> ToolCollection:
    """Get or create global tool collection"""
    global _tool_collection
    if _tool_collection is None:
        _tool_collection = ToolCollection()
        # Add built-in tools
        for tool in get_builtin_tools():
            _tool_collection.add_tool(tool)
        logger.info(
            f"Initialized tool collection with {len(_tool_collection.tools)} tools"
        )
    return _tool_collection

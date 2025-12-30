"""
Base tool implementation
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field


class Tool(BaseModel, ABC):
    """
    Base class for all tools

    Tools are functions that agents can call to perform actions
    """

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    requires_confirmation: bool = False

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Tool execution result
        """
        pass

    def to_dict(self) -> dict[str, Any]:
        """Convert tool to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class FunctionTool(Tool):
    """
    Tool that wraps a function

    Allows creating tools from regular Python functions
    """

    function: Optional[Callable] = None

    class Config:
        arbitrary_types_allowed = True

    async def execute(self, **kwargs) -> Any:
        """Execute the wrapped function"""
        if self.function is None:
            raise ValueError(f"Tool {self.name} has no function set")

        # Check if function is async
        import asyncio
        import inspect

        if inspect.iscoroutinefunction(self.function):
            return await self.function(**kwargs)
        else:
            # Run sync function in executor to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, lambda: self.function(**kwargs))

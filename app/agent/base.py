"""
Base agent implementation for the agentic platform
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field

from app.exceptions import AgentExecutionError
from app.llm import get_llm
from app.schema import AgentState, Memory, Message


class Agent(BaseModel, ABC):
    """
    Abstract base class for all agents

    Provides core functionality for:
    - State management
    - Memory/conversation history
    - LLM interaction
    - Execution loop
    """

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    # Agent properties
    name: str
    description: str
    system_prompt: str = ""
    max_steps: int = 20
    enable_stuck_detection: bool = True
    stuck_threshold: int = 3

    # Runtime state
    state: AgentState = AgentState.IDLE
    current_step: int = 0
    memory: Memory = Field(default_factory=Memory)

    def __init__(self, **data):
        super().__init__(**data)
        # Initialize with system prompt if provided
        if self.system_prompt:
            self.memory.add_message(Message.system_message(self.system_prompt))

    async def __aenter__(self):
        """Async context manager entry"""
        self.state = AgentState.RUNNING
        logger.info(f"Agent {self.name} starting execution")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if exc_type is not None:
            self.state = AgentState.ERROR
            logger.error(f"Agent {self.name} encountered error: {exc_val}")
        else:
            self.state = AgentState.FINISHED
            logger.info(f"Agent {self.name} finished execution")

        await self.cleanup()
        return False

    def update_memory(
        self,
        role: str,
        content: Optional[str] = None,
        tool_calls: Optional[list] = None,
        tool_call_id: Optional[str] = None,
        name: Optional[str] = None,
        images: Optional[list[str]] = None,
    ) -> None:
        """
        Add a message to agent memory

        Args:
            role: Message role (system, user, assistant, tool)
            content: Message content
            tool_calls: Tool calls for assistant messages
            tool_call_id: Tool call ID for tool response messages
            name: Tool name for tool response messages
            images: List of base64 encoded images
        """
        from app.schema import Role

        if role == "user":
            message = Message.user_message(content, images=images)
        elif role == "system":
            message = Message.system_message(content)
        elif role == "assistant":
            message = Message.assistant_message(content=content, tool_calls=tool_calls)
        elif role == "tool":
            message = Message.tool_message(content, tool_call_id, name)
        else:
            raise ValueError(f"Invalid role: {role}")

        self.memory.add_message(message)

    def is_stuck(self) -> bool:
        """
        Detect if agent is stuck in a loop

        Returns:
            True if agent appears stuck
        """
        if not self.enable_stuck_detection:
            return False

        messages = self.memory.get_messages()
        if len(messages) < self.stuck_threshold * 2:
            return False

        # Get recent assistant messages
        assistant_messages = [
            msg.content for msg in messages[-10:] if msg.role.value == "assistant"
        ]

        if len(assistant_messages) < self.stuck_threshold:
            return False

        # Check for repeated messages
        last_message = assistant_messages[-1]
        repeat_count = sum(1 for msg in assistant_messages[-5:] if msg == last_message)

        return repeat_count >= self.stuck_threshold

    async def run(self, prompt: str, images: Optional[list[str]] = None) -> str:
        """
        Main execution loop

        Args:
            prompt: User prompt to process
            images: Optional list of images

        Returns:
            Final response from agent
        """
        async with self:
            # Add user message
            self.update_memory("user", content=prompt, images=images)

            # Execute steps
            for step in range(self.max_steps):
                self.current_step = step + 1
                logger.info(
                    f"Agent {self.name} - Step {self.current_step}/{self.max_steps}"
                )

                # Check if stuck
                if self.is_stuck():
                    logger.warning(f"Agent {self.name} appears stuck, breaking loop")
                    self.update_memory(
                        "system",
                        "You appear to be stuck in a loop. Please try a different approach.",
                    )

                # Execute one step
                result = await self.step()

                # Check if we're done
                if result.get("done", False):
                    logger.info(f"Agent {self.name} completed task")
                    return result.get("response", "Task completed")

            logger.warning(f"Agent {self.name} reached max steps")
            return "I've reached the maximum number of steps. The task may not be fully complete."

    @abstractmethod
    async def step(self) -> dict[str, Any]:
        """
        Execute one reasoning step

        Returns:
            Dictionary with:
                - done: bool indicating if task is complete
                - response: str with the response (if done)
                - action: str describing the action taken
        """
        pass

    async def cleanup(self) -> None:
        """
        Cleanup resources

        Override in subclasses to cleanup specific resources
        """
        pass

    def get_llm(self):
        """Get LLM instance"""
        return get_llm()

    def get_conversation_history(self) -> list[dict[str, Any]]:
        """Get conversation history as list of dicts"""
        return self.memory.to_dict_list()

    def clear_memory(self) -> None:
        """Clear conversation memory (keeps system messages)"""
        self.memory.clear()

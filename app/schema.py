"""
Data models and schemas for the agentic platform
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class Role(str, Enum):
    """Message role enumeration"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ToolChoice(str, Enum):
    """Tool selection strategy"""

    NONE = "none"
    AUTO = "auto"
    REQUIRED = "required"


class AgentState(str, Enum):
    """Agent execution states"""

    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"


class Function(BaseModel):
    """Function call representation"""

    name: str
    arguments: str


class ToolCall(BaseModel):
    """Tool call representation"""

    id: str
    type: str = "function"
    function: Function


class Message(BaseModel):
    """Message in conversation history"""

    role: Role
    content: Optional[str] = None
    tool_calls: Optional[list[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    images: Optional[list[str]] = None  # Base64 encoded images

    def __add__(self, other):
        """Combine messages into a list"""
        if isinstance(other, Message):
            return [self, other]
        elif isinstance(other, list):
            return [self] + other
        raise TypeError(f"Cannot add Message and {type(other)}")

    @staticmethod
    def user_message(content: str, images: Optional[list[str]] = None) -> "Message":
        """Create a user message"""
        return Message(role=Role.USER, content=content, images=images)

    @staticmethod
    def system_message(content: str) -> "Message":
        """Create a system message"""
        return Message(role=Role.SYSTEM, content=content)

    @staticmethod
    def assistant_message(
        content: Optional[str] = None, tool_calls: Optional[list[ToolCall]] = None
    ) -> "Message":
        """Create an assistant message"""
        return Message(role=Role.ASSISTANT, content=content, tool_calls=tool_calls)

    @staticmethod
    def tool_message(content: str, tool_call_id: str, name: str) -> "Message":
        """Create a tool response message"""
        return Message(
            role=Role.TOOL, content=content, tool_call_id=tool_call_id, name=name
        )

    @staticmethod
    def from_tool_calls(tool_calls: list[ToolCall]) -> "Message":
        """Create an assistant message from tool calls"""
        return Message(role=Role.ASSISTANT, tool_calls=tool_calls)

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary"""
        result = {"role": self.role.value}

        if self.content:
            result["content"] = self.content
        if self.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in self.tool_calls
            ]
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.name:
            result["name"] = self.name
        if self.images:
            result["images"] = self.images

        return result


class Memory(BaseModel):
    """Conversation memory manager"""

    messages: list[Message] = Field(default_factory=list)
    max_size: int = 100

    def add_message(self, message: Message) -> None:
        """Add a message to memory"""
        self.messages.append(message)
        if len(self.messages) > self.max_size:
            # Keep system messages and trim from the middle
            system_messages = [m for m in self.messages if m.role == Role.SYSTEM]
            other_messages = [m for m in self.messages if m.role != Role.SYSTEM]
            # Keep most recent messages
            other_messages = other_messages[-(self.max_size - len(system_messages)) :]
            self.messages = system_messages + other_messages

    def get_messages(self) -> list[Message]:
        """Get all messages"""
        return self.messages

    def to_dict_list(self) -> list[dict[str, Any]]:
        """Convert messages to list of dictionaries"""
        return [msg.to_dict() for msg in self.messages]

    def clear(self) -> None:
        """Clear all messages except system messages"""
        self.messages = [m for m in self.messages if m.role == Role.SYSTEM]


class ToolDefinition(BaseModel):
    """Tool definition for LLM function calling"""

    type: str = "function"
    function: dict[str, Any]


class AgentConfig(BaseModel):
    """Configuration for an agent"""

    name: str
    description: str
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    max_steps: int = 20
    enable_tools: bool = True
    system_prompt: Optional[str] = None

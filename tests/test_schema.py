"""
Tests for schema module
"""

import pytest
from app.schema import Message, Memory, Role, AgentState, ToolCall, Function


def test_message_creation():
    """Test message creation"""
    msg = Message.user_message("Hello")
    assert msg.role == Role.USER
    assert msg.content == "Hello"


def test_system_message():
    """Test system message creation"""
    msg = Message.system_message("System prompt")
    assert msg.role == Role.SYSTEM
    assert msg.content == "System prompt"


def test_assistant_message():
    """Test assistant message creation"""
    msg = Message.assistant_message("Response")
    assert msg.role == Role.ASSISTANT
    assert msg.content == "Response"


def test_memory_management():
    """Test memory management"""
    memory = Memory()
    memory.add_message(Message.user_message("Test"))
    assert len(memory.get_messages()) == 1


def test_memory_pruning():
    """Test memory auto-pruning"""
    memory = Memory(max_size=5)
    for i in range(10):
        memory.add_message(Message.user_message(f"Message {i}"))
    assert len(memory.get_messages()) <= 5


def test_agent_state():
    """Test agent states"""
    assert AgentState.IDLE == "idle"
    assert AgentState.RUNNING == "running"
    assert AgentState.FINISHED == "finished"
    assert AgentState.ERROR == "error"


def test_tool_call():
    """Test tool call creation"""
    func = Function(name="test_tool", arguments='{"arg": "value"}')
    tc = ToolCall(id="1", type="function", function=func)
    assert tc.id == "1"
    assert tc.function.name == "test_tool"

"""
Tests for tools module
"""

import pytest
from app.tools.collection import ToolCollection
from app.tools.builtin import GetTimeTool, PythonExecuteTool


@pytest.mark.asyncio
async def test_get_time_tool():
    """Test get time tool"""
    tool = GetTimeTool()
    result = await tool.execute()
    assert result is not None
    assert len(result) > 0


@pytest.mark.asyncio
async def test_python_execute_tool():
    """Test Python execution tool"""
    tool = PythonExecuteTool()
    code = "result = 2 + 2"
    result = await tool.execute(code=code)
    assert "4" in result


def test_tool_collection():
    """Test tool collection"""
    collection = ToolCollection()
    tool = GetTimeTool()
    collection.add_tool(tool)
    assert "get_current_time" in collection.list_tools()


@pytest.mark.asyncio
async def test_tool_execution():
    """Test tool execution through collection"""
    collection = ToolCollection()
    tool = GetTimeTool()
    collection.add_tool(tool)

    result = await collection.execute_tool("get_current_time", {})
    assert result is not None

"""
Tools module for the agentic platform
"""

from app.tools.base import Tool, FunctionTool
from app.tools.collection import ToolCollection, get_tool_collection

# Import all tool categories
from app.tools.builtin import get_builtin_tools
from app.tools.browser import BrowserUseTool, PlaywrightTool
from app.tools.crawl import WebCrawlTool, HTMLToTextTool
from app.tools.advanced_file import StrReplaceEditorTool, FileSearchTool
from app.tools.visualization import (
    DataVisualizationTool,
    VisualizationPrepareTool,
    NormalPythonExecuteTool,
)
from app.tools.control import TerminateTool, AskHumanTool
from app.tools.env_config import (
    RequestEnvVariableTool,
    SaveEnvVariableTool,
    ListEnvVariablesTool,
    ClearEnvVariableTool,
)

__all__ = [
    "Tool",
    "FunctionTool",
    "ToolCollection",
    "get_tool_collection",
    "get_builtin_tools",
    # Browser tools
    "BrowserUseTool",
    "PlaywrightTool",
    # Crawl tools
    "WebCrawlTool",
    "HTMLToTextTool",
    # File tools
    "StrReplaceEditorTool",
    "FileSearchTool",
    # Visualization tools
    "DataVisualizationTool",
    "VisualizationPrepareTool",
    "NormalPythonExecuteTool",
    # Control tools
    "TerminateTool",
    "AskHumanTool",
    # Environment variable tools
    "RequestEnvVariableTool",
    "SaveEnvVariableTool",
    "ListEnvVariablesTool",
    "ClearEnvVariableTool",
]


def get_all_tools() -> list[Tool]:
    """Get all available tools including advanced ones"""
    tools = get_builtin_tools()

    # Add advanced tools
    tools.extend(
        [
            # Browser automation
            BrowserUseTool(),
            PlaywrightTool(),
            # Web crawling
            WebCrawlTool(),
            HTMLToTextTool(),
            # Advanced file operations
            StrReplaceEditorTool(),
            FileSearchTool(),
            # Data visualization
            DataVisualizationTool(),
            VisualizationPrepareTool(),
            NormalPythonExecuteTool(),
            # Environment variable management
            RequestEnvVariableTool(),
            SaveEnvVariableTool(),
            ListEnvVariablesTool(),
            ClearEnvVariableTool(),
            # Control
            TerminateTool(),
            AskHumanTool(),
        ]
    )

    return tools

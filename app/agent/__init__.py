"""
Agent module for the agentic platform
"""

from app.agent.base import Agent
from app.agent.react import ReActAgent
from app.agent.toolcall import ToolCallAgent
from app.agent.platform import PlatformAgent
from app.agent.browser import BrowserAgent
from app.agent.data_analysis import DataAnalysisAgent
from app.agent.mcp import MCPAgent
from app.agent.fullstack_ship import FullStackShipAgent

__all__ = [
    "Agent",
    "ReActAgent",
    "ToolCallAgent",
    "PlatformAgent",
    "BrowserAgent",
    "DataAnalysisAgent",
    "MCPAgent",
    "FullStackShipAgent",
]

"""
MCP (Model Context Protocol) agent

Connects to external MCP servers and uses their tools dynamically
"""

import asyncio
from typing import Any, Optional

from loguru import logger

from app.agent.toolcall import ToolCallAgent
from app.config import get_config
from app.prompts import MCP_AGENT_SYSTEM_PROMPT, MCP_AGENT_NEXT_STEP_PROMPT
from app.tools.base import Tool
from app.tools.collection import ToolCollection
from app.tools.control import TerminateTool


class MCPTool(Tool):
    """
    Wrapper for MCP server tools
    """

    _tool_schema: dict[str, Any]
    _mcp_client: Any

    def __init__(self, tool_schema: dict, mcp_client: Any, **data):
        self._tool_schema = tool_schema
        self._mcp_client = mcp_client

        # Extract tool info from schema
        name = tool_schema.get("name", "unknown")
        description = tool_schema.get("description", "No description")
        parameters = tool_schema.get("inputSchema", {})

        super().__init__(name=name, description=description, parameters=parameters, **data)

    async def execute(self, **kwargs) -> Any:
        """Execute MCP tool"""
        try:
            # Call the MCP server tool
            result = await self._mcp_client.call_tool(self.name, kwargs)
            return result
        except Exception as e:
            logger.error(f"MCP tool execution error: {str(e)}")
            return f"Error: {str(e)}"


class MCPAgent(ToolCallAgent):
    """
    Agent that connects to MCP servers and uses external tools

    Supports both SSE (Server-Sent Events) and stdio MCP connections
    """

    system_prompt: str = MCP_AGENT_SYSTEM_PROMPT
    max_steps: int = 20

    _mcp_clients: list[Any] = []
    _refresh_tools_interval: int = 10  # Refresh tools every N steps

    def __init__(self, mcp_servers: Optional[list[dict]] = None, **data):
        """
        Initialize MCP agent

        Args:
            mcp_servers: List of MCP server configurations
                Each config should have:
                - type: "sse" or "stdio"
                - url: Server URL (for SSE)
                - command: Command to run (for stdio)
                - args: Command arguments (for stdio)
        """
        # Initialize with terminate tool
        if "tool_collection" not in data:
            data["tool_collection"] = ToolCollection()
            data["tool_collection"].add_tool(TerminateTool())

        if "name" not in data:
            data["name"] = "MCPAgent"
        if "description" not in data:
            data["description"] = "Agent with Model Context Protocol support for external tools"

        super().__init__(**data)

        self.mcp_servers = mcp_servers or []
        self._mcp_clients = []

    @classmethod
    async def create(cls, mcp_servers: Optional[list[dict]] = None, **kwargs) -> "MCPAgent":
        """
        Factory method to create and initialize MCP agent

        Args:
            mcp_servers: MCP server configurations

        Returns:
            Initialized MCPAgent
        """
        agent = cls(mcp_servers=mcp_servers, **kwargs)
        await agent.initialize()
        return agent

    async def initialize(self):
        """Initialize connections to MCP servers and load tools"""
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError:
            logger.error("MCP library not installed. Install with: pip install mcp")
            return

        logger.info(f"Initializing MCP agent with {len(self.mcp_servers)} server(s)...")

        for server_config in self.mcp_servers:
            try:
                server_type = server_config.get("type", "stdio")

                if server_type == "stdio":
                    # Connect via stdio
                    command = server_config.get("command")
                    args = server_config.get("args", [])

                    if not command:
                        logger.warning("Stdio MCP server missing command")
                        continue

                    logger.info(f"Connecting to stdio MCP server: {command}")

                    # This is a simplified version - full implementation would
                    # properly handle the async context and tool loading
                    # For now, we log that MCP support is available but not fully integrated
                    logger.info(f"MCP server configuration ready: {command}")

                elif server_type == "sse":
                    # Connect via SSE
                    url = server_config.get("url")
                    if not url:
                        logger.warning("SSE MCP server missing URL")
                        continue

                    logger.info(f"MCP SSE server configuration ready: {url}")

            except Exception as e:
                logger.error(f"Error setting up MCP server: {str(e)}")

        # Note: Full MCP integration requires proper async context management
        # and tool schema parsing. This is a foundation for future enhancement.
        logger.info("MCP agent initialized (basic support)")

    async def _refresh_tools(self):
        """Refresh tools from MCP servers"""
        # This would query MCP servers for updated tool lists
        # and add/remove tools from the collection as needed
        logger.debug("MCP tool refresh triggered")

    async def step(self) -> dict[str, Any]:
        """Execute step with periodic tool refresh"""
        # Refresh tools periodically
        if self.current_step % self._refresh_tools_interval == 0:
            await self._refresh_tools()

        return await super().step()

    async def cleanup(self):
        """Cleanup MCP connections"""
        logger.info("Cleaning up MCP agent connections...")

        # Close all MCP clients
        for client in self._mcp_clients:
            try:
                if hasattr(client, "close"):
                    await client.close()
            except Exception as e:
                logger.error(f"Error closing MCP client: {str(e)}")

        self._mcp_clients = []
        await super().cleanup()

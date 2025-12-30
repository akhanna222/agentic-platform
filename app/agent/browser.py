"""
Browser automation agent
"""

from typing import Any, Optional

from loguru import logger

from app.agent.toolcall import ToolCallAgent
from app.config import get_config
from app.prompts import BROWSER_AGENT_SYSTEM_PROMPT, get_browser_agent_prompt
from app.tools.browser import BrowserUseTool, PlaywrightTool
from app.tools.collection import ToolCollection
from app.tools.control import TerminateTool


class BrowserAgent(ToolCallAgent):
    """
    Specialized agent for web browser automation

    Uses browser-use and playwright for web interaction
    """

    system_prompt: str = BROWSER_AGENT_SYSTEM_PROMPT
    max_steps: int = 20
    max_observation_length: int = 10000

    def __init__(self, **data):
        # Initialize with browser-specific tools
        if "tool_collection" not in data:
            data["tool_collection"] = ToolCollection()
            data["tool_collection"].add_tool(BrowserUseTool())
            data["tool_collection"].add_tool(PlaywrightTool())
            data["tool_collection"].add_tool(TerminateTool())

        if "name" not in data:
            data["name"] = "BrowserAgent"
        if "description" not in data:
            data["description"] = "Specialized agent for web browser automation and web scraping"

        super().__init__(**data)

    @classmethod
    async def create(cls, **kwargs) -> "BrowserAgent":
        """
        Factory method to create browser agent

        Returns:
            Initialized BrowserAgent
        """
        agent = cls(**kwargs)
        logger.info(f"Created BrowserAgent with {len(agent.tool_collection.tools)} tools")
        return agent

    async def get_browser_state(self) -> str:
        """
        Get current browser state from tools

        Returns:
            Browser state description
        """
        # Try to get state from browser tool
        browser_tool = self.tool_collection.get_tool("browser_use")
        if browser_tool and hasattr(browser_tool, "_browser_instance"):
            if browser_tool._browser_instance:
                try:
                    # Get current page info
                    page = await browser_tool._browser_instance.get_current_page()
                    if page:
                        url = page.url
                        title = await page.title()
                        return f"Current URL: {url}\nPage Title: {title}"
                except:
                    pass

        return "Browser not yet initialized"

    async def think(self) -> dict[str, Any]:
        """
        Enhanced think method with browser state

        Returns:
            Thought with browser context
        """
        # Get current browser state
        browser_state = await self.get_browser_state()

        # Add browser state to memory as a system message if browser is active
        if "not yet initialized" not in browser_state.lower():
            # Create enhanced prompt with browser state
            enhanced_prompt = get_browser_agent_prompt(browser_state)
            # Temporarily add to messages for this think cycle
            original_messages = self.memory.get_messages()
            self.update_memory("system", content=enhanced_prompt)

        # Call parent think method
        result = await super().think()

        return result

    async def cleanup(self) -> None:
        """Cleanup browser resources"""
        logger.info("Cleaning up browser agent...")
        # Cleanup tools (which will close browser)
        await super().cleanup()

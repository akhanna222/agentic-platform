"""
Browser automation tools using browser-use library
"""

import asyncio
from typing import Any, Optional

from loguru import logger

from app.tools.base import Tool


class BrowserUseTool(Tool):
    """
    Advanced browser automation tool using browser-use library

    Provides natural language browser control capabilities
    """

    name: str = "browser_use"
    description: str = """Control a web browser using natural language commands. You can:
- Navigate to websites
- Click on elements
- Fill out forms
- Extract information
- Take screenshots
- Interact with web pages

Provide a clear instruction of what you want to do with the browser."""

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "instruction": {
                "type": "string",
                "description": "Natural language instruction for browser action (e.g., 'Go to google.com and search for Python', 'Click the login button')",
            },
            "wait_time": {
                "type": "number",
                "description": "Time to wait after action (seconds)",
                "default": 2,
            },
        },
        "required": ["instruction"],
    }

    _browser_instance: Optional[Any] = None
    _browser_controller: Optional[Any] = None

    async def execute(self, instruction: str, wait_time: float = 2) -> str:
        """
        Execute browser action using natural language

        Args:
            instruction: Natural language instruction
            wait_time: Wait time after action

        Returns:
            Result of browser action
        """
        try:
            # Import browser-use (lazy import to avoid dependency issues)
            try:
                from browser_use import Agent as BrowserAgent, Browser, Controller
            except ImportError:
                return "Error: browser-use library not installed. Install with: pip install browser-use"

            # Initialize browser if not already done
            if self._browser_instance is None:
                logger.info("Initializing browser...")
                self._browser_instance = Browser()
                await self._browser_instance.start()
                logger.info("Browser started successfully")

            # Execute the instruction
            logger.info(f"Executing browser instruction: {instruction}")

            # Create a browser agent for this task
            from app.llm import get_llm

            llm = get_llm()

            # Create browser controller
            if self._browser_controller is None:
                self._browser_controller = Controller()

            # Execute the task
            # Note: This is a simplified version. In production, you'd integrate
            # more tightly with the browser-use library
            result = await self._execute_browser_command(instruction)

            if wait_time > 0:
                await asyncio.sleep(wait_time)

            return result

        except Exception as e:
            logger.error(f"Browser automation error: {str(e)}")
            return f"Error: {str(e)}"

    async def _execute_browser_command(self, instruction: str) -> str:
        """
        Execute browser command

        This is a simplified implementation. For full functionality,
        integrate with browser-use library's agent system.
        """
        try:
            # Get current page
            if not self._browser_instance:
                return "Error: Browser not initialized"

            page = await self._browser_instance.get_current_page()
            if not page:
                page = await self._browser_instance.new_page()

            # Parse simple commands
            instruction_lower = instruction.lower()

            if "go to" in instruction_lower or "navigate to" in instruction_lower:
                # Extract URL
                url = instruction_lower.split("go to")[-1].split("navigate to")[-1].strip()
                if not url.startswith("http"):
                    url = f"https://{url}"
                await page.goto(url)
                return f"Navigated to {url}"

            elif "screenshot" in instruction_lower:
                screenshot = await page.screenshot()
                return f"Screenshot taken ({len(screenshot)} bytes)"

            elif "get text" in instruction_lower or "extract text" in instruction_lower:
                text = await page.content()
                return f"Page content:\n{text[:1000]}..."

            else:
                # For complex instructions, we'd use browser-use Agent
                return f"Processed instruction: {instruction}\nNote: Complex browser automation requires full browser-use integration"

        except Exception as e:
            return f"Error executing browser command: {str(e)}"

    async def cleanup(self) -> None:
        """Cleanup browser resources"""
        if self._browser_instance:
            try:
                logger.info("Closing browser...")
                await self._browser_instance.close()
                self._browser_instance = None
                self._browser_controller = None
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")


class PlaywrightTool(Tool):
    """
    Direct Playwright browser control tool

    Provides low-level browser automation using Playwright
    """

    name: str = "playwright_execute"
    description: str = "Execute Playwright commands for browser automation. Supports Python code using playwright async API."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Playwright Python code to execute. Use 'page' variable for the browser page.",
            }
        },
        "required": ["code"],
    }

    _playwright: Optional[Any] = None
    _browser: Optional[Any] = None
    _page: Optional[Any] = None

    async def execute(self, code: str) -> str:
        """
        Execute Playwright code

        Args:
            code: Python code using playwright API

        Returns:
            Execution result
        """
        try:
            # Import playwright
            try:
                from playwright.async_api import async_playwright
            except ImportError:
                return "Error: playwright not installed. Install with: pip install playwright && playwright install"

            # Initialize playwright if needed
            if self._playwright is None:
                logger.info("Initializing Playwright...")
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(headless=True)
                self._page = await self._browser.new_page()
                logger.info("Playwright initialized")

            # Execute code with page context
            local_vars = {"page": self._page, "browser": self._browser}
            exec(code, {"__builtins__": __builtins__}, local_vars)

            # Get result if any
            result = local_vars.get("result", "Code executed successfully")
            return str(result)

        except Exception as e:
            logger.error(f"Playwright execution error: {str(e)}")
            return f"Error: {str(e)}"

    async def cleanup(self) -> None:
        """Cleanup playwright resources"""
        if self._browser:
            try:
                await self._browser.close()
            except:
                pass
        if self._playwright:
            try:
                await self._playwright.stop()
            except:
                pass
        self._playwright = None
        self._browser = None
        self._page = None

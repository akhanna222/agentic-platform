"""
Web crawling and scraping tools using crawl4ai
"""

from typing import Any

from loguru import logger

from app.tools.base import Tool


class WebCrawlTool(Tool):
    """
    Advanced web crawling using crawl4ai

    Extracts content, links, and structured data from websites
    """

    name: str = "web_crawl"
    description: str = """Crawl and extract content from websites. Can extract:
- Main text content
- Links and URLs
- Metadata
- Structured data
- Clean, readable text from web pages

Use this for deep web scraping and content extraction."""

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to crawl",
            },
            "extract_links": {
                "type": "boolean",
                "description": "Whether to extract all links from the page",
                "default": False,
            },
            "extract_images": {
                "type": "boolean",
                "description": "Whether to extract image URLs",
                "default": False,
            },
            "max_length": {
                "type": "integer",
                "description": "Maximum content length to return",
                "default": 5000,
            },
        },
        "required": ["url"],
    }

    async def execute(
        self,
        url: str,
        extract_links: bool = False,
        extract_images: bool = False,
        max_length: int = 5000,
    ) -> str:
        """
        Crawl and extract content from URL

        Args:
            url: URL to crawl
            extract_links: Whether to extract links
            extract_images: Whether to extract images
            max_length: Maximum content length

        Returns:
            Extracted content and metadata
        """
        try:
            # Import crawl4ai
            try:
                from crawl4ai import AsyncWebCrawler
            except ImportError:
                return "Error: crawl4ai not installed. Install with: pip install crawl4ai"

            logger.info(f"Crawling URL: {url}")

            # Create crawler
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url)

                if not result.success:
                    return f"Error: Failed to crawl {url} - {result.error_message}"

                # Build response
                output = []
                output.append(f"URL: {url}")
                output.append(f"Title: {result.title or 'N/A'}")
                output.append("\n--- Content ---")

                # Get main content
                content = result.markdown or result.cleaned_html or ""
                if len(content) > max_length:
                    content = content[:max_length] + f"\n... (truncated from {len(content)} chars)"

                output.append(content)

                # Extract links if requested
                if extract_links and result.links:
                    output.append("\n--- Links ---")
                    links = list(result.links.values())[:20]  # Limit to 20 links
                    output.append("\n".join(links))

                # Extract images if requested
                if extract_images and result.media:
                    output.append("\n--- Images ---")
                    images = [img["src"] for img in result.media.get("images", [])][:10]
                    output.append("\n".join(images))

                return "\n".join(output)

        except Exception as e:
            logger.error(f"Web crawl error: {str(e)}")
            return f"Error: {str(e)}"


class HTMLToTextTool(Tool):
    """
    Convert HTML to clean text using html2text
    """

    name: str = "html_to_text"
    description: str = "Convert HTML content to clean, readable text. Useful for processing web pages."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "html": {
                "type": "string",
                "description": "HTML content to convert",
            },
            "ignore_links": {
                "type": "boolean",
                "description": "Whether to ignore links in output",
                "default": False,
            },
        },
        "required": ["html"],
    }

    async def execute(self, html: str, ignore_links: bool = False) -> str:
        """
        Convert HTML to text

        Args:
            html: HTML content
            ignore_links: Whether to ignore links

        Returns:
            Clean text content
        """
        try:
            import html2text

            h = html2text.HTML2Text()
            h.ignore_links = ignore_links
            h.ignore_images = True

            text = h.handle(html)
            return text

        except Exception as e:
            logger.error(f"HTML to text error: {str(e)}")
            return f"Error: {str(e)}"

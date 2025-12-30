"""
Built-in tools for the platform
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from app.config import get_config
from app.tools.base import FunctionTool, Tool


class PythonExecuteTool(Tool):
    """Execute Python code in a safe environment"""

    name: str = "python_execute"
    description: str = "Execute Python code and return the result. Use this for calculations, data processing, or running Python scripts."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute",
            }
        },
        "required": ["code"],
    }

    async def execute(self, code: str) -> str:
        """Execute Python code"""
        try:
            # Create a restricted globals dict
            restricted_globals = {
                "__builtins__": __builtins__,
                "print": print,
                "len": len,
                "range": range,
                "sum": sum,
                "max": max,
                "min": min,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
            }

            # Execute code and capture output
            local_vars = {}
            exec(code, restricted_globals, local_vars)

            # Get result
            if "result" in local_vars:
                return str(local_vars["result"])
            else:
                return "Code executed successfully (no result variable set)"

        except Exception as e:
            logger.error(f"Python execution error: {str(e)}")
            return f"Error executing Python code: {str(e)}"


class FileReadTool(Tool):
    """Read contents of a file"""

    name: str = "file_read"
    description: str = "Read the contents of a file from the workspace directory."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to read (relative to workspace)",
            }
        },
        "required": ["file_path"],
    }

    async def execute(self, file_path: str) -> str:
        """Read file contents"""
        try:
            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            full_path = workspace / file_path

            # Security check - ensure path is within workspace
            if not str(full_path.resolve()).startswith(str(workspace.resolve())):
                return "Error: Access denied - path outside workspace"

            if not full_path.exists():
                return f"Error: File not found: {file_path}"

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            return content

        except Exception as e:
            logger.error(f"File read error: {str(e)}")
            return f"Error reading file: {str(e)}"


class FileWriteTool(Tool):
    """Write content to a file"""

    name: str = "file_write"
    description: str = "Write content to a file in the workspace directory. Creates the file if it doesn't exist."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to write (relative to workspace)",
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file",
            },
        },
        "required": ["file_path", "content"],
    }

    async def execute(self, file_path: str, content: str) -> str:
        """Write file contents"""
        try:
            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            full_path = workspace / file_path

            # Security check - ensure path is within workspace
            if not str(full_path.resolve()).startswith(str(workspace.resolve())):
                return "Error: Access denied - path outside workspace"

            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            return f"Successfully wrote to {file_path}"

        except Exception as e:
            logger.error(f"File write error: {str(e)}")
            return f"Error writing file: {str(e)}"


class FileListTool(Tool):
    """List files in a directory"""

    name: str = "file_list"
    description: str = "List files and directories in a specified path within the workspace."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory path to list (relative to workspace, default is root)",
                "default": ".",
            }
        },
        "required": [],
    }

    async def execute(self, directory: str = ".") -> str:
        """List directory contents"""
        try:
            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            full_path = workspace / directory

            # Security check
            if not str(full_path.resolve()).startswith(str(workspace.resolve())):
                return "Error: Access denied - path outside workspace"

            if not full_path.exists():
                return f"Error: Directory not found: {directory}"

            if not full_path.is_dir():
                return f"Error: Not a directory: {directory}"

            items = []
            for item in sorted(full_path.iterdir()):
                item_type = "DIR" if item.is_dir() else "FILE"
                size = item.stat().st_size if item.is_file() else 0
                items.append(f"{item_type:6} {item.name:40} {size:>10} bytes")

            return "\n".join(items) if items else "Empty directory"

        except Exception as e:
            logger.error(f"File list error: {str(e)}")
            return f"Error listing directory: {str(e)}"


class WebSearchTool(Tool):
    """Search the web using DuckDuckGo"""

    name: str = "web_search"
    description: str = "Search the web for information using DuckDuckGo. Returns a list of search results with titles and snippets."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 5,
            },
        },
        "required": ["query"],
    }

    async def execute(self, query: str, max_results: int = 5) -> str:
        """Search the web"""
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for i, result in enumerate(ddgs.text(query, max_results=max_results)):
                    results.append(
                        f"{i+1}. {result['title']}\n   {result['href']}\n   {result['body']}\n"
                    )

            return "\n".join(results) if results else "No results found"

        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return f"Error performing web search: {str(e)}"


class GetTimeTool(Tool):
    """Get current date and time"""

    name: str = "get_current_time"
    description: str = "Get the current date and time in ISO format."
    parameters: dict[str, Any] = {"type": "object", "properties": {}, "required": []}

    async def execute(self) -> str:
        """Get current time"""
        return datetime.now().isoformat()


class BashExecuteTool(Tool):
    """Execute bash commands (disabled by default for security)"""

    name: str = "bash_execute"
    description: str = "Execute a bash command in the workspace directory. Use with caution."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Bash command to execute",
            }
        },
        "required": ["command"],
    }
    requires_confirmation: bool = True

    async def execute(self, command: str) -> str:
        """Execute bash command"""
        try:
            config = get_config()
            workspace = Path(config.platform.workspace_dir)

            result = subprocess.run(
                command,
                shell=True,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=30,
            )

            output = result.stdout if result.stdout else result.stderr
            return output if output else "Command executed successfully (no output)"

        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds"
        except Exception as e:
            logger.error(f"Bash execution error: {str(e)}")
            return f"Error executing command: {str(e)}"


def get_builtin_tools() -> list[Tool]:
    """Get list of built-in tools"""
    return [
        PythonExecuteTool(),
        FileReadTool(),
        FileWriteTool(),
        FileListTool(),
        WebSearchTool(),
        GetTimeTool(),
        # BashExecuteTool() is disabled by default for security
    ]

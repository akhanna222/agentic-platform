"""
Advanced file manipulation tools
"""

import difflib
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from app.config import get_config
from app.tools.base import Tool


class StrReplaceEditorTool(Tool):
    """
    Advanced file editor using string replacement

    Allows precise editing of files by replacing specific strings
    """

    name: str = "str_replace_editor"
    description: str = """Edit files by replacing specific strings. More precise than rewriting entire files.
Use this to make targeted edits to code or text files."""

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to file to edit (relative to workspace)",
            },
            "old_str": {
                "type": "string",
                "description": "String to replace (must match exactly)",
            },
            "new_str": {
                "type": "string",
                "description": "Replacement string",
            },
        },
        "required": ["file_path", "old_str", "new_str"],
    }

    async def execute(self, file_path: str, old_str: str, new_str: str) -> str:
        """
        Replace string in file

        Args:
            file_path: File to edit
            old_str: String to replace
            new_str: Replacement string

        Returns:
            Result message with diff
        """
        try:
            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            full_path = workspace / file_path

            # Security check
            if not str(full_path.resolve()).startswith(str(workspace.resolve())):
                return "Error: Access denied - path outside workspace"

            if not full_path.exists():
                return f"Error: File not found: {file_path}"

            # Read file
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if old_str exists
            if old_str not in content:
                # Provide helpful error with similar strings
                lines = content.split("\n")
                similar = difflib.get_close_matches(old_str, lines, n=3, cutoff=0.6)
                msg = f"Error: String not found in file.\n"
                if similar:
                    msg += f"Did you mean one of these?\n" + "\n".join(f"  - {s}" for s in similar)
                return msg

            # Perform replacement
            new_content = content.replace(old_str, new_str, 1)  # Replace first occurrence

            # Write back
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            # Generate diff
            diff = list(
                difflib.unified_diff(
                    content.splitlines(keepends=True),
                    new_content.splitlines(keepends=True),
                    fromfile=f"{file_path} (original)",
                    tofile=f"{file_path} (modified)",
                )
            )

            diff_str = "".join(diff[:50])  # Limit diff output

            return f"Successfully edited {file_path}\n\nDiff:\n{diff_str}"

        except Exception as e:
            logger.error(f"File edit error: {str(e)}")
            return f"Error: {str(e)}"


class FileSearchTool(Tool):
    """
    Search for files and content in workspace
    """

    name: str = "file_search"
    description: str = "Search for files by name or search within file contents using patterns."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Search pattern (filename or content to search for)",
            },
            "search_content": {
                "type": "boolean",
                "description": "Whether to search file contents (True) or just filenames (False)",
                "default": False,
            },
            "file_extensions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by file extensions (e.g., ['.py', '.txt'])",
                "default": [],
            },
        },
        "required": ["pattern"],
    }

    async def execute(
        self,
        pattern: str,
        search_content: bool = False,
        file_extensions: list[str] = None,
    ) -> str:
        """
        Search for files or content

        Args:
            pattern: Search pattern
            search_content: Search in file contents
            file_extensions: Filter by extensions

        Returns:
            Search results
        """
        try:
            config = get_config()
            workspace = Path(config.platform.workspace_dir)

            results = []

            if search_content:
                # Search file contents
                for file_path in workspace.rglob("*"):
                    if not file_path.is_file():
                        continue

                    # Filter by extension
                    if file_extensions and file_path.suffix not in file_extensions:
                        continue

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            if pattern.lower() in content.lower():
                                # Find line numbers
                                lines = content.split("\n")
                                matching_lines = [
                                    (i + 1, line)
                                    for i, line in enumerate(lines)
                                    if pattern.lower() in line.lower()
                                ]
                                rel_path = file_path.relative_to(workspace)
                                results.append(f"{rel_path}:")
                                for line_no, line in matching_lines[:3]:  # Show first 3 matches
                                    results.append(f"  Line {line_no}: {line.strip()}")
                    except:
                        # Skip binary files or files that can't be read
                        continue
            else:
                # Search filenames
                for file_path in workspace.rglob(f"*{pattern}*"):
                    if file_extensions and file_path.suffix not in file_extensions:
                        continue
                    rel_path = file_path.relative_to(workspace)
                    file_type = "DIR" if file_path.is_dir() else "FILE"
                    results.append(f"{file_type}: {rel_path}")

            if not results:
                return f"No results found for pattern: {pattern}"

            # Limit results
            if len(results) > 50:
                results = results[:50]
                results.append(f"... (showing first 50 results)")

            return "\n".join(results)

        except Exception as e:
            logger.error(f"File search error: {str(e)}")
            return f"Error: {str(e)}"

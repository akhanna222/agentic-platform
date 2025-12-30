"""
Agent control tools
"""

from typing import Any

from app.tools.base import Tool


class TerminateTool(Tool):
    """
    Tool to signal task completion
    """

    name: str = "terminate"
    description: str = "Call this tool when the task is complete. Provide a summary of what was accomplished."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "Summary of task completion and results",
            },
            "success": {
                "type": "boolean",
                "description": "Whether the task was successful",
                "default": True,
            },
        },
        "required": ["summary"],
    }

    async def execute(self, summary: str, success: bool = True) -> str:
        """
        Signal task completion

        Args:
            summary: Task summary
            success: Success status

        Returns:
            Completion message
        """
        status = "✓ COMPLETED" if success else "✗ FAILED"
        return f"{status}\n\n{summary}"


class AskHumanTool(Tool):
    """
    Ask human for input or clarification
    """

    name: str = "ask_human"
    description: str = "Ask the human user for input, clarification, or additional information when needed."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Question to ask the user",
            }
        },
        "required": ["question"],
    }

    async def execute(self, question: str) -> str:
        """
        Ask human for input

        Args:
            question: Question to ask

        Returns:
            User's response
        """
        print(f"\n{'='*60}")
        print(f"AGENT QUESTION: {question}")
        print(f"{'='*60}")
        response = input("Your response: ").strip()
        return response or "No response provided"

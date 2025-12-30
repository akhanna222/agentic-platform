"""
ReAct (Reasoning and Acting) agent implementation
"""

from abc import abstractmethod
from typing import Any, Dict

from loguru import logger

from app.agent.base import Agent
from app.schema import AgentState


class ReActAgent(Agent):
    """
    ReAct agent that implements the Reasoning and Acting pattern

    The agent alternates between:
    - Think: Reasoning about the current state and deciding next action
    - Act: Executing the decided action
    """

    async def step(self) -> dict[str, Any]:
        """
        Execute one ReAct cycle (Think -> Act)

        Returns:
            Dictionary with step results
        """
        try:
            # Think: Decide what to do
            logger.debug(f"ReAct agent {self.name} - Think phase")
            thought = await self.think()

            # Check if we're done thinking
            if thought.get("done", False):
                return {
                    "done": True,
                    "response": thought.get("response", "Task completed"),
                    "action": "completed",
                }

            # Act: Execute the decision
            logger.debug(f"ReAct agent {self.name} - Act phase")
            action_result = await self.act(thought)

            # Check if action completed the task
            if action_result.get("done", False):
                return {
                    "done": True,
                    "response": action_result.get("response", "Task completed"),
                    "action": "completed",
                }

            return {
                "done": False,
                "action": action_result.get("action", "unknown"),
                "observation": action_result.get("observation", ""),
            }

        except Exception as e:
            logger.error(f"Error in ReAct step: {str(e)}")
            self.state = AgentState.ERROR
            raise

    @abstractmethod
    async def think(self) -> dict[str, Any]:
        """
        Thinking phase: Analyze current state and decide next action

        Returns:
            Dictionary containing:
                - done: bool indicating if task is complete
                - response: str with final response (if done)
                - action: str describing what action to take
                - reasoning: str explaining the thought process
        """
        pass

    @abstractmethod
    async def act(self, thought: dict[str, Any]) -> dict[str, Any]:
        """
        Acting phase: Execute the decided action

        Args:
            thought: The thought/decision from the think phase

        Returns:
            Dictionary containing:
                - done: bool indicating if task is complete
                - observation: str with action result
                - action: str describing what was done
        """
        pass

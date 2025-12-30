"""
Data analysis agent specialized for data analysis and visualization
"""

from loguru import logger

from app.agent.toolcall import ToolCallAgent
from app.config import get_config
from app.prompts import get_data_analysis_prompt, DATA_ANALYSIS_NEXT_STEP_PROMPT
from app.tools.collection import ToolCollection
from app.tools.control import TerminateTool
from app.tools.visualization import (
    DataVisualizationTool,
    VisualizationPrepareTool,
    NormalPythonExecuteTool,
)


class DataAnalysisAgent(ToolCallAgent):
    """
    Specialized agent for data analysis and visualization

    Equipped with data analysis tools, visualization capabilities,
    and Python execution for statistical analysis
    """

    max_steps: int = 20
    max_observation_length: int = 15000

    def __init__(self, **data):
        # Get workspace directory for prompt
        config = get_config()
        workspace_dir = config.platform.workspace_dir

        # Set system prompt with workspace directory
        if "system_prompt" not in data:
            data["system_prompt"] = get_data_analysis_prompt(workspace_dir)

        # Initialize with data analysis tools
        if "tool_collection" not in data:
            data["tool_collection"] = ToolCollection()
            data["tool_collection"].add_tool(NormalPythonExecuteTool())
            data["tool_collection"].add_tool(VisualizationPrepareTool())
            data["tool_collection"].add_tool(DataVisualizationTool())
            data["tool_collection"].add_tool(TerminateTool())

            # Add basic file tools for data loading
            from app.tools.builtin import FileReadTool, FileWriteTool, FileListTool

            data["tool_collection"].add_tool(FileReadTool())
            data["tool_collection"].add_tool(FileWriteTool())
            data["tool_collection"].add_tool(FileListTool())

        if "name" not in data:
            data["name"] = "DataAnalysisAgent"
        if "description" not in data:
            data["description"] = "Specialized agent for data analysis, visualization, and statistical computation"

        super().__init__(**data)

    @classmethod
    async def create(cls, **kwargs) -> "DataAnalysisAgent":
        """
        Factory method to create data analysis agent

        Returns:
            Initialized DataAnalysisAgent
        """
        agent = cls(**kwargs)
        logger.info(f"Created DataAnalysisAgent with {len(agent.tool_collection.tools)} tools")
        return agent

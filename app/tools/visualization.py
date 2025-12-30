"""
Data visualization tools for creating charts and graphs
"""

import base64
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from app.config import get_config
from app.tools.base import Tool


class DataVisualizationTool(Tool):
    """
    Create data visualizations using matplotlib, seaborn, or plotly
    """

    name: str = "data_visualization"
    description: str = """Create data visualizations and save them as images. Supports:
- Line plots, bar charts, scatter plots
- Histograms, box plots
- Heatmaps, correlation matrices
- Interactive plots with plotly

Provide Python code that creates a visualization using matplotlib, seaborn, or plotly."""

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to create visualization. Use 'plt' for matplotlib, 'sns' for seaborn, or 'fig' for plotly. Save with plt.savefig('output.png') or fig.write_html('output.html')",
            },
            "output_file": {
                "type": "string",
                "description": "Output filename (e.g., 'chart.png', 'plot.html')",
                "default": "visualization.png",
            },
            "library": {
                "type": "string",
                "description": "Visualization library to use",
                "enum": ["matplotlib", "seaborn", "plotly"],
                "default": "matplotlib",
            },
        },
        "required": ["code"],
    }

    async def execute(
        self, code: str, output_file: str = "visualization.png", library: str = "matplotlib"
    ) -> str:
        """
        Create data visualization

        Args:
            code: Python code for visualization
            output_file: Output filename
            library: Visualization library

        Returns:
            Result message
        """
        try:
            import matplotlib

            matplotlib.use("Agg")  # Non-interactive backend
            import matplotlib.pyplot as plt

            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            output_path = workspace / output_file

            # Prepare execution environment
            local_vars = {"plt": plt, "output_path": str(output_path)}

            if library == "seaborn" or "sns" in code:
                try:
                    import seaborn as sns

                    local_vars["sns"] = sns
                except ImportError:
                    return "Error: seaborn not installed. Install with: pip install seaborn"

            if library == "plotly" or "plotly" in code.lower():
                try:
                    import plotly.graph_objects as go
                    import plotly.express as px

                    local_vars["go"] = go
                    local_vars["px"] = px
                    local_vars["plotly"] = __import__("plotly")
                except ImportError:
                    return "Error: plotly not installed. Install with: pip install plotly"

            # Add numpy and pandas
            try:
                import numpy as np
                import pandas as pd

                local_vars["np"] = np
                local_vars["pd"] = pd
            except ImportError:
                pass

            # Execute visualization code
            exec(code, {"__builtins__": __builtins__}, local_vars)

            # Check if file was created
            if output_path.exists():
                file_size = output_path.stat().st_size
                return f"Visualization created successfully: {output_file} ({file_size} bytes)"
            else:
                # If no file created, try to save current matplotlib figure
                if library == "matplotlib" or library == "seaborn":
                    plt.savefig(output_path, dpi=150, bbox_inches="tight")
                    plt.close()
                    return f"Visualization saved: {output_file}"
                else:
                    return "Warning: Visualization code executed but no output file was created. Make sure to call plt.savefig() or fig.write_html()."

        except Exception as e:
            logger.error(f"Visualization error: {str(e)}")
            return f"Error: {str(e)}"


class VisualizationPrepareTool(Tool):
    """
    Prepare data for visualization
    """

    name: str = "visualization_prepare"
    description: str = "Load and prepare data for visualization. Supports CSV, JSON, and other data formats."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to data file (relative to workspace)",
            },
            "file_type": {
                "type": "string",
                "description": "Data file type",
                "enum": ["csv", "json", "excel", "parquet"],
                "default": "csv",
            },
        },
        "required": ["file_path"],
    }

    async def execute(self, file_path: str, file_type: str = "csv") -> str:
        """
        Prepare data for visualization

        Args:
            file_path: Path to data file
            file_type: Type of data file

        Returns:
            Data summary
        """
        try:
            import pandas as pd

            config = get_config()
            workspace = Path(config.platform.workspace_dir)
            full_path = workspace / file_path

            if not full_path.exists():
                return f"Error: File not found: {file_path}"

            # Load data
            if file_type == "csv":
                df = pd.read_csv(full_path)
            elif file_type == "json":
                df = pd.read_json(full_path)
            elif file_type == "excel":
                df = pd.read_excel(full_path)
            elif file_type == "parquet":
                df = pd.read_parquet(full_path)
            else:
                return f"Error: Unsupported file type: {file_type}"

            # Generate summary
            summary = []
            summary.append(f"Data loaded from {file_path}")
            summary.append(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            summary.append(f"\nColumns: {', '.join(df.columns.tolist())}")
            summary.append(f"\nData types:\n{df.dtypes.to_string()}")
            summary.append(f"\nFirst few rows:\n{df.head().to_string()}")
            summary.append(f"\nSummary statistics:\n{df.describe().to_string()}")

            return "\n".join(summary)

        except ImportError:
            return "Error: pandas not installed. Install with: pip install pandas"
        except Exception as e:
            logger.error(f"Data preparation error: {str(e)}")
            return f"Error: {str(e)}"


class NormalPythonExecuteTool(Tool):
    """
    Execute Python code for data analysis
    """

    name: str = "python_execute_analysis"
    description: str = "Execute Python code for data analysis, computation, or data manipulation. Has access to numpy, pandas, and other data libraries."

    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute. Use 'result' variable to return a value.",
            }
        },
        "required": ["code"],
    }

    async def execute(self, code: str) -> str:
        """
        Execute Python code for analysis

        Args:
            code: Python code to execute

        Returns:
            Execution result
        """
        try:
            # Prepare execution environment with data analysis libraries
            local_vars = {}
            global_vars = {"__builtins__": __builtins__}

            # Import common libraries
            try:
                import numpy as np
                import pandas as pd

                global_vars["np"] = np
                global_vars["pd"] = pd
            except ImportError:
                pass

            # Execute code
            exec(code, global_vars, local_vars)

            # Get result
            if "result" in local_vars:
                result = local_vars["result"]
                # Format result nicely
                if hasattr(result, "to_string"):  # pandas DataFrame/Series
                    return result.to_string()
                else:
                    return str(result)
            else:
                return "Code executed successfully (no result variable set)"

        except Exception as e:
            logger.error(f"Python execution error: {str(e)}")
            return f"Error: {str(e)}"

"""
Agentic Platform - An autonomous AI agent framework
"""

import sys
import warnings

# Check Python version compatibility
if sys.version_info < (3, 11) or sys.version_info >= (3, 14):
    ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    warnings.warn(
        f"Warning: Unsupported Python version {ver}, please use 3.11-3.13",
        stacklevel=2,
    )

__version__ = "0.1.0"

from app.agent.base import Agent
from app.agent.platform import PlatformAgent

__all__ = ["Agent", "PlatformAgent", "__version__"]

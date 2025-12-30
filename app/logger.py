"""
Logging configuration for the agentic platform
"""

import sys
from loguru import logger

from app.config import get_config


def setup_logger():
    """Configure the logger with appropriate settings"""
    config = get_config()

    # Remove default handler
    logger.remove()

    # Add custom handler with formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.platform.log_level,
        colorize=True,
    )

    # Add file handler for persistent logs
    logger.add(
        f"{config.platform.workspace_dir}/platform.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    return logger


# Initialize logger on import
setup_logger()

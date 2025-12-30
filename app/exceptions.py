"""
Custom exceptions for the agentic platform
"""


class PlatformException(Exception):
    """Base exception for platform errors"""

    pass


class TokenLimitExceeded(PlatformException):
    """Raised when token limit is exceeded"""

    pass


class AgentExecutionError(PlatformException):
    """Raised when agent execution fails"""

    pass


class ToolExecutionError(PlatformException):
    """Raised when tool execution fails"""

    pass


class ConfigurationError(PlatformException):
    """Raised when configuration is invalid"""

    pass


class LLMError(PlatformException):
    """Raised when LLM interaction fails"""

    pass

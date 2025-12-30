"""
Configuration management for the agentic platform
"""

import os
import threading
from pathlib import Path
from typing import Any, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from pydantic import BaseModel, Field


class LLMSettings(BaseModel):
    """LLM configuration settings"""

    model: str = "gpt-4o"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_type: str = "openai"  # openai, azure, bedrock
    temperature: float = 0.7
    max_tokens: int = 4096
    max_completion_tokens: Optional[int] = None
    timeout: int = 120
    max_retries: int = 3

    # AWS Bedrock specific
    aws_region: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # Azure specific
    azure_deployment: Optional[str] = None
    api_version: Optional[str] = None


class BrowserSettings(BaseModel):
    """Browser automation settings"""

    headless: bool = True
    disable_security: bool = False
    chrome_instance_path: Optional[str] = None
    wss_url: Optional[str] = None
    cdp_url: Optional[str] = None
    proxy: Optional[str] = None


class SearchSettings(BaseModel):
    """Search engine configuration"""

    engine: str = "duckduckgo"  # duckduckgo, google, baidu
    fallback_engines: list[str] = Field(default_factory=lambda: ["duckduckgo"])
    max_retries: int = 3
    language: str = "en"
    country: str = "us"


class SandboxSettings(BaseModel):
    """Sandbox execution environment settings"""

    enabled: bool = False
    docker_image: str = "python:3.12-slim"
    timeout: int = 300
    memory_limit: str = "512m"
    cpu_limit: str = "1.0"
    network_enabled: bool = False


class PlatformSettings(BaseModel):
    """General platform settings"""

    workspace_dir: str = "./workspace"
    log_level: str = "INFO"
    max_agent_steps: int = 20
    enable_human_feedback: bool = True


class Config:
    """Singleton configuration manager"""

    _instance: Optional["Config"] = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if Config._initialized:
            return

        with Config._lock:
            if Config._initialized:
                return

            # Load configuration from file
            config_path = Path("config/config.toml")
            if not config_path.exists():
                config_path = Path("config/config.example.toml")

            if config_path.exists():
                with open(config_path, "rb") as f:
                    config_data = tomllib.load(f)
            else:
                config_data = {}

            # Initialize settings from config file or environment
            self.llm = self._load_llm_settings(config_data.get("llm", {}))
            self.browser = BrowserSettings(**config_data.get("browser", {}))
            self.search = SearchSettings(**config_data.get("search", {}))
            self.sandbox = SandboxSettings(**config_data.get("sandbox", {}))
            self.platform = PlatformSettings(**config_data.get("platform", {}))

            # Create workspace directory if it doesn't exist
            workspace = Path(self.platform.workspace_dir)
            workspace.mkdir(parents=True, exist_ok=True)

            Config._initialized = True

    def _load_llm_settings(self, config: dict[str, Any]) -> LLMSettings:
        """Load LLM settings from config or environment variables"""
        # Override with environment variables if present
        if os.getenv("OPENAI_API_KEY"):
            config["api_key"] = os.getenv("OPENAI_API_KEY")
        if os.getenv("OPENAI_API_BASE"):
            config["api_base"] = os.getenv("OPENAI_API_BASE")
        if os.getenv("AWS_REGION"):
            config["aws_region"] = os.getenv("AWS_REGION")
        if os.getenv("AWS_ACCESS_KEY_ID"):
            config["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
        if os.getenv("AWS_SECRET_ACCESS_KEY"):
            config["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")

        return LLMSettings(**config)

    def get_llm_config(self) -> dict[str, Any]:
        """Get LLM configuration as dictionary"""
        return self.llm.model_dump()


# Global config instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get or create global config instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

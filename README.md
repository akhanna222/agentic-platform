# Agentic Platform

A powerful, extensible autonomous AI agent framework for building intelligent agents capable of executing complex tasks through natural language interaction.

## Overview

The Agentic Platform provides a complete framework for developing AI agents that can:

- **Execute Complex Tasks**: Break down and accomplish multi-step objectives autonomously
- **Use Tools Dynamically**: Access and utilize various tools including file operations, web search, Python execution, and more
- **Support Multiple LLM Providers**: Compatible with OpenAI, Azure OpenAI, and AWS Bedrock
- **Maintain Conversation Context**: Intelligent memory management for coherent long-running tasks
- **Extensible Architecture**: Easy to add custom tools and extend functionality

## Key Features

### 🤖 Specialized Agent System
- **Platform Agent**: General-purpose with all tools
- **Browser Agent**: Web automation and scraping specialist
- **Data Analysis Agent**: Data visualization expert
- **MCP Agent**: External tool integration via Model Context Protocol
- **FullStack Ship Agent**: Complete SaaS builder (Next.js + Supabase + Stripe)
- Multi-step reasoning and execution
- Automatic tool selection and usage
- Stuck detection and recovery
- Configurable execution limits

### 🛠️ Built-in Tools
- **File Operations**: Read, write, and list files in workspace
- **Python Execution**: Run Python code safely
- **Web Search**: Search the internet using DuckDuckGo
- **Time/Date**: Get current timestamp
- **Extensible**: Easy to add custom tools

### 🔌 LLM Provider Support
- OpenAI (GPT-4o, GPT-4-turbo, GPT-3.5-turbo)
- Azure OpenAI
- AWS Bedrock (Claude models)
- Custom endpoints

### 📊 Advanced Features
- Token counting and management
- Conversation memory with automatic pruning
- Async/await architecture for performance
- Comprehensive logging
- Sandbox execution support (optional)

## 🌐 Web UI - Lovable-Inspired Interface

The Agentic Platform includes a beautiful web interface for interacting with all agents visually!

**Quick Start with Web UI:**

```bash
# Install minimal dependencies
pip install -r requirements-minimal.txt

# Set your API key
export OPENAI_API_KEY=sk-...

# Start the web server
python web_server.py
```

Then open http://localhost:8000 in your browser!

**Features:**
- 🎨 Modern gradient UI with smooth animations
- 🤖 Select from 5 specialized agents
- 💬 Real-time WebSocket streaming
- 📝 Session history and management
- 📱 Fully responsive design

See [WEB_UI_DEPLOYMENT.md](WEB_UI_DEPLOYMENT.md) for full deployment guide.

---

## Quick Start (CLI Mode)

### Prerequisites

- Python 3.11, 3.12, or 3.13
- OpenAI API key (or other LLM provider credentials)
- `uv` package manager (recommended) or `pip`

### Installation

#### Using uv (Recommended)

```bash
# Install uv if you don't have it
pip install uv

# Clone the repository
git clone https://github.com/yourusername/agentic-platform.git
cd agentic-platform

# Install dependencies
uv pip install -r requirements.txt

# Or install in a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

#### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Create your configuration file:

```bash
cp config/config.example.toml config/config.toml
```

2. Edit `config/config.toml` and add your API key:

```toml
[llm]
model = "gpt-4o"
api_key = "your-api-key-here"  # Or set OPENAI_API_KEY env variable
api_type = "openai"
temperature = 0.7
max_tokens = 4096
```

Alternatively, set environment variables:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Running the Agent

#### Interactive Mode

```bash
# Default platform agent
python main.py

# Specific agent type
python main.py --agent browser  # For web automation
python main.py --agent data     # For data analysis
python main.py --agent mcp      # For external tools
python main.py --agent ship     # For SaaS building
```

Then enter your task when prompted.

#### Command Line Mode

```bash
# Platform agent
python main.py --prompt "Create a file called hello.txt with the text 'Hello World' and read it back"

# Browser agent
python main.py --agent browser --prompt "Go to example.com and extract all links"

# Data analysis agent
python main.py --agent data --prompt "Create a bar chart of sales data"

# FullStack Ship agent
python main.py --agent ship --prompt "Build a SaaS app for task management"
```

#### Python API

```python
import asyncio
from app.agent.platform import PlatformAgent

async def main():
    # Create agent
    agent = await PlatformAgent.create(
        name="MyAgent",
        max_steps=20
    )

    # Run task
    response = await agent.run("What is the current time?")
    print(response)

    # Cleanup
    await agent.cleanup()

asyncio.run(main())
```

## Architecture

### Project Structure

```
agentic-platform/
├── app/
│   ├── agent/           # Agent implementations
│   │   ├── base.py      # Base agent class
│   │   └── platform.py  # Main platform agent
│   ├── tools/           # Tool system
│   │   ├── base.py      # Tool base classes
│   │   ├── builtin.py   # Built-in tools
│   │   └── collection.py # Tool management
│   ├── config.py        # Configuration management
│   ├── llm.py          # LLM integration
│   ├── schema.py       # Data models
│   ├── logger.py       # Logging setup
│   └── exceptions.py   # Custom exceptions
├── config/
│   └── config.example.toml  # Configuration template
├── examples/           # Example scripts
├── workspace/          # Agent workspace (auto-created)
├── main.py            # Main entry point
├── requirements.txt   # Dependencies
└── README.md         # This file
```

### Core Components

#### Agent System
- **BaseAgent**: Abstract base class providing core agent functionality
- **PlatformAgent**: Main implementation with tool calling capabilities
- Async execution model
- State management and error handling

#### Tool System
- **Tool**: Base class for all tools
- **ToolCollection**: Manages available tools
- **Built-in Tools**: File ops, Python execution, web search, etc.
- Easy extension with custom tools

#### LLM Integration
- Multi-provider support (OpenAI, Azure, Bedrock)
- Token counting and management
- Retry logic with exponential backoff
- Streaming support

## Configuration Options

### LLM Settings

```toml
[llm]
model = "gpt-4o"              # LLM model to use
api_type = "openai"            # openai, azure, or bedrock
api_key = "your-key"           # API key
temperature = 0.7              # Sampling temperature
max_tokens = 4096              # Maximum tokens per request
timeout = 120                  # Request timeout in seconds
max_retries = 3                # Maximum retry attempts
```

### Platform Settings

```toml
[platform]
workspace_dir = "./workspace"   # Agent workspace directory
log_level = "INFO"             # DEBUG, INFO, WARNING, ERROR
max_agent_steps = 20           # Maximum steps per task
enable_human_feedback = true   # Enable human-in-the-loop
```

### Browser Settings (Optional)

```toml
[browser]
headless = true
disable_security = false
# chrome_instance_path = "/path/to/chrome"
```

### Search Settings

```toml
[search]
engine = "duckduckgo"
fallback_engines = ["duckduckgo"]
language = "en"
country = "us"
```

## Examples

### Example 1: File Operations

```python
import asyncio
from app.agent.platform import PlatformAgent

async def main():
    agent = await PlatformAgent.create()

    response = await agent.run(
        "Create a Python script that prints 'Hello World' and save it as hello.py"
    )

    print(response)
    await agent.cleanup()

asyncio.run(main())
```

### Example 2: Web Search and Analysis

```python
import asyncio
from app.agent.platform import PlatformAgent

async def main():
    agent = await PlatformAgent.create(max_steps=15)

    response = await agent.run(
        "Search for the latest news about AI and summarize the top 3 results"
    )

    print(response)
    await agent.cleanup()

asyncio.run(main())
```

### Example 3: Data Processing

```python
import asyncio
from app.agent.platform import PlatformAgent

async def main():
    agent = await PlatformAgent.create()

    response = await agent.run(
        "Calculate the first 10 Fibonacci numbers and save them to fibonacci.txt"
    )

    print(response)
    await agent.cleanup()

asyncio.run(main())
```

## Creating Custom Tools

You can easily extend the platform with custom tools:

```python
from app.tools.base import Tool
from typing import Any

class MyCustomTool(Tool):
    name: str = "my_custom_tool"
    description: str = "Description of what this tool does"
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "First parameter"
            }
        },
        "required": ["param1"]
    }

    async def execute(self, param1: str) -> str:
        # Your tool logic here
        result = f"Processed: {param1}"
        return result

# Register the tool
from app.tools.collection import get_tool_collection
tool_collection = get_tool_collection()
tool_collection.add_tool(MyCustomTool())
```

## Deployment

### Docker Deployment

```bash
# Build the image
docker build -t agentic-platform .

# Run with environment variables
docker run -it \
  -e OPENAI_API_KEY=your-key \
  -v $(pwd)/workspace:/app/workspace \
  agentic-platform
```

Or using docker-compose:

```bash
# Set environment variables in .env file
echo "OPENAI_API_KEY=your-key" > .env

# Run
docker-compose up
```

### AWS Deployment

See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) for detailed instructions on deploying to AWS ECS, EC2, or Lambda.

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Code Quality

```bash
# Install dev tools
pip install black ruff

# Format code
black app/ main.py

# Lint code
ruff check app/ main.py
```

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure you're in the project root and have installed dependencies
pip install -r requirements.txt
```

**API Key Issues**
```bash
# Verify your API key is set
echo $OPENAI_API_KEY

# Or check config/config.toml
```

**Permission Errors**
```bash
# Ensure workspace directory is writable
chmod 755 workspace/
```

## Performance Tips

1. **Token Management**: Monitor token usage and adjust `max_tokens` in config
2. **Step Limits**: Set appropriate `max_steps` for your tasks (default: 20)
3. **Memory Limits**: The system auto-prunes conversation history to stay within limits
4. **Async Operations**: Use async/await for concurrent operations

## Security Considerations

- The platform runs code in a restricted environment
- File operations are limited to the workspace directory
- Bash execution is disabled by default
- Review and audit custom tools before deployment
- Use environment variables for sensitive credentials
- Never commit API keys to version control

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review examples in the `examples/` directory

## Acknowledgments

This project draws inspiration from various open-source AI agent frameworks and the broader AI community. Built with modern Python best practices and designed for extensibility and production use.

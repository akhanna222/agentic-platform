# Quick Start Guide

Get up and running with Agentic Platform in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- OpenAI API key or other LLM provider credentials
- `uv` package manager (recommended) or `pip`

## Installation Steps

### 1. Install uv (if not already installed)

```bash
pip install uv
```

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/agentic-platform.git
cd agentic-platform

# Install dependencies using uv
uv pip install -r requirements.txt

# Or use pip with virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure

```bash
# Create config file
cp config/config.example.toml config/config.toml

# Set your API key via environment variable (recommended)
export OPENAI_API_KEY="your-api-key-here"

# Or edit config/config.toml directly
```

### 4. Run Your First Agent

```bash
# Interactive mode
python main.py

# Command line mode
python main.py --prompt "What is the current time?"

# Run an example
python examples/simple_task.py
```

## Your First Task

Try this simple example:

```bash
python main.py --prompt "Create a file called test.txt with 'Hello World' and read it back"
```

The agent will:
1. Create the file in the workspace
2. Write the content
3. Read it back to verify
4. Report the result

## Next Steps

### Try More Examples

```bash
# File operations
python examples/file_operations.py

# Web search
python main.py --prompt "Search for the latest Python news and summarize it"

# Python execution
python main.py --prompt "Calculate the first 10 prime numbers"
```

### Use the Python API

Create `my_agent.py`:

```python
import asyncio
from app.agent.platform import PlatformAgent


async def main():
    # Create agent
    agent = await PlatformAgent.create(
        name="MyAssistant",
        max_steps=15
    )

    # Run task
    response = await agent.run("Your task here")
    print(response)

    # Cleanup
    await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python my_agent.py
```

### Configure for Different LLM Providers

#### OpenAI (default)

```toml
[llm]
model = "gpt-4o"
api_key = "your-key"  # or use OPENAI_API_KEY env var
api_type = "openai"
```

#### Azure OpenAI

```toml
[llm]
model = "gpt-4o"
api_type = "azure"
api_key = "your-azure-key"
api_base = "https://your-resource.openai.azure.com/"
azure_deployment = "your-deployment-name"
api_version = "2024-02-01"
```

#### AWS Bedrock

```toml
[llm]
model = "anthropic.claude-3-sonnet"
api_type = "bedrock"
aws_region = "us-east-1"
# Set AWS credentials via environment variables:
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
```

## Common Tasks

### View Logs

Logs are saved to `workspace/platform.log`:

```bash
tail -f workspace/platform.log
```

### List Available Tools

The platform includes these built-in tools:
- `file_read` - Read files from workspace
- `file_write` - Write files to workspace
- `file_list` - List directory contents
- `python_execute` - Execute Python code
- `web_search` - Search the web
- `get_current_time` - Get current timestamp

### Adjust Agent Behavior

In `config/config.toml`:

```toml
[platform]
max_agent_steps = 30  # Increase for complex tasks
log_level = "DEBUG"   # More verbose logging

[llm]
temperature = 0.3     # Lower for more deterministic responses
max_tokens = 8192     # Increase for longer responses
```

## Troubleshooting

### Import Errors

```bash
# Make sure you're in the project directory
cd agentic-platform

# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Not Found

```bash
# Check environment variable is set
echo $OPENAI_API_KEY

# Or verify config file
cat config/config.toml | grep api_key
```

### Module Not Found

```bash
# Ensure you're in the right directory
pwd  # Should show .../agentic-platform

# Check Python path
python -c "import sys; print(sys.path)"
```

## What's Next?

1. **Read the full README** - [README.md](README.md)
2. **Deploy to AWS** - [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)
3. **Add custom tools** - See [CONTRIBUTING.md](CONTRIBUTING.md)
4. **Run tests** - `pytest tests/`
5. **Explore examples** - Check `examples/` directory

## Getting Help

- Check [README.md](README.md) for detailed documentation
- Review examples in `examples/` directory
- Open an issue on GitHub
- Check logs in `workspace/platform.log`

## Quick Reference

```bash
# Install
uv pip install -r requirements.txt

# Configure
export OPENAI_API_KEY="your-key"

# Run
python main.py

# Test
pytest tests/

# Deploy (see AWS_DEPLOYMENT.md)
docker build -t agentic-platform .
```

Happy building! 🚀

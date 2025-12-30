# Installation Guide

This guide covers different installation scenarios for the Agentic Platform.

## Installation Options

### Option 1: Minimal Install (Recommended for Getting Started)

Perfect for testing the web UI and basic agent functionality.

```bash
pip install -r requirements-minimal.txt
```

**What's included:**
- FastAPI web server with WebSocket support
- OpenAI LLM integration
- Basic tools (file operations, web search)
- Core agent functionality
- All essential dependencies

**What's NOT included:**
- Browser automation (Playwright, Selenium)
- Data visualization (matplotlib, seaborn, plotly)
- Advanced web crawling (crawl4ai)
- MCP server dependencies
- Computer automation tools

**Use this if:**
- You want to try the web UI quickly
- You're building simple automation tasks
- You don't need browser or data visualization
- You're deploying in a lightweight environment

### Option 2: Full Install (All Features)

Includes all specialized agents and tools.

**System Dependencies (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3-dev \
    libx11-dev \
    libxtst-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev
```

**Python Packages:**
```bash
# Note: Some packages have dependency conflicts
# Install in stages:

# Stage 1: Core + Web Server
pip install pydantic openai loguru tenacity tiktoken fastapi uvicorn

# Stage 2: Browser Tools (optional)
pip install playwright selenium browser-use
playwright install chromium

# Stage 3: Data Analysis (optional)
pip install numpy pandas matplotlib seaborn plotly datasets

# Stage 4: MCP (optional)
pip install mcp httpx sse-starlette

# Stage 5: Web Tools (optional)
pip install requests beautifulsoup4 duckduckgo_search

# Stage 6: Async Tools
pip install aiofiles aiohttp
```

**Known Issues:**

1. **crawl4ai dependency conflicts**
   - Conflicts with Pillow versions
   - Solution: Install separately after other packages
   ```bash
   pip install crawl4ai --no-deps
   ```

2. **pyautogui build issues**
   - Requires X11 development headers
   - May fail on headless systems
   - Solution: Skip if not needed for computer control
   ```bash
   pip install pyautogui || echo "Skipping pyautogui"
   ```

3. **html2text build errors**
   - Old package with setup.py issues
   - Solution: Use newer alternative
   ```bash
   pip install markdownify  # Modern alternative
   ```

### Option 3: Docker Install (Isolated Environment)

Recommended for production deployments.

**Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "web_server.py"]
```

**Build and run:**
```bash
docker build -t agentic-platform .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... agentic-platform
```

### Option 4: Virtual Environment (Recommended for Development)

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install minimal dependencies first
pip install -r requirements-minimal.txt

# Test that it works
python -c "from app.agent import PlatformAgent; print('Success!')"

# Optionally install additional features
pip install playwright selenium  # Browser automation
pip install numpy pandas matplotlib  # Data analysis
```

## Verifying Installation

### Test Core Imports

```bash
python3 -c "
from app.agent import PlatformAgent
from app.llm import get_llm
from app.config import get_config
print('✅ All core imports successful')
"
```

### Test Web Server

```bash
python3 -c "
from web_server import app
print('✅ Web server imports successfully')
print(f'✅ Available routes: {len(app.routes)}')
"
```

### Test OpenAI Connection

```bash
# Set your API key first
export OPENAI_API_KEY=sk-...

python3 -c "
import asyncio
from app.llm import get_llm

async def test():
    llm = get_llm()
    response = await llm.chat([{'role': 'user', 'content': 'Say hello'}])
    print(f'✅ OpenAI connection works: {response}')

asyncio.run(test())
"
```

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
# Identify missing package
pip list | grep package-name

# Install specific package
pip install package-name

# Or reinstall all minimal requirements
pip install -r requirements-minimal.txt --force-reinstall
```

### Build Errors

**Problem:** `ERROR: Failed building wheel for X`

**Solutions:**

1. **Install build dependencies:**
```bash
sudo apt-get install -y build-essential python3-dev
```

2. **Use binary packages:**
```bash
pip install --only-binary :all: package-name
```

3. **Skip problematic packages:**
```bash
# Edit requirements.txt and comment out the failing package
# Then install
pip install -r requirements.txt
```

### Playwright Installation

**Problem:** Playwright browsers not installed

**Solution:**
```bash
pip install playwright
playwright install chromium
```

### Permission Errors

**Problem:** Permission denied when installing packages

**Solutions:**

1. **Use virtual environment (recommended):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
```

2. **Use user install:**
```bash
pip install --user -r requirements-minimal.txt
```

3. **Use sudo (not recommended):**
```bash
sudo pip install -r requirements-minimal.txt
```

### SSL Certificate Errors

**Problem:** SSL certificate verification failed

**Solution:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-minimal.txt
```

## Platform-Specific Instructions

### Ubuntu/Debian

```bash
# Update package list
sudo apt-get update

# Install Python and build tools
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev build-essential

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-minimal.txt
```

### macOS

```bash
# Install Python via Homebrew
brew install python@3.11

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-minimal.txt
```

### Windows

```powershell
# Install Python from python.org
# Then in PowerShell:

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements-minimal.txt
```

### AWS EC2

```bash
# Amazon Linux 2
sudo yum update -y
sudo yum install -y python3.11 python3.11-pip python3.11-devel gcc

# Install dependencies
pip3.11 install -r requirements-minimal.txt
```

## Recommended Development Setup

```bash
# 1. Create project directory
mkdir agentic-platform && cd agentic-platform

# 2. Clone repository
git clone <your-repo-url> .

# 3. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 4. Install minimal requirements
pip install -r requirements-minimal.txt

# 5. Install development tools (optional)
pip install pytest pytest-asyncio black ruff

# 6. Create .env file
cat > .env << EOF
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
EOF

# 7. Test installation
python -c "from app.agent import PlatformAgent; print('Success!')"

# 8. Start web server
python web_server.py
```

## Next Steps

After successful installation:

1. **Configure your API key** (see Configuration section in README.md)
2. **Start the web server** with `python web_server.py`
3. **Open http://localhost:8000** in your browser
4. **Try the Platform Agent** with a simple task
5. **Explore specialized agents** (Browser, Data, MCP, Ship)
6. **Read the guides:**
   - WEB_UI_DEPLOYMENT.md - Deploy the web interface
   - FULLSTACK_SHIP_GUIDE.md - Build SaaS apps
   - AWS_DEPLOYMENT.md - Deploy on AWS

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review error messages carefully
3. Check GitHub issues for similar problems
4. Create a new issue with:
   - Python version (`python --version`)
   - Operating system
   - Full error traceback
   - Installation method used

---

**Built with ❤️ by the Agentic Platform Team**

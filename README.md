# Agentic Platform

A powerful, extensible AI agent framework for building intelligent agents with a beautiful web interface.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](docs/LICENSE)

---

## 🚀 Quick Start

**Complete Setup (From Zero to Running):**

```bash
# Clone the repository
git clone https://github.com/akhanna222/agentic-platform.git
cd agentic-platform

# Run interactive setup (installs everything!)
python start.py
```

This will guide you through setup, test your connection, and start the platform!

**Already cloned? Just run:**

```bash
python start.py
```

**Or manual setup:**

```bash
# 1. Install dependencies
pip install -r requirements-minimal.txt

# 2. Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# 3. Start the web UI
python web_server.py

# 4. Open http://localhost:8000
```

**That's it!** You now have a beautiful interface to interact with AI agents.

See [QUICKSTART.md](QUICKSTART.md) for all setup options.

---

## ✨ What Is This?

The Agentic Platform is a complete framework for building autonomous AI agents that can:

- 🤖 **Execute complex tasks** autonomously
- 🛠️ **Use tools dynamically** (file operations, web search, browser automation, etc.)
- 🌐 **Beautiful web interface** inspired by Lovable/Replit
- 🎨 **Build SaaS apps** with modern UIs (Tailwind, shadcn/ui, gradients)
- 🔌 **Multiple LLM providers** (OpenAI, Azure, AWS Bedrock)
- 📊 **Data visualization** and analysis
- 🧪 **Automated testing** and validation

---

## 🎨 Web UI

<div align="center">
  <img src="https://via.placeholder.com/800x400/667eea/ffffff?text=Beautiful+Gradient+UI+%E2%80%A2+Real-time+Updates+%E2%80%A2+6+Specialized+Agents" alt="Web UI Preview" />
</div>

**Features:**
- 🎨 Modern gradient UI with glassmorphism
- 💬 Real-time WebSocket streaming
- 🤖 6 specialized agents
- 📝 Session history
- 📱 Fully responsive

**Start it:**
```bash
python web_server.py
# Open http://localhost:8000
```

---

## 🤖 Available Agents

| Agent | Purpose | Use Case | Icon |
|-------|---------|----------|------|
| **Platform Agent** | General-purpose | File ops, search, Python code | 🤖 |
| **Browser Agent** | Web automation | Scraping, form filling, clicking | 🌐 |
| **Data Agent** | Data analysis | Charts, CSV analysis, visualization | 📊 |
| **MCP Agent** | External tools | API integrations via MCP | 🔌 |
| **Ship Agent** | SaaS builder | Build complete apps with beautiful UIs | 🚀 |
| **Test Agent** | Validation | Check all components work | 🧪 |

---

## 📚 Documentation

### Getting Started
- [Quick Start Guide](QUICKSTART.md) - Get running in 5 minutes
- [Installation Guide](docs/guides/INSTALLATION.md) - Detailed installation options
- [Contributing Guide](docs/guides/CONTRIBUTING.md) - How to contribute

### Deployment
- [AWS Quick Start](docs/deployment/AWS_QUICK_START.md) - Deploy to AWS in 10 minutes
- [AWS Full Guide](docs/deployment/AWS_DEPLOYMENT.md) - Complete AWS deployment
- [Web UI Deployment](docs/deployment/WEB_UI_DEPLOYMENT.md) - Deploy the web interface

### Guides
- [FullStack Ship Agent](docs/guides/FULLSTACK_SHIP_GUIDE.md) - Build SaaS apps

---

## 💻 CLI Usage

### Interactive Mode
```bash
# Default platform agent
python main.py

# Specific agent
python main.py --agent ship
python main.py --agent test
```

### One-Line Commands
```bash
# General task
python main.py --prompt "Search for AI news and summarize"

# Web scraping
python main.py --agent browser --prompt "Scrape HN top posts"

# Data analysis
python main.py --agent data --prompt "Create a sales chart"

# Build a SaaS
python main.py --agent ship --prompt "Build a todo app"

# Run tests
python main.py --agent test --prompt "Validate all components"
```

### Python API
```python
import asyncio
from app.agent import PlatformAgent

async def main():
    agent = await PlatformAgent.create(max_steps=20)
    response = await agent.run("Your task here")
    print(response)
    await agent.cleanup()

asyncio.run(main())
```

---

## 🏗️ Project Structure

```
agentic-platform/
├── README.md                   # This file
├── QUICKSTART.md              # Quick start guide
├── main.py                    # CLI entry point
├── web_server.py              # Web UI server
│
├── docs/                      # Documentation
│   ├── deployment/           # Deployment guides
│   │   ├── AWS_DEPLOYMENT.md
│   │   ├── AWS_QUICK_START.md
│   │   └── WEB_UI_DEPLOYMENT.md
│   ├── guides/              # User guides
│   │   ├── INSTALLATION.md
│   │   ├── FULLSTACK_SHIP_GUIDE.md
│   │   └── CONTRIBUTING.md
│   └── LICENSE
│
├── app/                       # Application code
│   ├── agent/                # Agent implementations
│   │   ├── platform.py      # General-purpose agent
│   │   ├── browser.py       # Browser automation
│   │   ├── data_analysis.py # Data visualization
│   │   ├── mcp.py          # External tool integration
│   │   ├── fullstack_ship.py # SaaS builder
│   │   └── test.py         # Testing & validation
│   ├── tools/               # Tool implementations
│   ├── llm.py              # LLM integration
│   └── config.py           # Configuration
│
├── ui/                       # Web UI files
│   ├── index.html
│   └── assets/
│       ├── css/
│       └── js/
│
├── config/                   # Configuration files
├── tests/                    # Test suite
└── workspace/               # Agent workspace
```

---

## 🛠️ Built-in Tools

### File Operations
- `file_read` - Read files
- `file_write` - Write files
- `file_list` - List directories

### Code Execution
- `python_execute` - Run Python code safely

### Web & Search
- `web_search` - Search the internet
- `browser_use` - Browser automation
- `web_crawl` - Extract web content

### Data & Visualization
- `data_visualization` - Create charts
- `data_prepare` - Prepare data for analysis

### SaaS Building
- `supabase_*` - Database setup and schema
- `stripe_*` - Payment integration
- `deploy_*` - Deployment automation

### Testing
- `test_llm_connection` - Validate LLM API
- `test_database` - Check database connectivity
- `health_check` - System diagnostics

---

## ⚙️ Configuration

### Environment Variables
```bash
# Required
export OPENAI_API_KEY=sk-...

# Optional
export OPENAI_MODEL=gpt-4o-mini
export SUPABASE_URL=https://...
export STRIPE_SECRET_KEY=sk_test_...
```

### Config File
Create `config/config.toml`:
```toml
[llm]
model = "gpt-4o-mini"
temperature = 0.7
max_tokens = 4096

[platform]
max_agent_steps = 20
workspace_dir = "./workspace"
log_level = "INFO"
```

---

## 🎯 Example Tasks

### Beginner
```bash
# File operations
python main.py --prompt "List all Python files"

# Web search
python main.py --prompt "Search for Python news"

# Current time
python main.py --prompt "What time is it?"
```

### Intermediate
```bash
# Web scraping
python main.py --agent browser --prompt "Get top HN posts"

# Data analysis
python main.py --agent data --prompt "Create sample sales chart"

# Code generation
python main.py --prompt "Create a fibonacci calculator"
```

### Advanced
```bash
# Build a complete SaaS app
python main.py --agent ship --prompt "Build a project management SaaS with Stripe subscriptions"

# System validation
python main.py --agent test --prompt "Run comprehensive health check and validate all integrations"
```

---

## 🚀 Deployment

### Local Development
```bash
pip install -r requirements-minimal.txt
python web_server.py
```

### Docker
```bash
docker build -t agentic-platform .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... agentic-platform
```

### AWS (Quick)
```bash
# See docs/deployment/AWS_QUICK_START.md
aws ec2 run-instances ...
```

See [deployment guides](docs/deployment/) for complete instructions.

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test specific component
python main.py --agent test --prompt "Test LLM connection"

# Full health check
python main.py --agent test --prompt "Run comprehensive health check"
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/guides/CONTRIBUTING.md) for:
- Code style guidelines
- How to add new agents
- How to add new tools
- Submitting pull requests

---

## 📊 Dependencies

**Minimal (for web UI):**
- Python 3.11+
- FastAPI & Uvicorn
- OpenAI SDK
- Pydantic

**Full (all features):**
- Browser automation: Playwright, Selenium
- Data analysis: Pandas, Matplotlib, Plotly
- See `requirements.txt` for complete list

---

## 🔒 Security

- Code execution in restricted sandbox
- File operations limited to workspace
- Environment variable-based secrets
- Row Level Security for databases
- Webhook signature verification

See deployment guides for production security.

---

## 📖 Learn More

- **Architecture**: How agents work internally
- **Tools**: Built-in and custom tool development
- **LLM Providers**: OpenAI, Azure, Bedrock setup
- **Advanced Topics**: Memory management, error handling

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](docs/LICENSE) for details.

---

## 🙏 Acknowledgments

- Inspired by OpenManus, Lovable, Replit Agent, and the broader AI community
- Built with modern Python best practices
- Designed for extensibility and production use

---

## 🆘 Support

- **Documentation**: Check the [docs](docs/) folder
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Issues**: Open a GitHub issue
- **Guides**: See [docs/guides/](docs/guides/)

---

<div align="center">

**Built with ❤️ by the Agentic Platform Team**

[Quick Start](QUICKSTART.md) • [Deployment](docs/deployment/) • [Guides](docs/guides/) • [Contributing](docs/guides/CONTRIBUTING.md)

</div>

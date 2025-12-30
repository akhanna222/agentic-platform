# Quick Start - Run Locally in 5 Minutes

Get the Agentic Platform running on your local machine with either the **Web UI** (easiest) or **CLI**.

## Prerequisites

- Python 3.11 or higher
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

---

## 🎨 Option 1: Web UI (Recommended)

The easiest way - beautiful interface with real-time updates.

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd agentic-platform

# Install minimal dependencies (fastest)
pip install -r requirements-minimal.txt
```

### Step 2: Set Your API Key

```bash
# Linux/Mac
export OPENAI_API_KEY=sk-your-key-here

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"

# Windows CMD
set OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Start the Web Server

```bash
python web_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 4: Open Your Browser

Navigate to: **http://localhost:8000**

You'll see a beautiful gradient interface where you can:
- ✨ Select from 5 specialized agents
- 💬 Enter your task in plain English
- 👀 Watch the agent work in real-time
- 📋 View session history

**Try it now!** Select "Platform Agent" and enter:
```
Create a Python script that prints Hello World
```

---

## 💻 Option 2: Command Line (For Developers)

For those who prefer the terminal.

### Step 1: Install & Configure

```bash
pip install -r requirements-minimal.txt
export OPENAI_API_KEY=sk-your-key-here
```

### Step 2: Run a Task

**Interactive mode:**
```bash
python main.py
```

Then type your task when prompted.

**One-line command:**
```bash
python main.py --prompt "Create a file called hello.txt with 'Hello World'"
```

**Use specific agents:**
```bash
# General tasks
python main.py --prompt "Search for Python news and summarize it"

# Browser automation
python main.py --agent browser --prompt "Go to example.com and extract all links"

# Data analysis
python main.py --agent data --prompt "Create a sample sales chart"

# Build a SaaS app
python main.py --agent ship --prompt "Build a todo app with Next.js and Supabase"
```

---

## 🚀 Example Tasks to Try

Copy and paste these into the Web UI or CLI:

### Beginner Tasks
```
List all Python files in this directory
What is the current time?
Create a Python script that calculates fibonacci numbers
```

### Intermediate Tasks
```
Search for the latest AI news and create a summary
Create a CSV file with sample user data (name, email, age)
Build a simple calculator function in Python
```

### Advanced Tasks
```
Go to news.ycombinator.com and extract the top 5 posts (Browser Agent)
Create sample sales data and visualize it with a chart (Data Agent)
Build a blog platform with user authentication (Ship Agent)
```

---

## 🔧 Python API

Use the platform in your own scripts:

```python
import asyncio
from app.agent.platform import PlatformAgent

async def main():
    # Create agent
    agent = await PlatformAgent.create(max_steps=20)

    # Run task
    response = await agent.run("Calculate 2+2 and explain")
    print(response)

    # Cleanup
    await agent.cleanup()

asyncio.run(main())
```

Save as `my_script.py` and run:
```bash
python my_script.py
```

---

## 🎯 What Each Agent Does

Use the right agent for your task:

| Agent | Best For | Example |
|-------|----------|---------|
| **🤖 Platform** | General tasks, files, code | "Create a Python script" |
| **🌐 Browser** | Web scraping, automation | "Scrape data from website" |
| **📊 Data** | Charts, data analysis | "Create a bar chart" |
| **🔌 MCP** | External tool integration | "Connect to my API" |
| **🚀 Ship** | Build complete SaaS apps | "Build a todo app" |

---

## ⚙️ Configuration (Optional)

### Environment Variables

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4o for more complex tasks
LOG_LEVEL=INFO
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

## 🐛 Troubleshooting

### "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements-minimal.txt
```

### "Invalid API key"

**Solution:**
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Set it again
export OPENAI_API_KEY=sk-your-actual-key-here
```

### "Permission denied"

**Solution:**
```bash
# Create workspace directory
mkdir -p workspace
chmod 755 workspace
```

### Port 8000 already in use

**Solution:**
```bash
# Find what's using it (Mac/Linux)
lsof -i :8000

# Find what's using it (Windows)
netstat -ano | findstr :8000

# Use a different port
# Edit web_server.py and change port to 8080
```

### Web UI blank page

**Solution:**
```bash
# Check if server is running
curl http://localhost:8000/api/health

# Should return: {"status":"healthy"}
```

---

## 📁 Project Structure

After running, you'll see:

```
agentic-platform/
├── app/                    # Core platform code
├── ui/                     # Web interface
│   ├── index.html         # Web UI
│   └── assets/
├── workspace/              # Agent workspace (auto-created)
│   ├── files/             # Files created by agents
│   └── outputs/           # Agent outputs
├── main.py                # CLI entry point
├── web_server.py          # Web UI server
└── requirements-minimal.txt  # Dependencies
```

---

## 🎓 Common Workflows

### 1. Quick Test (30 seconds)

```bash
export OPENAI_API_KEY=sk-...
python main.py --prompt "What is 2+2?"
```

### 2. Use Web Interface (Recommended)

```bash
export OPENAI_API_KEY=sk-...
python web_server.py
# Open http://localhost:8000
```

### 3. Build Something Real

```bash
# Start web server
python web_server.py

# In browser, select "Ship Agent" and enter:
# "Build a blog platform with user authentication and Stripe payments"
```

### 4. Automate Tasks

```bash
# Daily scraping script
python main.py --agent browser --prompt "Get top HN posts and save to CSV"

# Analyze the data
python main.py --agent data --prompt "Read posts.csv and create a chart"
```

---

## 💡 Tips for Best Results

1. **Be specific**:
   - ❌ "make fibonacci"
   - ✅ "Create a Python script that calculates the first 10 fibonacci numbers and saves them to fib.txt"

2. **Use the right agent**:
   - File operations → Platform Agent
   - Web scraping → Browser Agent
   - Data visualization → Data Agent
   - Complete apps → Ship Agent

3. **Adjust max steps for complex tasks**:
   ```bash
   python main.py --max-steps 30 --prompt "Build a complete app"
   ```

4. **Check the workspace**:
   ```bash
   ls -la workspace/
   cat workspace/output.txt
   ```

---

## 🎉 You're Ready!

**Fastest way to start:**

```bash
# 1. Install
pip install -r requirements-minimal.txt

# 2. Set API key
export OPENAI_API_KEY=sk-...

# 3. Start web UI
python web_server.py

# 4. Open browser
# http://localhost:8000
```

---

## 📚 Next Steps

Once you're comfortable:

1. **Deploy to AWS** → [AWS_QUICK_START.md](AWS_QUICK_START.md)
2. **Build a SaaS** → [FULLSTACK_SHIP_GUIDE.md](FULLSTACK_SHIP_GUIDE.md)
3. **Web UI Deployment** → [WEB_UI_DEPLOYMENT.md](WEB_UI_DEPLOYMENT.md)
4. **Full Installation Guide** → [INSTALLATION.md](INSTALLATION.md)

---

## 🆘 Need Help?

- **Quick issues**: Check troubleshooting section above
- **Documentation**: See [README.md](README.md)
- **Examples**: Look at example tasks in this guide
- **GitHub**: Open an issue for bugs or questions

---

**Built with ❤️ - Start building amazing things with AI!**

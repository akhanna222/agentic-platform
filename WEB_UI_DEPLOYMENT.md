# Web UI Deployment Guide

The Agentic Platform includes a beautiful web interface inspired by Lovable and Replit, providing an intuitive way to interact with all the platform's agents.

## 🎨 Features

- **Modern UI**: Gradient backgrounds, smooth animations, glassmorphism effects
- **Real-time Updates**: WebSocket connection for live agent output
- **Agent Selection**: Choose from 5 specialized agents
- **Session Management**: Track and review previous tasks
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🚀 Quick Start

### 1. Install Dependencies

**Option A: Minimal Install (Recommended for Testing)**
```bash
pip install -r requirements-minimal.txt
```

This installs only the core dependencies needed for the web UI:
- FastAPI & Uvicorn (web server)
- OpenAI (LLM integration)
- Pydantic (data validation)
- Loguru (logging)
- Basic tools (web search, file operations)

**Option B: Full Install (All Features)**
```bash
# Install system dependencies first (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y build-essential python3-dev

# Install Python packages
pip install -r requirements.txt
```

Note: Some advanced features (browser automation, data visualization) require additional system packages.

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# LLM Configuration (Required)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Optional: Alternative LLM Providers
# AZURE_OPENAI_ENDPOINT=https://...
# AZURE_OPENAI_API_KEY=...
# AWS_BEDROCK_REGION=us-east-1

# Optional: Advanced Features
# SUPABASE_URL=https://...
# SUPABASE_KEY=...
# STRIPE_SECRET_KEY=sk_test_...

# Optional: Sandbox Settings
# ENABLE_SANDBOX=false
# DOCKER_ENABLED=false
```

### 3. Start the Web Server

```bash
python web_server.py
```

The server will start on `http://localhost:8000`

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Access the UI

Open your browser and navigate to:
```
http://localhost:8000
```

## 📋 Using the Web UI

### Step 1: Select an Agent

Choose from 5 specialized agents:

1. **🤖 Platform Agent** - General-purpose with all tools
2. **🌐 Browser Agent** - Web automation and scraping
3. **📊 Data Analysis Agent** - Data visualization expert
4. **🔌 MCP Agent** - External tool integration
5. **🚀 FullStack Ship Agent** - Complete SaaS builder

### Step 2: Describe Your Task

Enter a detailed description of what you want to build:

**Examples:**
- "Build a SaaS app for project management with Stripe subscriptions"
- "Scrape product data from a website and create visualizations"
- "Search for AI news and summarize the top 5 articles"
- "Build a Next.js app with Supabase authentication"

### Step 3: Configure Options

- **Max Steps**: How many reasoning steps the agent can take (10-50)
- Higher steps = more complex tasks, but longer execution time

### Step 4: Watch It Build

- Real-time output shows agent's thinking and actions
- Status badge shows: Running → Completed/Error
- View step count and agent state in footer

### Step 5: Review Results

- All sessions are saved and can be reviewed later
- Click "View" on any session to see full details
- Start new tasks or continue exploring

## 🌐 Production Deployment

### AWS EC2

1. **Launch EC2 Instance**
```bash
# t3.small or larger recommended
# Ubuntu 22.04 LTS
```

2. **Install Dependencies**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip nginx

git clone https://github.com/yourusername/agentic-platform.git
cd agentic-platform

pip3 install -r requirements-minimal.txt
```

3. **Configure Systemd Service**

Create `/etc/systemd/system/agentic-platform.service`:
```ini
[Unit]
Description=Agentic Platform Web Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/agentic-platform
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/usr/bin/python3 web_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable agentic-platform
sudo systemctl start agentic-platform
```

4. **Configure Nginx**

Create `/etc/nginx/sites-available/agentic-platform`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/agentic-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. **Setup SSL with Let's Encrypt**
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Docker Deployment

1. **Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "web_server.py"]
```

2. **Build and Run**

```bash
# Build image
docker build -t agentic-platform .

# Run container
docker run -d \
  --name agentic-platform \
  -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e OPENAI_MODEL=gpt-4o-mini \
  agentic-platform
```

3. **Docker Compose** (with Nginx)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: agentic-platform
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=gpt-4o-mini
    restart: unless-stopped
    volumes:
      - ./data:/app/data

  nginx:
    image: nginx:alpine
    container_name: agentic-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped
```

Start with:
```bash
docker-compose up -d
```

### Replit Deployment

1. **Import Repository**
   - Go to https://replit.com
   - Click "Create Repl" → "Import from GitHub"
   - Enter repository URL

2. **Configure .replit**

Create `.replit`:
```toml
run = "python web_server.py"
language = "python3"

[nix]
channel = "stable-22_11"

[deployment]
run = ["python", "web_server.py"]
deploymentTarget = "cloudrun"
```

3. **Set Environment Variables**
   - Go to "Secrets" (lock icon)
   - Add `OPENAI_API_KEY`
   - Add other required variables

4. **Deploy**
   - Click "Deploy" button
   - Choose "Autoscale" or "Reserved VM"
   - Get your public URL

### Vercel Deployment

While Vercel is optimized for Next.js, you can deploy the Python backend:

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Create `vercel.json`**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "web_server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "web_server.py"
    }
  ]
}
```

3. **Deploy**
```bash
vercel --prod
```

## 🔧 Configuration Options

### Web Server Settings

Edit `web_server.py` to customize:

```python
# Change port
uvicorn.run(app, host="0.0.0.0", port=8080)

# Add HTTPS
uvicorn.run(
    app,
    host="0.0.0.0",
    port=443,
    ssl_keyfile="/path/to/key.pem",
    ssl_certfile="/path/to/cert.pem"
)

# Adjust CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Agent Configuration

Configure agents in `config.toml`:

```toml
[llm]
provider = "openai"
model = "gpt-4o-mini"
temperature = 0.7
max_tokens = 4096

[agents]
default_max_steps = 20
enable_sandbox = false
browser_enabled = true
mcp_enabled = true
```

## 📊 Monitoring and Logs

### View Logs

```bash
# Systemd service logs
sudo journalctl -u agentic-platform -f

# Docker logs
docker logs -f agentic-platform

# Python logs (if running directly)
tail -f logs/agent.log
```

### Health Check

The API provides a health check endpoint:

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T12:00:00Z"
}
```

### Monitor Active Sessions

```bash
curl http://localhost:8000/api/sessions
```

## 🔒 Security Best Practices

1. **Environment Variables**
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, Vault)
   - Rotate API keys regularly

2. **HTTPS**
   - Always use SSL in production
   - Use Let's Encrypt for free certificates
   - Enable HTTP → HTTPS redirect

3. **Rate Limiting**
   - Add rate limiting middleware
   - Limit concurrent sessions
   - Monitor for abuse

4. **Authentication** (Optional Enhancement)
   - Add user authentication
   - Implement session tokens
   - Use OAuth for social login

5. **Firewall Rules**
   - Only expose ports 80, 443
   - Use security groups (AWS)
   - Enable DDoS protection

## 🐛 Troubleshooting

### WebSocket Connection Failed

**Problem**: "WebSocket connection failed"

**Solution**:
- Check if server is running: `curl http://localhost:8000/api/health`
- Verify no firewall blocking port 8000
- Check Nginx WebSocket configuration (see nginx config above)

### Agent Not Responding

**Problem**: Agent starts but never responds

**Solution**:
- Check OpenAI API key is valid
- View server logs for errors
- Verify LLM provider is accessible
- Check rate limits on OpenAI account

### UI Not Loading

**Problem**: Blank page or 404 errors

**Solution**:
- Verify `ui/` directory exists
- Check static files are mounted: `app.mount("/ui", StaticFiles(directory="ui"))`
- Try accessing directly: `http://localhost:8000/ui/index.html`

### Port Already in Use

**Problem**: "Address already in use" error

**Solution**:
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Or use a different port
python web_server.py --port 8080
```

## 📈 Performance Optimization

### 1. Use Production ASGI Server

For production, use Gunicorn with Uvicorn workers:

```bash
pip install gunicorn

gunicorn web_server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

### 2. Enable Caching

Add caching for agent responses:
- Use Redis for session storage
- Cache LLM responses for similar queries
- Implement response compression

### 3. Load Balancing

For high traffic, use multiple instances:
- AWS ELB/ALB
- Nginx load balancer
- Kubernetes with horizontal pod autoscaling

## 🎯 Next Steps

After deployment:

1. **Test All Agents**
   - Platform Agent with file operations
   - Browser Agent with web scraping
   - Data Agent with visualizations
   - MCP Agent with external tools
   - Ship Agent with full SaaS workflow

2. **Add Custom Agents**
   - Create specialized agents for your use case
   - Add custom tools and capabilities
   - Extend the agent collection

3. **Enhance UI**
   - Add user authentication
   - Implement chat history
   - Add code syntax highlighting
   - Create mobile app (PWA)

4. **Monitor and Scale**
   - Set up application monitoring
   - Track agent performance
   - Optimize token usage
   - Scale based on demand

## 💡 Additional Resources

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Agent Documentation**: See `FULLSTACK_SHIP_GUIDE.md`
- **AWS Deployment**: See `AWS_DEPLOYMENT.md`
- **GitHub**: [Your repository URL]

---

**Built with ❤️ by the Agentic Platform Team**

For support, open an issue on GitHub or contact support@your-domain.com

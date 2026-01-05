#!/bin/bash

# ================================================================
# Agentic Platform - AWS EC2 One-Click Deployment Script
# ================================================================
# This script will:
# 1. Install all dependencies
# 2. Set up virtual environment
# 3. Kill any processes on ports 8000-8010
# 4. Ask for OpenAI API key
# 5. Start the web server
# ================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${BLUE}============================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# ================================================================
# Step 1: Check Python Version
# ================================================================

print_header "Step 1: Checking Python Version"

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

print_success "Python version: $(python3 --version)"

if [[ $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) -eq 1 ]]; then
    print_warning "Python 3.11+ recommended, but continuing with $PYTHON_VERSION"
fi

# ================================================================
# Step 2: Set up Virtual Environment
# ================================================================

print_header "Step 2: Setting Up Virtual Environment"

if [ -d "venv" ]; then
    print_info "Virtual environment already exists"
else
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

# ================================================================
# Step 3: Install Dependencies
# ================================================================

print_header "Step 3: Installing Dependencies"

print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

print_info "Installing required packages..."
if [ -f "requirements-minimal.txt" ]; then
    pip install -r requirements-minimal.txt
    print_success "Installed from requirements-minimal.txt"
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Installed from requirements.txt"
else
    print_warning "No requirements file found, installing core packages..."
    pip install fastapi uvicorn websockets python-dotenv openai anthropic loguru pydantic tenacity
fi

# Ensure python-dotenv is installed
pip install python-dotenv > /dev/null 2>&1
print_success "All dependencies installed"

# ================================================================
# Step 4: Kill Processes on Ports 8000-8010
# ================================================================

print_header "Step 4: Cleaning Up Ports"

for PORT in {8000..8010}; do
    PID=$(lsof -ti:$PORT 2>/dev/null || true)
    if [ ! -z "$PID" ]; then
        print_warning "Killing process on port $PORT (PID: $PID)"
        kill -9 $PID 2>/dev/null || sudo kill -9 $PID 2>/dev/null || true
        sleep 1
        print_success "Port $PORT is now free"
    fi
done

print_success "All ports cleaned up"

# ================================================================
# Step 5: Configure OpenAI API Key
# ================================================================

print_header "Step 5: Configure OpenAI API Key"

# Check if .env exists and has a valid key
if [ -f ".env" ]; then
    EXISTING_KEY=$(grep "^OPENAI_API_KEY=" .env | cut -d'=' -f2 || echo "")
    if [[ "$EXISTING_KEY" != "" && "$EXISTING_KEY" != "your-openai-api-key-here" ]]; then
        print_success "OpenAI API key already configured"
        echo -e "${BLUE}Current key: ${EXISTING_KEY:0:10}...${EXISTING_KEY: -4}${NC}"
        read -p "Do you want to update it? (y/N): " UPDATE_KEY
        if [[ ! "$UPDATE_KEY" =~ ^[Yy]$ ]]; then
            print_info "Keeping existing API key"
        else
            EXISTING_KEY=""
        fi
    else
        EXISTING_KEY=""
    fi
else
    EXISTING_KEY=""
fi

# Ask for API key if needed
if [ -z "$EXISTING_KEY" ] || [[ "$EXISTING_KEY" == "your-openai-api-key-here" ]]; then
    echo ""
    print_info "You need an OpenAI API key to use the agents"
    print_info "Get one at: https://platform.openai.com/api-keys"
    echo ""
    read -p "Enter your OpenAI API key (starts with sk-): " OPENAI_KEY

    # Validate key format
    if [[ ! "$OPENAI_KEY" =~ ^sk- ]]; then
        print_error "Invalid API key format (should start with 'sk-')"
        print_warning "Continuing anyway, but agents may not work"
    fi

    # Create or update .env file
    cat > .env << EOF
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=$OPENAI_KEY

# Optional: Supabase Configuration
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-supabase-anon-key

# Optional: Stripe Configuration
# STRIPE_SECRET_KEY=sk_test_your-stripe-key
# STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key

# Optional: LLM Model Selection
# LLM_MODEL=gpt-4o
# LLM_TYPE=openai
EOF

    print_success "API key saved to .env file"
fi

# ================================================================
# Step 6: Test OpenAI Connection
# ================================================================

print_header "Step 6: Testing OpenAI Connection"

python3 << 'EOF'
import os

# Read .env file manually to avoid AssertionError in heredoc
api_key = None
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                api_key = line.split('=', 1)[1].strip()
                break
except FileNotFoundError:
    pass

if api_key and api_key != 'your-openai-api-key-here':
    print(f"✓ API Key configured: {api_key[:10]}...{api_key[-4:]}")

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Connection successful'"}],
            max_tokens=10
        )
        print(f"✓ OpenAI API Working! Response: {response.choices[0].message.content}")
        exit(0)
    except Exception as e:
        print(f"✗ OpenAI API Error: {str(e)[:150]}")
        print("⚠ Continuing anyway, but agents may not work")
        exit(0)
else:
    print("✗ API Key not configured properly")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    print_warning "API test failed, but continuing..."
fi

# ================================================================
# Step 7: Get EC2 Public IP
# ================================================================

print_header "Step 7: Getting EC2 Public IP"

# Try to get public IP from EC2 metadata
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "")

if [ -z "$PUBLIC_IP" ]; then
    # Fallback: get from external service
    PUBLIC_IP=$(curl -s http://checkip.amazonaws.com 2>/dev/null || echo "localhost")
fi

print_success "Public IP: $PUBLIC_IP"

# ================================================================
# Step 8: Configure AWS Security Group (Info Only)
# ================================================================

print_header "Step 8: AWS Security Group Setup"

print_info "To access from your browser, ensure port 8005 is open:"
echo ""
echo "   1. Go to EC2 Dashboard → Security Groups"
echo "   2. Select your instance's security group"
echo "   3. Edit Inbound Rules → Add Rule"
echo "   4. Type: Custom TCP, Port: 8005, Source: 0.0.0.0/0"
echo "   5. Save rules"
echo ""
print_warning "Press Enter to continue..."
read

# ================================================================
# Step 9: Start Web Server
# ================================================================

print_header "Step 9: Starting Web Server"

print_success "All setup complete!"
echo ""
print_info "Starting Agentic Platform Web Server..."
print_info "Server will be available at:"
echo ""
echo -e "   ${GREEN}http://$PUBLIC_IP:8005${NC}"
echo ""
print_info "Press Ctrl+C to stop the server"
echo ""

# Wait a moment
sleep 2

# Start the server
python3 web_server.py

# ================================================================
# Cleanup on exit
# ================================================================

cleanup() {
    echo ""
    print_info "Shutting down server..."
    deactivate 2>/dev/null || true
    print_success "Goodbye!"
}

trap cleanup EXIT

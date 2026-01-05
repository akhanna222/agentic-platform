#!/bin/bash

# ================================================================
# App Preview Script - Start a web server for any workspace app
# ================================================================

echo "🚀 Agentic Platform - App Preview"
echo "=================================="
echo ""

WORKSPACE="/home/user/agentic-platform/workspace"

# List available apps
echo "📁 Available apps in workspace:"
echo ""

apps=()
i=1
for dir in "$WORKSPACE"/*/ ; do
    if [ -d "$dir" ]; then
        app_name=$(basename "$dir")
        apps+=("$app_name")
        echo "  $i) $app_name"
        i=$((i+1))
    fi
done

if [ ${#apps[@]} -eq 0 ]; then
    echo "❌ No apps found in workspace!"
    echo ""
    echo "💡 Use the Ship Agent (🚀) in the web UI to build an app first."
    echo "   Example: 'build a landing page'"
    exit 1
fi

echo ""
echo -n "Select app number (or press Enter for #1): "
read selection

# Default to first app if no selection
if [ -z "$selection" ]; then
    selection=1
fi

# Validate selection
if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt ${#apps[@]} ]; then
    echo "❌ Invalid selection!"
    exit 1
fi

# Get selected app
app_name="${apps[$((selection-1))]}"
app_path="$WORKSPACE/$app_name"

echo ""
echo "✅ Selected: $app_name"
echo ""

# Check if index.html exists
if [ ! -f "$app_path/index.html" ]; then
    echo "⚠️  Warning: No index.html found in $app_name"
    echo "   This might not be a web app."
    echo ""
fi

# Find available port
PORT=8080
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; do
    PORT=$((PORT+1))
done

echo "🌐 Starting web server..."
echo "   App: $app_name"
echo "   Port: $PORT"
echo ""

# Detect public IP (for AWS/cloud)
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ App Preview Ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   🌍 Open in browser:"
if [ "$PUBLIC_IP" != "localhost" ]; then
    echo "      http://$PUBLIC_IP:$PORT"
    echo "      http://localhost:$PORT (if on same machine)"
else
    echo "      http://localhost:$PORT"
fi
echo ""
echo "   📁 Serving: $app_path"
echo "   🛑 Press Ctrl+C to stop"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start server
cd "$app_path"
python3 -m http.server $PORT

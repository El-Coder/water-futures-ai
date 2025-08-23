#!/bin/bash

echo "Setting up Alpaca MCP Server for Water Futures Trading"
echo "======================================================="

# Clone Alpaca MCP server if not exists
if [ ! -d "alpaca-mcp-server" ]; then
    echo "Cloning Alpaca MCP Server..."
    git clone https://github.com/alpacahq/alpaca-mcp-server.git
fi

cd alpaca-mcp-server

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists, if not create template
if [ ! -f .env ]; then
    echo "Creating .env template file..."
    echo "Please copy .env.example to .env and fill in your API keys"
    cat > .env.example << EOF
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_API_SECRET=your_alpaca_api_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
EOF
    echo "❌ .env file not found. Please:"
    echo "   1. Copy .env.example to .env"
    echo "   2. Add your actual Alpaca API credentials to .env"
    echo "   3. Run this script again"
    exit 1
fi

echo "Using existing .env file..."

echo "Starting Alpaca MCP Server..."
python alpaca_mcp_server.py &

echo "✅ Alpaca MCP Server is running!"
echo "You can now trade through the agent mode in the frontend"
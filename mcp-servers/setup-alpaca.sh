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

# Create .env file with API keys
echo "Creating .env file..."
cat > .env << EOF
ALPACA_API_KEY=PKBGCEN19LBO7XSXRV0P
ALPACA_API_SECRET=c4Mbdt3J0cLKPaeUJecD6Db1sTsmiNudz0QdfyaP
ALPACA_BASE_URL=https://paper-api.alpaca.markets
EOF

echo "Starting Alpaca MCP Server..."
python alpaca_mcp_server.py &

echo "✅ Alpaca MCP Server is running!"
echo "You can now trade through the agent mode in the frontend"
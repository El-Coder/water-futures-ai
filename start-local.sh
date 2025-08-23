#!/bin/bash

# Quick start script for local development
# This starts all services needed for the Water Futures AI platform

echo "🚀 Starting Water Futures AI Platform"
echo "===================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}Port $1 is already in use!${NC}"
        return 1
    fi
    return 0
}

# Check required ports
echo -e "${BLUE}Checking ports...${NC}"
check_port 8000 || exit 1
check_port 8001 || exit 1
check_port 8080 || exit 1
check_port 5173 || exit 1

# Start Backend
echo -e "${BLUE}Starting Backend on port 8000...${NC}"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
python main.py &
BACKEND_PID=$!
cd ..
sleep 3

# Start MCP Services
echo -e "${BLUE}Starting MCP Services...${NC}"
cd mcp-servers

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    npm install
fi

# Start MCP HTTP Wrapper on 8080
echo -e "${GREEN}Starting MCP Wrapper on port 8080${NC}"
PORT=8080 BACKEND_URL=http://localhost:8000 node http-wrapper.js &
MCP_PID=$!

# Start Chat Service on 8001
echo -e "${GREEN}Starting Chat Service on port 8001${NC}"
CHAT_PORT=8001 BACKEND_URL=http://localhost:8000 node chat-wrapper.js &
CHAT_PID=$!

cd ..
sleep 2

# Start Frontend
echo -e "${BLUE}Starting Frontend on port 5173...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd ..

# Function to stop all services
cleanup() {
    echo -e "\n${BLUE}Stopping all services...${NC}"
    kill $BACKEND_PID $MCP_PID $CHAT_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Display status
echo -e "\n${GREEN}====================================="
echo "✅ All services started successfully!"
echo "====================================="
echo -e "${NC}"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🤖 Chat Service: http://localhost:8001"
echo "🔌 MCP Wrapper: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep script running
while true; do
    sleep 1
done
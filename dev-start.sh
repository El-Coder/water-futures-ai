#!/bin/bash

echo "🚀 Starting Water Futures AI Development Environment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if required tools are installed
check_requirements() {
    echo -e "${BLUE}Checking requirements...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 is not installed${NC}"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Node.js is not installed${NC}"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}npm is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ All requirements met${NC}"
}

# Start backend
start_backend() {
    echo -e "${BLUE}Starting backend...${NC}"
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        cat > .env << EOF
DEBUG=True
PORT=8000
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
CROSSMINT_API_KEY=your_crossmint_key
VERTEX_ENDPOINT_NAME=
EOF
        echo -e "${RED}Please update .env with your API keys${NC}"
    fi
    
    # Start FastAPI server
    echo -e "${GREEN}Starting FastAPI server on http://localhost:8000${NC}"
    python main.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    cd ..
}

# Start frontend
start_frontend() {
    echo -e "${BLUE}Starting frontend...${NC}"
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "Creating frontend .env file..."
        cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_ANTHROPIC_API_KEY=your_anthropic_api_key_here
EOF
    fi
    
    # Start Vite dev server
    echo -e "${GREEN}Starting React app on http://localhost:5173${NC}"
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    
    cd ..
}

# Start MCP servers
start_mcp_servers() {
    echo -e "${BLUE}Starting MCP servers...${NC}"
    
    cd mcp-servers
    
    if [ ! -d "node_modules" ]; then
        echo "Installing MCP server dependencies..."
        npm install
    fi
    
    # Start MCP HTTP wrapper on port 8080
    echo -e "${GREEN}Starting MCP HTTP Wrapper on port 8080${NC}"
    PORT=8080 node http-wrapper.js &
    MCP_WRAPPER_PID=$!
    echo "MCP Wrapper PID: $MCP_WRAPPER_PID"
    
    # Start Chat service on port 8001
    echo -e "${GREEN}Starting Chat Service on port 8001${NC}"
    CHAT_PORT=8001 BACKEND_URL=http://localhost:8000 node chat-wrapper.js &
    CHAT_PID=$!
    echo "Chat Service PID: $CHAT_PID"
    
    cd ..
}

# Cleanup function
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    
    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Stopped backend"
    fi
    
    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "Stopped frontend"
    fi
    
    # Kill MCP wrapper
    if [ ! -z "$MCP_WRAPPER_PID" ]; then
        kill $MCP_WRAPPER_PID 2>/dev/null
        echo "Stopped MCP wrapper"
    fi
    
    # Kill Chat service
    if [ ! -z "$CHAT_PID" ]; then
        kill $CHAT_PID 2>/dev/null
        echo "Stopped Chat service"
    fi
    
    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

# Set up trap for cleanup on exit
trap cleanup EXIT INT TERM

# Main execution
main() {
    check_requirements
    
    echo -e "\n${BLUE}Starting all services...${NC}\n"
    
    start_backend
    sleep 3  # Give backend time to start
    
    start_frontend
    sleep 2  # Give frontend time to start
    
    start_mcp_servers
    
    echo -e "\n${GREEN}=================================================="
    echo "✅ All services started successfully!"
    echo "=================================================="
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
}

# Run main function
main
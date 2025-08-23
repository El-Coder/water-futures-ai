# Water Futures AI - Development Setup

## 🚀 Quick Start

```bash
# Clone the repo
cd water-futures-ai

# Run everything with one command
./dev-start.sh
```

This starts:
- Backend API on http://localhost:8000
- Frontend on http://localhost:5173
- MCP Servers for trading and farmer assistance

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- Google Cloud CLI (optional for deployment)

## 🛠️ Manual Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DEBUG=True
PORT=8000
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
ANTHROPIC_API_KEY=your_anthropic_key
CROSSMINT_API_KEY=your_crossmint_key
EOF

# Run the backend
python main_simple.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_ANTHROPIC_API_KEY=your_anthropic_key
EOF

# Run the frontend
npm run dev
```

### MCP Server Setup

```bash
# Install Smithery CLI globally
npm install -g @smithery/cli

# Start Trading Agent
cd mcp-servers/trading-agent
npm install
node index.js

# Start Farmer Assistant (in another terminal)
cd mcp-servers/farmer-assistant
npm install
node index.js
```

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│                 │     │                  │     │                │
│  React Frontend │────▶│  FastAPI Backend │────▶│  Vertex AI     │
│                 │     │                  │     │  (ML Models)   │
└─────────────────┘     └──────────────────┘     └────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │                     │
                    │    MCP Servers      │
                    │  - Trading Agent    │
                    │  - Farmer Assistant │
                    │  (Claude-powered)   │
                    └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │                     │
                    │  External Services  │
                    │  - Alpaca Trading   │
                    │  - Crossmint Pay    │
                    │  - News APIs        │
                    └─────────────────────┘
```

## 🔑 API Keys Required

1. **Anthropic (Claude)**: For the chatbot
   - Get from: https://console.anthropic.com

2. **Alpaca**: For trading simulation
   - Get from: https://alpaca.markets (use paper trading keys)

3. **Crossmint**: For government subsidy payments
   - Get from: https://www.crossmint.com/developers

4. **Google Cloud**: For Vertex AI (optional)
   - Set up project: `water-futures-ai`
   - Enable APIs: Vertex AI, Cloud Storage

## 🧪 Testing the Application

### 1. Test the Chatbot
- Click the chat icon in the bottom right
- Ask: "What subsidies am I eligible for?"
- Ask: "Should I buy water futures?"

### 2. Test Trading
- Go to Market Forecast page
- Enter contract code: NQH25
- Generate forecast
- Review AI predictions

### 3. Test Account & Transactions
- View mock government subsidies via Crossmint
- See automated trading transactions
- Check account balance updates

### 4. Upload Historical Data
- Create a CSV with water futures data
- Format:
  ```csv
  date,contract_code,open,high,low,close,volume
  2024-01-01,NQH25,495.50,498.00,494.00,497.25,1234
  ```

## 🔧 Development Commands

### Backend
```bash
# Run tests
pytest

# Format code
black .

# Type checking
mypy .
```

### Frontend
```bash
# Run tests
npm test

# Build for production
npm run build

# Type checking
npm run type-check
```

### MCP Servers
```bash
# Register with Smithery (optional)
smithery publish mcp-servers/trading-agent
smithery publish mcp-servers/farmer-assistant

# Test MCP server locally
smithery test mcp-servers/trading-agent
```

## 🐛 Troubleshooting

### Backend Issues
- **Port 8000 in use**: Change PORT in .env
- **Import errors**: Activate virtual environment
- **API errors**: Check .env file has all keys

### Frontend Issues
- **Blank page**: Check console for errors
- **API connection failed**: Verify backend is running
- **Build errors**: Clear node_modules and reinstall

### MCP Server Issues
- **Connection refused**: Check if backend is running
- **Smithery not found**: Install globally with npm
- **Claude API errors**: Verify ANTHROPIC_API_KEY

## 📦 Deployment

### Deploy to Google Cloud Run
```bash
# Ensure you're authenticated
gcloud auth login
gcloud config set project water-futures-ai

# Deploy with one command
./deploy.sh
```

### Docker Development
```bash
# Run everything with Docker Compose
docker-compose up

# Build images
docker-compose build

# Stop everything
docker-compose down
```

## 🤖 MCP/Smithery Integration

The app includes two MCP servers:

1. **Trading Agent** (`mcp-servers/trading-agent`)
   - Executes trades via Alpaca
   - Analyzes market conditions
   - Runs automated strategies

2. **Farmer Assistant** (`mcp-servers/farmer-assistant`)
   - Claude-powered chat
   - Processes government subsidies via Crossmint
   - Provides personalized recommendations

### Using MCP Servers

```javascript
// Example: Call MCP server from frontend
const response = await fetch('http://localhost:8000/api/v1/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "What subsidies am I eligible for?",
    context: {
      location: "Central Valley",
      droughtSeverity: 4
    }
  })
});
```

## 📊 Sample Data

The app includes sample data for testing:
- Historical water futures prices
- Drought severity maps
- Government subsidy programs
- Mock trading transactions

## 🎯 Hackathon Checklist

- [x] Backend API running
- [x] Frontend displaying data
- [x] Claude chatbot responding
- [x] Trading functionality
- [x] Government subsidies via Crossmint
- [x] MCP servers connected
- [ ] Vertex AI model deployed (optional)
- [ ] Live demo ready

## 📚 Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [Smithery Registry](https://smithery.ai)
- [Crossmint Docs](https://docs.crossmint.com)
- [Alpaca API](https://alpaca.markets/docs)
- [Claude API](https://docs.anthropic.com)
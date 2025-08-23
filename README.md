# 🌾💧 Water Futures AI - Intelligent Agricultural Risk Management Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com/)

## 🎯 Vision

Water Futures AI is an intelligent platform that helps farmers manage water scarcity risks through AI-powered futures trading, automated government subsidy processing, and predictive analytics. The platform combines cutting-edge AI technologies with real-world financial instruments to create a comprehensive risk management solution for agricultural water needs.

## ✨ Key Features

- **🤖 AI-Powered Trading Agent**: Claude-powered assistant with dual-mode operation (Chat Mode for information, Agent Mode for real transactions)
- **📈 Water Futures Trading**: Paper trading integration via Alpaca API for water futures contracts
- **💰 Government Subsidy Processing**: Automated subsidy claims and payments via Crossmint
- **🔮 Predictive Analytics**: Vertex AI-powered price forecasting based on drought conditions
- **🗺️ Drought Monitoring**: Real-time drought severity tracking and visualization
- **⚠️ Trade Approval System**: User-controlled trade execution with explicit approval/decline mechanism
- **📊 Portfolio Management**: Real-time account tracking and position monitoring

## 🏗️ Architecture Overview

The platform consists of:
- **Frontend**: React + TypeScript + Vite with Material-UI
- **Backend**: FastAPI with async support
- **AI Services**: Claude (Anthropic), Vertex AI (Google Cloud)
- **MCP Servers**: Smithery-registered agents for trading and assistance
- **External Integrations**: Alpaca (trading), Crossmint (payments)
- **Database**: PostgreSQL with pgvector for embeddings

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn
- Google Cloud CLI (optional)

### One-Command Setup
```bash
# Clone and start everything
git clone https://github.com/yourusername/water-futures-ai.git
cd water-futures-ai
./dev-start.sh
```

This starts:
- Backend API on http://localhost:8000
- Frontend on http://localhost:5173
- MCP Servers for trading and farmer assistance

## 📦 Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the simplified backend (recommended for development)
python main_simple.py

# Or run the full backend
python main.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start development server
npm run dev
```

### MCP Server Setup

```bash
# Install Smithery CLI
npm install -g @smithery/cli

# Trading Agent Server
cd mcp-servers/trading-agent
npm install
node index.js

# Farmer Assistant Server (new terminal)
cd mcp-servers/farmer-assistant
npm install
node index.js
```

## 🔑 API Keys Required

1. **Anthropic (Claude)** - AI chatbot and agent
   - Get from: https://console.anthropic.com

2. **Alpaca** - Paper trading for water futures
   - Get from: https://alpaca.markets (use paper trading keys)

3. **Crossmint** - Government subsidy payments
   - Get from: https://www.crossmint.com/developers

4. **Google Cloud** - Vertex AI for predictions (optional)
   - Project: `water-futures-ai`
   - Enable: Vertex AI, Cloud Storage APIs

## 🎮 Using the Platform

### 1. Chat Mode (Safe Information Mode)
- Click the chat icon in the bottom right
- Ask questions about water futures, subsidies, market conditions
- No real transactions are executed
- Perfect for learning and analysis

### 2. Agent Mode (Live Trading Mode)
- Toggle "Agent Mode" in the chat interface
- Confirm the warning dialog about real money transactions
- The AI can now:
  - Execute real trades via Alpaca
  - Process subsidy payments via Crossmint
  - Modify account positions

### 3. Trade Approval Flow
When in Agent Mode:
1. AI analyzes your request and suggests a trade
2. Approval dialog appears with trade details
3. You can ACCEPT or DECLINE the trade
4. Only approved trades are executed
5. All transactions are logged

## 📊 API Endpoints

### Core Endpoints

#### Chat & Agent
- `POST /api/v1/chat` - Safe chat mode (no execution)
- `POST /api/v1/agent/execute` - Agent mode with execution capability
- `POST /api/v1/agent/action` - Execute specific approved action

#### Water Futures
- `GET /api/v1/water-futures/current` - Current prices
- `GET /api/v1/water-futures/history` - Historical data
- `POST /api/v1/water-futures/contracts` - Available contracts

#### Forecasting
- `POST /api/v1/forecasts/predict` - Generate price predictions
- `GET /api/v1/forecasts/{id}` - Get specific forecast

#### Trading
- `POST /api/v1/trading/order` - Place order (requires agent mode)
- `GET /api/v1/trading/portfolio` - Portfolio status
- `GET /api/v1/trading/positions` - Current positions

#### News & Analysis
- `GET /api/v1/news/latest` - Water-related news
- `GET /api/v1/embeddings/drought-map` - Drought severity data

### Request Examples

```javascript
// Chat Mode Request
POST /api/v1/chat
{
  "message": "Should I buy water futures given the drought?",
  "context": {
    "location": "Central Valley",
    "droughtSeverity": 4
  }
}

// Agent Mode Trade Execution
POST /api/v1/agent/execute
{
  "message": "Buy 5 NQH25 water futures contracts",
  "mode": "agent",
  "context": {
    "agentModeEnabled": true,
    "location": "Central Valley"
  }
}
```

## 🤖 MCP Server Integration

### Trading Agent (`mcp-servers/trading-agent`)
- Connects to Alpaca for paper trading
- Executes buy/sell orders for water futures
- Maps water futures symbols to tradeable proxies
- Provides real-time market quotes

### Farmer Assistant (`mcp-servers/farmer-assistant`)
- Claude-powered conversational AI
- Processes government subsidies via Crossmint
- Provides personalized recommendations
- Integrates with all platform services

## 🛡️ Security & Safety Features

1. **Dual-Mode Operation**
   - Chat Mode: Information only, no execution
   - Agent Mode: Requires explicit enablement

2. **Trade Approval System**
   - Visual warnings (red UI elements)
   - Confirmation dialogs for all trades
   - Accept/Decline mechanism for each action

3. **Transaction Logging**
   - All agent actions are logged
   - Audit trail for compliance
   - Real-time status updates

4. **Paper Trading Default**
   - Alpaca paper trading for testing
   - No real money at risk during development
   - Symbol mapping for demo purposes

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Test
```bash
# Run the test script
python test_system.py
```

## 📈 Sample Data

The platform includes sample data for testing:
- Historical water futures prices (CSV format)
- Drought severity maps for California regions
- Mock government subsidy programs
- Example trading transactions

### Upload Historical Data
```csv
date,contract_code,open,high,low,close,volume
2024-01-01,NQH25,495.50,498.00,494.00,497.25,1234
2024-01-02,NQH25,497.25,502.00,496.50,501.00,1567
```

## 🚢 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Google Cloud Run
```bash
# Configure GCP
gcloud auth login
gcloud config set project water-futures-ai

# Deploy
./deploy.sh
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```
DEBUG=True
PORT=8000
DATABASE_URL=postgresql://user:pass@localhost/water_futures
ANTHROPIC_API_KEY=sk-ant-...
ALPACA_API_KEY=PK...
ALPACA_SECRET_KEY=...
CROSSMINT_API_KEY=...
VERTEX_AI_ENDPOINT=...
```

#### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_ANTHROPIC_API_KEY=sk-ant-...
```

## 📚 Technology Stack

### Frontend
- React 18 with TypeScript
- Material-UI for components
- Vite for build tooling
- Recharts for data visualization
- Axios for API calls

### Backend
- FastAPI for REST API
- SQLAlchemy for ORM
- AsyncPG for database
- Pydantic for validation
- Anthropic SDK for Claude

### AI/ML
- Claude (Anthropic) for conversational AI
- Vertex AI for price predictions
- pgvector for embeddings
- Scikit-learn for data processing

### Infrastructure
- Docker for containerization
- Google Cloud Platform
- PostgreSQL database
- GitHub Actions for CI/CD

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Anthropic for Claude AI
- Alpaca for trading APIs
- Crossmint for payment processing
- Google Cloud for Vertex AI
- The MCP/Smithery community

## 📞 Support

For support, please:
- Open an issue on GitHub
- Contact the development team
- Check the [Documentation](DEVELOPMENT.md)

## 🎯 Roadmap

- [ ] Real water futures contracts integration
- [ ] Advanced ML models for price prediction
- [ ] Mobile application
- [ ] Multi-region support
- [ ] Advanced portfolio optimization
- [ ] Automated trading strategies
- [ ] Integration with IoT sensors
- [ ] Blockchain-based smart contracts

---

Built with ❤️ for farmers facing water scarcity challenges
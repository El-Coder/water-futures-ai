# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Water Futures AI is an intelligent agricultural risk management platform that combines AI-powered futures trading, automated government subsidy processing, and predictive analytics for water scarcity management.

## Development Commands

### Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run simplified backend (recommended for development)
python main_simple.py

# Run full backend with all services
python main.py

# Run tests
pytest
pytest tests/test_unit_services.py -m unit
pytest tests/test_integration_api.py -m integration

# Type checking with pyright
pyright
```

### Frontend
```bash
cd frontend
npm install
npm run dev       # Start development server on http://localhost:5173
npm run build     # Build production bundle
npm run lint      # Run ESLint
npm run preview   # Preview production build
```

### Quick Start All Services
```bash
./dev-start.sh    # Starts backend, frontend, and MCP servers
```

### Testing
```bash
./run-tests.sh all        # Run all tests
./run-tests.sh unit       # Unit tests only
./run-tests.sh integration # Integration tests only
./run-tests.sh e2e        # End-to-end tests only
./run-tests.sh smoke      # Quick smoke tests

# Python specific tests
cd backend && pytest
python test_vertex_integration.py  # Test Vertex AI integration
```

### Deployment
```bash
./deploy.sh [project-id]  # Deploy to Google Cloud Run
cd frontend && ./deploy.sh # Deploy frontend to Firebase
```

## Architecture

### Core Stack
- **Frontend**: React 18 + TypeScript + Vite + Material-UI
  - Located in `/frontend/src`
  - Pages in `/frontend/src/pages`: Dashboard, Trading, Forecast, News, Account, DataUpload
  - Components in `/frontend/src/components`: Chatbot, ChatbotV2, Layout
  - API client in `/frontend/src/services/api.ts`

- **Backend**: FastAPI with async support
  - Main entry: `/backend/main.py` (full) or `/backend/main_simple.py` (simplified)
  - API routes in `/backend/api/routes/`
  - Services in `/backend/services/`
  - Models in `/backend/models/`

- **MCP Servers**: Node.js-based Model Context Protocol servers
  - Trading agent: `/mcp-servers/trading-agent/index.js`
  - Farmer assistant: `/mcp-servers/farmer-assistant/index.js`
  - HTTP wrapper: `/mcp-servers/http-wrapper.js`
  - Chat wrapper: `/mcp-servers/chat-wrapper.js`

### Key Services

**AI/ML Services**:
- `services/farmer_agent.py`: Claude-powered chat agent with dual-mode operation (chat/agent)
- `services/vertex_ai_service.py`: Vertex AI integration for predictions
- `services/forecast_service.py`: Price forecasting with drought conditions
- `services/ml_service.py`: Machine learning models for predictions
- `services/sentiment_service.py`: News sentiment analysis

**Trading & Financial**:
- `services/alpaca_service.py`: Alpaca API integration for paper trading
- `services/trading_service.py`: Trade execution and portfolio management
- `services/crossmint_service.py`: Government subsidy processing via Crossmint
- `services/water_futures_service.py`: Water futures contract management

**MCP Integration**:
- `services/mcp_connector.py`: MCP server connection management
- `services/mcp_bridge.py`: Bridge between FastAPI and MCP servers
- `services/alpaca_mcp_client.py`: MCP client for Alpaca trading

### API Endpoints

Core endpoints are defined in `/backend/api/routes/`:
- `/api/v1/chat`: Safe chat mode (no execution)
- `/api/v1/agent/execute`: Agent mode with execution capability
- `/api/v1/water-futures/*`: Water futures prices and contracts
- `/api/v1/forecasts/*`: Price predictions
- `/api/v1/trading/*`: Trading operations
- `/api/v1/news/*`: Water-related news
- `/api/v1/embeddings/*`: Drought data and embeddings

### Dual-Mode Chat System

The platform features a safety-first chat system:
1. **Chat Mode**: Information only, no real transactions
2. **Agent Mode**: Requires explicit enablement, can execute trades with approval

Trade approval flow is implemented with visual warnings and confirmation dialogs for each action.

## Environment Configuration

### Backend (.env)
```
DEBUG=True
PORT=8000
ANTHROPIC_API_KEY=sk-ant-...
ALPACA_API_KEY=PK...
ALPACA_SECRET_KEY=...
CROSSMINT_API_KEY=...
VERTEX_ENDPOINT_NAME=...
DATABASE_URL=postgresql://...
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_MCP_URL=http://localhost:8080
VITE_ANTHROPIC_API_KEY=sk-ant-...
```

## Testing Strategy

Tests are organized with pytest markers:
- `unit`: Unit tests for individual components
- `integration`: Integration tests for API endpoints
- `e2e`: End-to-end tests for complete user flows
- `requires_services`: Tests requiring all services running

Test configuration in `pytest.ini` includes coverage reporting and async support.

## Key Dependencies

**Backend**:
- FastAPI 0.115.5 with uvicorn
- Anthropic SDK 0.34.0 for Claude AI
- Alpaca-py 0.35.0 for trading
- Google Cloud AI Platform 1.38.0
- SQLAlchemy 2.0.36 with asyncpg

**Frontend**:
- React 19.1.1 with TypeScript 5.8.3
- Material-UI 7.3.1 for components
- Recharts 3.1.2 for data visualization
- Axios 1.11.0 for API calls
- Vite 4.5.0 for build tooling

## Security Considerations

- Paper trading mode by default (Alpaca sandbox)
- Explicit agent mode enablement required for real transactions
- Trade approval system with accept/decline mechanism
- All agent actions are logged for audit trail
- Never commit API keys or secrets to the repository

## Current Development Status

Active work includes:
- `backend/services/forecast_service_updated.py`: Enhanced forecast service
- `backend/test_vertex_integration.py`: Vertex AI integration testing
- Recent fixes for frontend Account page API endpoints and Grid component
- Trading signals and performance metrics additions
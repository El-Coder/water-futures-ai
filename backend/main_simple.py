from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import datetime
from services.data_store import data_store
from services.vertex_ai_service import vertex_ai_service
from services.mcp_connector import mcp_connector
from services.farmer_agent import farmer_agent
import os
import asyncio

app = FastAPI(
    title="Water Futures AI API",
    description="Simplified API for water futures hackathon",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple Pydantic models
class ForecastRequest(BaseModel):
    contract_code: str
    horizon_days: int = 7

class OrderRequest(BaseModel):
    contract_code: str
    side: str  # BUY or SELL
    quantity: int

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = {}

@app.get("/")
async def root():
    return {"message": "Water Futures AI API", "version": "1.0.0"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload historical water futures CSV data"""
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process the CSV
        result = data_store.upload_csv(temp_path, "historical")
        
        # Clean up temp file
        os.remove(temp_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/water-futures/history")
async def get_historical_data(
    contract_code: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get historical water futures data"""
    df = data_store.get_historical_prices(contract_code, start_date, end_date)
    return df.to_dict(orient="records")

@app.get("/api/v1/water-futures/current")
async def get_current_prices():
    """Get current/recent water futures prices"""
    # For hackathon, return mock data or last historical prices
    prices = data_store.get_current_prices()
    if not prices and data_store.historical_prices is not None:
        # Return last few historical prices as "current"
        df = data_store.historical_prices.tail(5)
        prices = df.to_dict(orient="records")
    return prices

@app.post("/api/v1/forecasts/predict")
async def generate_forecast(request: ForecastRequest):
    """Generate forecast using Vertex AI or fallback to simple model"""
    df = data_store.get_historical_prices(request.contract_code)
    
    # Prepare features for Vertex AI
    features = {
        "contract_code": request.contract_code,
        "horizon_days": request.horizon_days,
        "drought_severity": 4,  # Would come from real drought data
        "precipitation": 35,  # mm, would come from weather data
        "region": "Central Valley",
    }
    
    # Add historical prices if available
    if not df.empty and 'close' in df.columns:
        features["current_price"] = float(df['close'].iloc[-1])
        features["historical_prices"] = df['close'].tail(30).tolist()
    else:
        features["current_price"] = 500.0
        features["historical_prices"] = []
    
    # Get prediction from Vertex AI
    prediction = await vertex_ai_service.predict(features)
    
    return {
        "contract_code": request.contract_code,
        "current_price": features["current_price"],
        "predicted_prices": prediction["predicted_prices"],
        "model_confidence": prediction["model_confidence"],
        "confidence_intervals": prediction.get("confidence", {}),
        "factors": prediction["factors"]
    }

@app.get("/api/v1/news/latest")
async def get_latest_news(limit: int = 20):
    """Get latest water-related news"""
    news = data_store.get_news(limit)
    if not news:
        # Return mock news for demo
        return [
            {
                "title": "California Drought Conditions Worsen in Central Valley",
                "source": "Water News Daily",
                "url": "https://example.com/news1",
                "published_at": datetime.now().isoformat(),
                "relevance_score": 0.95,
                "sentiment_score": -0.3,
                "summary": "Drought conditions continue to impact agricultural regions..."
            },
            {
                "title": "New Water Conservation Measures Announced",
                "source": "CA Water Board",
                "url": "https://example.com/news2",
                "published_at": datetime.now().isoformat(),
                "relevance_score": 0.88,
                "sentiment_score": 0.1,
                "summary": "State announces new conservation targets for 2025..."
            }
        ]
    return news

@app.post("/api/v1/trading/order")
async def place_order(request: OrderRequest):
    """Place a mock trading order"""
    # For hackathon demo - just return success
    return {
        "order_id": f"ORD-{datetime.now().timestamp():.0f}",
        "status": "pending",
        "message": f"Order to {request.side} {request.quantity} contracts of {request.contract_code} placed successfully"
    }

@app.get("/api/v1/embeddings/drought-map")
async def get_drought_map():
    """Get drought severity data for California regions"""
    # Mock data for visualization
    return {
        "regions": [
            {"name": "Central Valley", "lat": 36.7468, "lng": -119.7726, "severity": 4},
            {"name": "Imperial Valley", "lat": 32.8475, "lng": -115.5694, "severity": 5},
            {"name": "Sacramento Valley", "lat": 39.3633, "lng": -121.9686, "severity": 3},
            {"name": "San Joaquin Valley", "lat": 36.6062, "lng": -120.1890, "severity": 4},
            {"name": "Coastal", "lat": 34.0522, "lng": -118.2437, "severity": 2}
        ],
        "updated_at": datetime.now().isoformat()
    }

@app.post("/api/v1/chat")
async def chat_with_assistant(request: ChatRequest):
    """Chat endpoint - safe mode, no real transactions"""
    try:
        # Use Farmer Agent for intelligent responses
        result = await farmer_agent.process_request(
            message=request.message,
            mode="chat",
            context=request.context or {}
        )
        return result
        
    except Exception as e:
        return {
            "response": "I'm here to help with water futures and farming. What would you like to know?",
            "suggestedActions": [],
            "error": str(e)
        }

@app.post("/api/v1/agent/execute")
async def agent_execute(request: ChatRequest):
    """Agent endpoint - can execute real transactions with Alpaca"""
    try:
        # Verify agent mode is enabled
        if not request.context.get("agentModeEnabled"):
            return {
                "response": "Agent mode is not enabled. Please enable it to execute transactions.",
                "error": "Agent mode required"
            }
        
        # Process with Farmer Agent in agent mode
        result = await farmer_agent.process_request(
            message=request.message,
            mode="agent",
            context=request.context
        )
        return result
        
    except Exception as e:
        return {
            "response": "Agent action failed. Please try again.",
            "error": str(e)
        }

@app.post("/api/v1/agent/action")
async def execute_agent_action(request: dict):
    """Execute a specific agent action (trade or subsidy)"""
    try:
        action = request.get("action", {})
        context = request.get("context", {})
        
        if action.get("type") == "trade":
            # Execute trade
            result = await mcp_connector._execute_trade_action(
                message=f"Execute trade: {action}",
                intent={
                    "primary": "TRADE_EXECUTE",
                    "action": action.get("action", "BUY"),
                    "quantity": action.get("contracts", 5),
                    "contract_code": "NQH25"
                },
                context=context
            )
        elif action.get("type") == "subsidy":
            # Process subsidy
            result = await mcp_connector._execute_subsidy_action(
                message=f"Process subsidy: {action}",
                intent={"primary": "SUBSIDY_CLAIM"},
                context=context
            )
        else:
            result = {"error": "Unknown action type"}
        
        return result
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
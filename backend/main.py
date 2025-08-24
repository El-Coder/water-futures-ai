from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import pandas as pd
import os
from datetime import datetime

# Import routes
from api.routes import water_futures, forecasts, trading, news, embeddings, mcp, crossmint_direct

# Import services
from config.settings import settings
from services.database import init_db
from services.data_store import data_store
from services.vertex_ai_service import vertex_ai_service
from services.mcp_connector import mcp_connector
from services.farmer_agent import farmer_agent

# Pydantic models for requests
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

class WeatherRequest(BaseModel):
    zip_code: str
    farmer_id: Optional[str] = None

class FarmerLocationUpdate(BaseModel):
    farmer_id: str
    zip_code: str
    city: Optional[str] = None
    county: Optional[str] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database not required for core functionality
    # await init_db()
    yield
    
app = FastAPI(
    title="Water Futures AI API",
    description="Comprehensive API for water futures trading, forecasting, AI agents, and analysis",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(water_futures.router, prefix="/api/v1/water-futures", tags=["Water Futures"])
app.include_router(forecasts.router, prefix="/api/v1/forecasts", tags=["Forecasts"])
app.include_router(trading.router, prefix="/api/v1/trading", tags=["Trading"])
app.include_router(news.router, prefix="/api/v1/news", tags=["News"])
app.include_router(embeddings.router, prefix="/api/v1/embeddings", tags=["Embeddings"])
app.include_router(mcp.router, prefix="/api/mcp", tags=["MCP"])
app.include_router(crossmint_direct.router, prefix="/api/v1/crossmint", tags=["Crossmint Direct"])

@app.get("/")
async def root():
    return {"message": "Water Futures AI API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "database": "connected",
            "farmer_agent": "ready",
            "mcp_connector": "ready",
            "vertex_ai": "ready"
        }
    }

# Chat and Agent endpoints
@app.post("/api/v1/chat")
async def chat_with_assistant(request: ChatRequest):
    """Chat endpoint - safe mode, no real transactions"""
    try:
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
        if not request.context.get("agentModeEnabled"):
            return {
                "response": "Agent mode is not enabled. Please enable it to execute transactions.",
                "error": "Agent mode required"
            }
        
        result = await farmer_agent.process_request(
            message=request.message,
            mode="agent",
            context=request.context or {}
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
            # Get the actual values from the action object
            result = await mcp_connector._execute_trade_action(
                message=f"Execute trade: {action.get('action', '')}",
                intent={
                    "primary": "TRADE_EXECUTE",
                    "action": action.get("side", "BUY"),  # Get side from action
                    "quantity": action.get("quantity", action.get("contracts", 1)),  # Get actual quantity
                    "contract_code": action.get("symbol", "NQH25")
                },
                context=context
            )
        elif action.get("type") == "subsidy":
            result = await mcp_connector._execute_subsidy_action(
                message=f"Process subsidy: {action.get('action', '')}",
                intent={
                    "primary": "SUBSIDY_CLAIM",
                    "subsidy_type": action.get("subsidy_type", "drought_relief"),
                    "amount": action.get("amount", 15000)
                },
                context=context
            )
        else:
            result = {"error": f"Unknown action type: {action.get('type')}"}
        
        return result
    except Exception as e:
        # Log the error for debugging
        print(f"Error in execute_agent_action: {e}")
        import traceback
        traceback.print_exc()
        
        # Return HTTP 500 with proper error response
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "message": "Failed to execute action",
                "executed": False
            }
        )

# Weather endpoints
@app.post("/api/v1/weather/get")
async def get_weather(request: WeatherRequest):
    """Get weather data for a specific zip code"""
    try:
        result = await farmer_agent._get_weather_data({
            "zip_code": request.zip_code,
            "farmer_id": request.farmer_id
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/weather/current/{zip_code}")
async def get_current_weather(zip_code: str):
    """Get current weather for a zip code"""
    try:
        result = await farmer_agent._get_weather_data({
            "zip_code": zip_code
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Farmer profile endpoints
@app.post("/api/v1/farmer/update-location")
async def update_farmer_location(request: FarmerLocationUpdate):
    """Update farmer's location with zip code"""
    try:
        result = await farmer_agent._update_farmer_location({
            "farmer_id": request.farmer_id,
            "location": {
                "zip_code": request.zip_code,
                "city": request.city,
                "county": request.county,
                "state": "CA"
            }
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Data upload endpoint
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload historical water futures CSV data"""
    try:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        result = data_store.upload_csv(temp_path, "historical")
        os.remove(temp_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
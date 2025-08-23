from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from api.controllers.forecast_controller import ForecastController
from pydantic import BaseModel

router = APIRouter()
controller = ForecastController()

class ForecastRequest(BaseModel):
    contract_code: str
    horizon_days: int = 7
    include_embeddings: bool = True
    include_news_sentiment: bool = True

class ForecastResponse(BaseModel):
    contract_code: str
    current_price: float
    predicted_prices: List[dict]
    confidence_intervals: dict
    model_confidence: float
    factors: dict

@router.post("/predict", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest):
    try:
        return await controller.generate_forecast(
            contract_code=request.contract_code,
            horizon_days=request.horizon_days,
            include_embeddings=request.include_embeddings,
            include_news_sentiment=request.include_news_sentiment
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals")
async def get_trading_signals():
    try:
        return await controller.get_active_signals()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/{contract_code}")
async def get_model_performance(contract_code: str):
    try:
        return await controller.get_model_performance(contract_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backtest")
async def run_backtest(
    contract_code: str,
    start_date: datetime,
    end_date: datetime
):
    try:
        return await controller.run_backtest(contract_code, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
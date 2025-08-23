from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timedelta
from api.controllers.water_futures_controller import WaterFuturesController
from pydantic import BaseModel

router = APIRouter()
controller = WaterFuturesController()

class WaterFutureResponse(BaseModel):
    contract_code: str
    price: float
    volume: int
    change: float
    change_percent: float
    timestamp: datetime

class PriceHistoryQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    interval: Optional[str] = "daily"

@router.get("/current", response_model=List[WaterFutureResponse])
async def get_current_prices():
    try:
        return await controller.get_current_prices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/index")
async def get_water_index():
    try:
        return await controller.get_nasdaq_water_index()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{contract_code}")
async def get_price_history(
    contract_code: str,
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None),
    interval: str = Query(default="daily")
):
    try:
        return await controller.get_historical_prices(
            contract_code, start_date, end_date, interval
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contracts")
async def list_contracts():
    try:
        return await controller.list_available_contracts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
async def refresh_data():
    try:
        return await controller.refresh_market_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
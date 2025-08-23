from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from api.controllers.news_controller import NewsController
from pydantic import BaseModel

router = APIRouter()
controller = NewsController()

class NewsResponse(BaseModel):
    title: str
    source: str
    url: str
    published_at: datetime
    relevance_score: float
    sentiment_score: float
    summary: str

@router.get("/latest", response_model=List[NewsResponse])
async def get_latest_news(
    limit: int = Query(default=20, le=100),
    california_only: bool = Query(default=True)
):
    try:
        return await controller.get_latest_news(limit, california_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_news(
    query: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(default=20, le=100)
):
    try:
        return await controller.search_news(query, start_date, end_date, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights")
async def get_market_insights():
    try:
        return await controller.get_market_insights()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def get_water_events(active_only: bool = Query(default=True)):
    try:
        return await controller.get_water_events(active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment/aggregate")
async def get_aggregate_sentiment(days: int = Query(default=7)):
    try:
        return await controller.get_aggregate_sentiment(days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
async def refresh_news():
    try:
        return await controller.refresh_news_feed()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
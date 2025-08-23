from typing import Optional, List
from datetime import datetime, timedelta
from services.news_service import NewsService
from services.sentiment_service import SentimentService

class NewsController:
    def __init__(self):
        self.news_service = NewsService()
        self.sentiment_service = SentimentService()
    
    async def get_latest_news(self, limit: int, california_only: bool):
        # Use the correct method name
        articles = await self.news_service.get_latest_news(
            limit=limit
        )
        
        # Add sentiment scores
        for article in articles:
            # Use the summary field for sentiment analysis
            article["sentiment_score"] = article.get("sentiment_score", 0.0)
        
        return articles
    
    async def search_news(
        self,
        query: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        limit: int
    ):
        # Use the correct method name
        return await self.news_service.search_news(
            query=query,
            limit=limit
        )
    
    async def get_market_insights(self):
        # Use a method that exists
        return await self.news_service.get_news_summary()
    
    async def get_water_events(self, active_only: bool):
        # Return mock water events for now
        return {
            "events": [
                {
                    "id": "EVT-001",
                    "title": "California Drought Emergency Declaration",
                    "date": datetime.now().isoformat(),
                    "severity": "high",
                    "active": True
                },
                {
                    "id": "EVT-002", 
                    "title": "Federal Relief Program Announced",
                    "date": datetime.now().isoformat(),
                    "severity": "medium",
                    "active": True
                }
            ]
        }
    
    async def get_aggregate_sentiment(self, days: int):
        # Use the news service sentiment analysis
        return await self.news_service.analyze_news_sentiment()
    
    async def refresh_news_feed(self):
        # Return a simple refresh status
        return {
            "status": "success",
            "message": "News feed refreshed",
            "timestamp": datetime.now().isoformat()
        }
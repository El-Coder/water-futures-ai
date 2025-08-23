from typing import Optional, List
from datetime import datetime, timedelta
from services.news_service import NewsService
from services.sentiment_service import SentimentService

class NewsController:
    def __init__(self):
        self.news_service = NewsService()
        self.sentiment_service = SentimentService()
    
    async def get_latest_news(self, limit: int, california_only: bool):
        articles = await self.news_service.fetch_latest_articles(
            limit=limit,
            california_only=california_only
        )
        
        for article in articles:
            article["sentiment_score"] = await self.sentiment_service.analyze(
                article["content"]
            )
        
        return articles
    
    async def search_news(
        self,
        query: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        limit: int
    ):
        return await self.news_service.search_articles(
            query=query,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    async def get_market_insights(self):
        return await self.news_service.generate_insights()
    
    async def get_water_events(self, active_only: bool):
        return await self.news_service.get_water_events(active_only)
    
    async def get_aggregate_sentiment(self, days: int):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return await self.sentiment_service.get_aggregate_sentiment(
            start_date,
            end_date
        )
    
    async def refresh_news_feed(self):
        return await self.news_service.refresh_feed()
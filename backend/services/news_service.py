"""
News Service - Handles news aggregation and analysis for water-related topics
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random

class NewsService:
    """Service for managing water-related news and updates"""
    
    def __init__(self):
        self.news_cache = []
        self.sources = [
            "Water News Daily",
            "California Water Board",
            "USDA Reports",
            "Reuters Agriculture",
            "Bloomberg Commodities",
            "CME Group News"
        ]
        self._generate_mock_news()
    
    def _generate_mock_news(self):
        """Generate mock news for demonstration"""
        news_templates = [
            {
                "title": "California Drought Conditions Worsen in Central Valley",
                "summary": "Drought conditions continue to impact agricultural regions, with severity reaching level 4 out of 5.",
                "sentiment": -0.3,
                "relevance": 0.95
            },
            {
                "title": "New Water Conservation Measures Announced",
                "summary": "State announces new conservation targets for 2025, requiring 15% reduction in water usage.",
                "sentiment": 0.1,
                "relevance": 0.88
            },
            {
                "title": "Water Futures Trading Volume Reaches Record High",
                "summary": "Trading volume in water futures contracts surpasses $500M as farmers hedge against drought risk.",
                "sentiment": 0.2,
                "relevance": 0.92
            },
            {
                "title": "Federal Drought Relief Program Expanded",
                "summary": "USDA announces $2B expansion of drought relief subsidies for affected farmers.",
                "sentiment": 0.5,
                "relevance": 0.90
            },
            {
                "title": "Groundwater Levels Hit Historic Lows",
                "summary": "Central Valley aquifers show concerning depletion rates, raising alarm for future water security.",
                "sentiment": -0.4,
                "relevance": 0.87
            },
            {
                "title": "Innovative Irrigation Technology Shows Promise",
                "summary": "New drip irrigation systems reduce water usage by 30% while maintaining crop yields.",
                "sentiment": 0.6,
                "relevance": 0.75
            }
        ]
        
        # Generate news items with timestamps
        for i, template in enumerate(news_templates):
            self.news_cache.append({
                "id": f"NEWS-{i+1:03d}",
                "title": template["title"],
                "summary": template["summary"],
                "source": random.choice(self.sources),
                "url": f"https://example.com/news/{i+1}",
                "published_at": (datetime.now() - timedelta(hours=i*4)).isoformat(),
                "relevance_score": template["relevance"],
                "sentiment_score": template["sentiment"],
                "categories": self._get_categories(template["title"]),
                "entities": self._extract_entities(template["summary"])
            })
    
    def _get_categories(self, title: str) -> List[str]:
        """Categorize news based on title"""
        categories = []
        title_lower = title.lower()
        
        if "drought" in title_lower:
            categories.append("drought")
        if "conservation" in title_lower or "water" in title_lower:
            categories.append("water-management")
        if "trading" in title_lower or "futures" in title_lower:
            categories.append("markets")
        if "federal" in title_lower or "usda" in title_lower:
            categories.append("government")
        if "technology" in title_lower or "irrigation" in title_lower:
            categories.append("technology")
        
        return categories if categories else ["general"]
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from news text"""
        entities = []
        
        # Simple entity extraction (in production, use NLP)
        if "California" in text or "Central Valley" in text:
            entities.append("California")
        if "USDA" in text:
            entities.append("USDA")
        if "drought" in text.lower():
            entities.append("Drought")
        if "farmers" in text.lower():
            entities.append("Farmers")
        
        return entities
    
    async def get_latest_news(
        self, 
        limit: int = 20,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get latest news articles
        """
        try:
            # Ensure news_cache is a list
            if not isinstance(self.news_cache, list):
                return []
                
            news = self.news_cache.copy()
            
            # Filter by category if specified
            if category:
                news = [n for n in news if category in n.get("categories", [])]
            
            # Sort by published date (newest first)
            news.sort(key=lambda x: x["published_at"], reverse=True)
            
            return news[:limit]
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    async def get_news_by_sentiment(
        self, 
        sentiment: str = "positive",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get news filtered by sentiment
        """
        if sentiment == "positive":
            filtered = [n for n in self.news_cache if n["sentiment_score"] > 0.2]
        elif sentiment == "negative":
            filtered = [n for n in self.news_cache if n["sentiment_score"] < -0.2]
        else:  # neutral
            filtered = [n for n in self.news_cache if -0.2 <= n["sentiment_score"] <= 0.2]
        
        filtered.sort(key=lambda x: abs(x["sentiment_score"]), reverse=True)
        return filtered[:limit]
    
    async def get_market_impact_news(self) -> List[Dict[str, Any]]:
        """
        Get news that might impact water futures markets
        """
        # Filter for high relevance market-related news
        market_news = [
            n for n in self.news_cache 
            if n["relevance_score"] > 0.8 and 
            ("markets" in n.get("categories", []) or 
             "drought" in n.get("categories", []))
        ]
        
        return market_news
    
    async def analyze_news_sentiment(self) -> Dict[str, Any]:
        """
        Analyze overall news sentiment
        """
        if not self.news_cache:
            return {
                "overall_sentiment": 0,
                "interpretation": "No news available",
                "confidence": 0
            }
        
        sentiments = [n["sentiment_score"] for n in self.news_cache]
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        if avg_sentiment > 0.3:
            interpretation = "Very Positive"
        elif avg_sentiment > 0.1:
            interpretation = "Positive"
        elif avg_sentiment > -0.1:
            interpretation = "Neutral"
        elif avg_sentiment > -0.3:
            interpretation = "Negative"
        else:
            interpretation = "Very Negative"
        
        return {
            "overall_sentiment": avg_sentiment,
            "interpretation": interpretation,
            "positive_count": sum(1 for s in sentiments if s > 0.2),
            "neutral_count": sum(1 for s in sentiments if -0.2 <= s <= 0.2),
            "negative_count": sum(1 for s in sentiments if s < -0.2),
            "total_articles": len(sentiments),
            "confidence": 0.75
        }
    
    async def get_news_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current news situation
        """
        sentiment_analysis = await self.analyze_news_sentiment()
        latest_news = await self.get_latest_news(limit=5)
        market_impact = await self.get_market_impact_news()
        
        return {
            "summary": {
                "headline": "Current water market conditions show mixed signals",
                "key_points": [
                    "Drought conditions remain severe in Central Valley",
                    "Government expanding relief programs",
                    "Trading volume increasing as farmers hedge risks"
                ],
                "market_impact": "Moderate to High",
                "recommendation": "Consider hedging positions due to drought severity"
            },
            "sentiment": sentiment_analysis,
            "latest_headlines": [n["title"] for n in latest_news],
            "high_impact_count": len(market_impact),
            "last_updated": datetime.now().isoformat()
        }
    
    async def search_news(
        self, 
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search news by keyword
        """
        query_lower = query.lower()
        results = []
        
        for news_item in self.news_cache:
            # Simple keyword search (in production, use full-text search)
            if (query_lower in news_item["title"].lower() or 
                query_lower in news_item["summary"].lower()):
                results.append(news_item)
        
        return results[:limit]
    
    async def add_news_alert(
        self,
        keywords: List[str],
        farmer_id: str
    ) -> Dict[str, Any]:
        """
        Add news alert for specific keywords
        """
        # In production, this would be stored in database
        return {
            "alert_id": f"ALERT-{datetime.now().timestamp():.0f}",
            "farmer_id": farmer_id,
            "keywords": keywords,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "message": f"Alert created for keywords: {', '.join(keywords)}"
        }
    
    async def fetch_latest_articles(
        self,
        limit: int = 20,
        california_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch latest articles (alias for get_latest_news)
        """
        return await self.get_latest_news(limit=limit)
    
    async def generate_insights(self) -> Dict[str, Any]:
        """
        Generate market insights (alias for get_news_summary)
        """
        return await self.get_news_summary()
    
    async def get_water_events(
        self,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get water-related events
        """
        events = [
            {
                "id": "EVT-001",
                "title": "California Drought Emergency",
                "description": "Statewide drought emergency declared",
                "severity": 4,
                "active": True,
                "start_date": datetime.now().isoformat(),
                "affected_regions": ["Central Valley", "Southern California"]
            },
            {
                "id": "EVT-002",
                "title": "Federal Relief Program",
                "description": "$2B drought relief program announced",
                "severity": 2,
                "active": True,
                "start_date": datetime.now().isoformat(),
                "affected_regions": ["All California"]
            }
        ]
        
        if active_only:
            return [e for e in events if e["active"]]
        return events
    
    async def refresh_feed(self) -> Dict[str, Any]:
        """
        Refresh the news feed
        """
        # In production, this would fetch new articles
        self._generate_mock_news()
        return {
            "status": "success",
            "articles_updated": len(self.news_cache),
            "timestamp": datetime.now().isoformat()
        }

# Singleton instance
news_service = NewsService()
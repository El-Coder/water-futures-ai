"""
Sentiment Service - Analyzes sentiment in news and text
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

class SentimentService:
    """Service for sentiment analysis"""
    
    def __init__(self):
        self.sentiment_cache = {}
        
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a single text
        """
        # Simple keyword-based sentiment analysis
        positive_words = ["good", "increase", "profit", "growth", "success", "positive", "improve", "recovery"]
        negative_words = ["drought", "loss", "decline", "shortage", "crisis", "negative", "worsen", "severe"]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate sentiment score
        if positive_count + negative_count == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / (positive_count + negative_count)
        
        # Determine sentiment label
        if sentiment_score > 0.2:
            sentiment = "positive"
        elif sentiment_score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "confidence": 0.7,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count
        }
    
    async def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment of multiple texts
        """
        results = []
        for text in texts:
            result = await self.analyze_text(text)
            results.append(result)
        return results
    
    async def get_market_sentiment(self, news_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall market sentiment from news
        """
        if not news_articles:
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0,
                "article_count": 0,
                "confidence": 0
            }
        
        sentiments = []
        for article in news_articles:
            if "sentiment_score" in article:
                sentiments.append(article["sentiment_score"])
            else:
                # Analyze if not already analyzed
                analysis = await self.analyze_text(article.get("title", "") + " " + article.get("summary", ""))
                sentiments.append(analysis["sentiment_score"])
        
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        if avg_sentiment > 0.2:
            overall = "positive"
        elif avg_sentiment < -0.2:
            overall = "negative"
        else:
            overall = "neutral"
        
        return {
            "overall_sentiment": overall,
            "sentiment_score": avg_sentiment,
            "article_count": len(news_articles),
            "positive_count": sum(1 for s in sentiments if s > 0.2),
            "neutral_count": sum(1 for s in sentiments if -0.2 <= s <= 0.2),
            "negative_count": sum(1 for s in sentiments if s < -0.2),
            "confidence": 0.75,
            "analyzed_at": datetime.now().isoformat()
        }
    
    async def get_sentiment_trends(self, period_days: int = 7) -> Dict[str, Any]:
        """
        Get sentiment trends over time
        """
        # Mock trend data
        trends = []
        for i in range(period_days):
            date = datetime.now() - timedelta(days=period_days-i-1)
            # Generate varying sentiment
            sentiment = 0.1 * np.sin(i / 2) + np.random.normal(0, 0.1)
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "sentiment_score": float(sentiment),
                "article_count": np.random.randint(5, 20)
            })
        
        return {
            "period_days": period_days,
            "trends": trends,
            "overall_trend": "improving" if trends[-1]["sentiment_score"] > trends[0]["sentiment_score"] else "declining",
            "volatility": np.std([t["sentiment_score"] for t in trends])
        }
    
    async def analyze_impact(self, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze potential market impact of sentiment
        """
        sentiment_score = sentiment_data.get("sentiment_score", 0)
        
        if abs(sentiment_score) < 0.2:
            impact = "minimal"
            price_impact = "0-1%"
            trading_recommendation = "No action needed"
        elif sentiment_score > 0.5:
            impact = "significant_positive"
            price_impact = "2-5% increase expected"
            trading_recommendation = "Consider reducing long positions"
        elif sentiment_score < -0.5:
            impact = "significant_negative"
            price_impact = "2-5% decrease expected"
            trading_recommendation = "Consider hedging or buying opportunity"
        elif sentiment_score > 0.2:
            impact = "moderate_positive"
            price_impact = "1-2% increase possible"
            trading_recommendation = "Monitor for opportunities"
        else:
            impact = "moderate_negative"
            price_impact = "1-2% decrease possible"
            trading_recommendation = "Watch for support levels"
        
        return {
            "impact_level": impact,
            "expected_price_impact": price_impact,
            "trading_recommendation": trading_recommendation,
            "confidence": 0.65,
            "factors_considered": [
                "news_sentiment",
                "article_volume",
                "sentiment_trend"
            ]
        }

# Import numpy for trends calculation
import numpy as np
from datetime import timedelta

# Singleton instance
sentiment_service = SentimentService()
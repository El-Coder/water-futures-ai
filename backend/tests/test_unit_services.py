"""
Unit Tests for Water Futures AI Backend Services
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.water_futures_service import WaterFuturesService
from services.news_service import NewsService
from services.forecast_service import ForecastService
from services.trading_service import TradingService
from services.farmer_agent import FarmerAgent


class TestWaterFuturesService:
    """Unit tests for Water Futures Service"""
    
    @pytest.fixture
    def service(self):
        return WaterFuturesService()
    
    @pytest.mark.asyncio
    async def test_get_current_prices(self, service):
        """Test fetching current water futures prices"""
        prices = await service.get_current_prices()
        
        assert isinstance(prices, list)
        assert len(prices) > 0
        
        # Check structure of price data
        for price in prices:
            assert 'contract_code' in price
            assert 'price' in price
            assert 'volume' in price
            assert 'timestamp' in price
            assert price['price'] > 0
    
    @pytest.mark.asyncio
    async def test_get_nasdaq_water_index(self, service):
        """Test fetching NASDAQ water index"""
        index = await service.get_nasdaq_water_index()
        
        assert 'index_value' in index
        assert 'change_percent' in index
        assert 'timestamp' in index
        assert index['index_value'] > 0
    
    @pytest.mark.asyncio
    async def test_calculate_drought_impact(self, service):
        """Test drought impact calculation"""
        impact = await service.calculate_drought_impact(
            severity=4,
            location="Central Valley"
        )
        
        assert 'price_impact' in impact
        assert 'recommendation' in impact
        assert impact['severity'] == 4
        assert 0 <= impact['price_impact'] <= 100


class TestNewsService:
    """Unit tests for News Service"""
    
    @pytest.fixture
    def service(self):
        return NewsService()
    
    @pytest.mark.asyncio
    async def test_get_latest_news(self, service):
        """Test fetching latest news articles"""
        news = await service.get_latest_news(limit=5)
        
        assert isinstance(news, list)
        assert len(news) <= 5
        
        for article in news:
            assert 'title' in article
            assert 'summary' in article
            assert 'sentiment_score' in article
            assert -1 <= article['sentiment_score'] <= 1
    
    @pytest.mark.asyncio
    async def test_analyze_news_sentiment(self, service):
        """Test news sentiment analysis"""
        sentiment = await service.analyze_news_sentiment()
        
        assert 'overall_sentiment' in sentiment
        assert 'interpretation' in sentiment
        assert 'confidence' in sentiment
        assert -1 <= sentiment['overall_sentiment'] <= 1
    
    @pytest.mark.asyncio
    async def test_search_news(self, service):
        """Test news search functionality"""
        results = await service.search_news("drought", limit=3)
        
        assert isinstance(results, list)
        assert len(results) <= 3
        
        # Verify search results contain the keyword
        for article in results:
            assert 'drought' in article['title'].lower() or 'drought' in article['summary'].lower()


class TestForecastService:
    """Unit tests for Forecast Service"""
    
    @pytest.fixture
    def service(self):
        return ForecastService()
    
    @pytest.mark.asyncio
    async def test_predict_prices(self, service):
        """Test price prediction"""
        prediction = await service.predict(
            contract_code="NQH25",
            horizon_days=7
        )
        
        assert 'current_price' in prediction
        assert 'predicted_prices' in prediction
        assert 'confidence' in prediction
        assert len(prediction['predicted_prices']) == 7
        assert 0 <= prediction['confidence'] <= 1
    
    @pytest.mark.asyncio
    async def test_calculate_risk_metrics(self, service):
        """Test risk metrics calculation"""
        metrics = await service.calculate_risk_metrics(
            contract_code="NQH25"
        )
        
        assert 'volatility' in metrics
        assert 'var_95' in metrics  # Value at Risk
        assert 'sharpe_ratio' in metrics
        assert metrics['volatility'] >= 0


class TestTradingService:
    """Unit tests for Trading Service"""
    
    @pytest.fixture
    def service(self):
        return TradingService()
    
    @pytest.mark.asyncio
    async def test_validate_order(self, service):
        """Test order validation"""
        # Valid order
        valid_order = {
            'symbol': 'NQH25',
            'quantity': 5,
            'side': 'BUY',
            'order_type': 'MARKET'
        }
        
        is_valid, message = await service.validate_order(valid_order)
        assert is_valid == True
        
        # Invalid order (negative quantity)
        invalid_order = {
            'symbol': 'NQH25',
            'quantity': -5,
            'side': 'BUY',
            'order_type': 'MARKET'
        }
        
        is_valid, message = await service.validate_order(invalid_order)
        assert is_valid == False
        assert 'quantity' in message.lower()
    
    @pytest.mark.asyncio
    async def test_calculate_order_cost(self, service):
        """Test order cost calculation"""
        cost = await service.calculate_order_cost(
            symbol='NQH25',
            quantity=10,
            side='BUY'
        )
        
        assert 'subtotal' in cost
        assert 'commission' in cost
        assert 'total' in cost
        assert cost['total'] > 0
        assert cost['commission'] >= 0
    
    @pytest.mark.asyncio
    async def test_get_portfolio_summary(self, service):
        """Test portfolio summary generation"""
        summary = await service.get_portfolio_summary()
        
        assert 'total_value' in summary
        assert 'positions' in summary
        assert 'cash_balance' in summary
        assert 'daily_pnl' in summary
        assert isinstance(summary['positions'], list)


class TestFarmerAgent:
    """Unit tests for Farmer Agent"""
    
    @pytest.fixture
    def agent(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            return FarmerAgent()
    
    @pytest.mark.asyncio
    async def test_analyze_intent_trade(self, agent):
        """Test intent analysis for trade requests"""
        with patch.object(agent, 'anthropic') as mock_anthropic:
            mock_anthropic.messages.create.return_value = Mock(
                content=[Mock(text="Trade intent detected")]
            )
            
            intent = await agent._analyze_intent_with_tools(
                "Buy 10 water futures contracts",
                {}
            )
            
            assert intent['primary_intent'] == 'TRADE'
            assert 'trade_water_futures' in intent['tools_needed']
            assert intent['parameters']['side'] == 'BUY'
            assert intent['parameters']['quantity'] == 10
    
    @pytest.mark.asyncio
    async def test_analyze_intent_subsidy(self, agent):
        """Test intent analysis for subsidy requests"""
        with patch.object(agent, 'anthropic') as mock_anthropic:
            mock_anthropic.messages.create.return_value = Mock(
                content=[Mock(text="Subsidy intent detected")]
            )
            
            intent = await agent._analyze_intent_with_tools(
                "Apply for drought relief subsidy",
                {}
            )
            
            assert intent['primary_intent'] == 'SUBSIDY'
            assert 'process_subsidy' in intent['tools_needed']
    
    @pytest.mark.asyncio
    async def test_get_weather_data(self, agent):
        """Test weather data retrieval"""
        weather = await agent._get_weather_data({
            'zip_code': '93277'
        })
        
        assert weather['success'] == True
        assert 'weather' in weather
        assert 'temperature' in weather['weather']
        assert 'drought_index' in weather['weather']
        assert 'forecast' in weather['weather']


def run_unit_tests():
    """Run all unit tests"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_unit_tests()
"""
Integration Tests for Water Futures AI API Endpoints
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    async def async_client(self):
        """Create async test client"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    # ==================== Health & Status Tests ====================
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "services" in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Water Futures" in data["message"]
    
    # ==================== Water Futures Tests ====================
    
    def test_get_current_prices(self, client):
        """Test fetching current water futures prices"""
        response = client.get("/api/v1/water-futures/current")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Validate data structure
        for item in data:
            assert "contract_code" in item
            assert "price" in item
            assert "volume" in item
            assert item["price"] > 0
    
    def test_get_nasdaq_index(self, client):
        """Test fetching NASDAQ water index"""
        response = client.get("/api/v1/water-futures/nasdaq-index")
        
        assert response.status_code == 200
        data = response.json()
        assert "index_value" in data
        assert "change_percent" in data
        assert data["index_value"] > 0
    
    def test_get_historical_prices(self, client):
        """Test fetching historical prices"""
        response = client.get(
            "/api/v1/water-futures/history",
            params={
                "contract_code": "NQH25",
                "interval": "daily"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    # ==================== News Tests ====================
    
    def test_get_latest_news(self, client):
        """Test fetching latest news"""
        response = client.get("/api/v1/news/latest?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
        
        for article in data:
            assert "title" in article
            assert "sentiment_score" in article
    
    def test_search_news(self, client):
        """Test news search"""
        response = client.get(
            "/api/v1/news/search",
            params={"query": "drought"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_market_insights(self, client):
        """Test market insights endpoint"""
        response = client.get("/api/v1/news/insights")
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "sentiment" in data
    
    # ==================== Forecast Tests ====================
    
    def test_generate_forecast(self, client):
        """Test price forecast generation"""
        response = client.post(
            "/api/v1/forecasts/predict",
            json={
                "contract_code": "NQH25",
                "horizon_days": 7
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "current_price" in data
        assert "predicted_prices" in data
        assert "model_confidence" in data
        assert len(data["predicted_prices"]) == 7
    
    def test_analyze_market(self, client):
        """Test market analysis"""
        response = client.post("/api/v1/forecasts/analyze-market")
        
        assert response.status_code == 200
        data = response.json()
        assert "market_condition" in data
        assert "drought_impact" in data
        assert "recommendation" in data
    
    # ==================== Trading Tests ====================
    
    def test_validate_order(self, client):
        """Test order validation"""
        response = client.post(
            "/api/v1/trading/validate",
            json={
                "contract_code": "NQH25",
                "side": "BUY",
                "quantity": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        assert "estimated_cost" in data
    
    def test_place_order(self, client):
        """Test order placement"""
        response = client.post(
            "/api/v1/trading/order",
            json={
                "contract_code": "NQH25",
                "side": "BUY",
                "quantity": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "order_id" in data
        assert "status" in data
    
    def test_get_portfolio(self, client):
        """Test portfolio retrieval"""
        response = client.get("/api/v1/trading/portfolio")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_value" in data
        assert "positions" in data
        assert "cash_balance" in data
    
    # ==================== Chat & Agent Tests ====================
    
    def test_chat_endpoint(self, client):
        """Test chat endpoint"""
        response = client.post(
            "/api/v1/chat",
            json={
                "message": "What are current water prices?",
                "context": {}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "mode" in data
        assert data["mode"] == "chat"
    
    def test_agent_execute_without_mode(self, client):
        """Test agent execute without agent mode enabled"""
        response = client.post(
            "/api/v1/agent/execute",
            json={
                "message": "Buy 5 water futures",
                "context": {"agentModeEnabled": False}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data or "Agent mode" in data["response"]
    
    def test_agent_execute_with_mode(self, client):
        """Test agent execute with agent mode enabled"""
        response = client.post(
            "/api/v1/agent/execute",
            json={
                "message": "Analyze market conditions",
                "context": {"agentModeEnabled": True}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data.get("mode") == "agent"
    
    # ==================== Weather Tests ====================
    
    def test_get_weather(self, client):
        """Test weather data retrieval"""
        response = client.post(
            "/api/v1/weather/get",
            json={"zip_code": "93277"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "weather" in data
        assert "temperature" in data["weather"]
        assert "drought_index" in data["weather"]
    
    def test_get_current_weather(self, client):
        """Test current weather endpoint"""
        response = client.get("/api/v1/weather/current/93277")
        
        assert response.status_code == 200
        data = response.json()
        assert "weather" in data
    
    # ==================== Embeddings Tests ====================
    
    def test_get_drought_map(self, client):
        """Test drought map endpoint"""
        response = client.get("/api/v1/embeddings/drought-map")
        
        assert response.status_code == 200
        data = response.json()
        assert "regions" in data
        assert isinstance(data["regions"], list)
        
        for region in data["regions"]:
            assert "name" in region
            assert "severity" in region
    
    def test_search_documents(self, client):
        """Test document search"""
        response = client.post(
            "/api/v1/embeddings/search",
            json={"query": "drought relief programs"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)


class TestAPIErrorHandling:
    """Test API error handling"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_invalid_contract_code(self, client):
        """Test handling of invalid contract code"""
        response = client.get(
            "/api/v1/water-futures/history",
            params={
                "contract_code": "INVALID",
                "interval": "daily"
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 404]
    
    def test_invalid_order_quantity(self, client):
        """Test handling of invalid order quantity"""
        response = client.post(
            "/api/v1/trading/order",
            json={
                "contract_code": "NQH25",
                "side": "BUY",
                "quantity": -5  # Invalid negative quantity
            }
        )
        
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        response = client.post(
            "/api/v1/trading/order",
            json={"contract_code": "NQH25"}  # Missing side and quantity
        )
        
        assert response.status_code == 422
    
    def test_malformed_json(self, client):
        """Test handling of malformed JSON"""
        response = client.post(
            "/api/v1/chat",
            data="not valid json"
        )
        
        assert response.status_code == 422


class TestAPIPerformance:
    """Test API performance characteristics"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_response_time_health(self, client):
        """Test health endpoint response time"""
        import time
        
        start = time.time()
        response = client.get("/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        import concurrent.futures
        
        def make_request():
            return client.get("/api/v1/water-futures/current")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # All requests should succeed
        for response in results:
            assert response.status_code == 200
    
    def test_large_limit_handling(self, client):
        """Test handling of large limit parameters"""
        response = client.get("/api/v1/news/latest?limit=1000")
        
        assert response.status_code == 200
        data = response.json()
        # Should be capped at reasonable limit
        assert len(data) <= 100


def run_integration_tests():
    """Run all integration tests"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_integration_tests()
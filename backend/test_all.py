#!/usr/bin/env python3
"""
Comprehensive Test Suite for Water Futures AI
Tests: Unit, Component, and Integration
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List
from datetime import datetime
import sys

# Test configuration
BACKEND_URL = "http://localhost:8000"
MCP_URL = "http://localhost:8080"

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def add_pass(self):
        self.passed += 1
        print(f"{GREEN}✓{RESET}", end="")
        
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"{RED}✗{RESET}", end="")
        
    def print_summary(self):
        print(f"\n\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}TEST RESULTS SUMMARY{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        
        if self.errors:
            print(f"\n{RED}Errors:{RESET}")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.failed == 0:
            print(f"\n{GREEN}🎉 ALL TESTS PASSED!{RESET}")
        else:
            print(f"\n{RED}❌ SOME TESTS FAILED{RESET}")
            sys.exit(1)

async def test_backend_health(client: httpx.AsyncClient, results: TestResults):
    """Test backend health endpoint"""
    try:
        response = await client.get(f"{BACKEND_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        results.add_pass()
    except Exception as e:
        results.add_fail("Backend Health", str(e))

async def test_mcp_health(client: httpx.AsyncClient, results: TestResults):
    """Test MCP wrapper health endpoint"""
    try:
        response = await client.get(f"{MCP_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        results.add_pass()
    except Exception as e:
        results.add_fail("MCP Health", str(e))

# ============================
# Unit Tests
# ============================

async def run_unit_tests(client: httpx.AsyncClient, results: TestResults):
    """Run unit tests for individual components"""
    print(f"\n{YELLOW}Running Unit Tests...{RESET}")
    
    # Test water futures endpoints
    tests = [
        ("GET /api/v1/water-futures/contracts", f"{BACKEND_URL}/api/v1/water-futures/contracts"),
        ("GET /api/v1/water-futures/nasdaq-index", f"{BACKEND_URL}/api/v1/water-futures/nasdaq-index"),
        ("GET /api/v1/news/latest", f"{BACKEND_URL}/api/v1/news/latest"),
        ("GET /api/v1/embeddings/regions", f"{BACKEND_URL}/api/v1/embeddings/regions"),
    ]
    
    for test_name, url in tests:
        try:
            response = await client.get(url)
            assert response.status_code == 200
            results.add_pass()
        except Exception as e:
            results.add_fail(test_name, str(e))

# ============================
# Component Tests
# ============================

async def run_component_tests(client: httpx.AsyncClient, results: TestResults):
    """Run component tests for service interactions"""
    print(f"\n{YELLOW}Running Component Tests...{RESET}")
    
    # Test forecast generation
    try:
        response = await client.post(
            f"{BACKEND_URL}/api/v1/forecasts/predict",
            json={
                "contract_code": "NQH25",
                "horizon_days": 7,
                "include_embeddings": True,
                "include_news_sentiment": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "predicted_prices" in data
        results.add_pass()
    except Exception as e:
        results.add_fail("Forecast Generation", str(e))
    
    # Test trading signals
    try:
        response = await client.get(f"{BACKEND_URL}/api/v1/forecasts/signals")
        assert response.status_code == 200
        results.add_pass()
    except Exception as e:
        results.add_fail("Trading Signals", str(e))
    
    # Test chat endpoint
    try:
        response = await client.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={
                "message": "What's the current water price?",
                "context": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        results.add_pass()
    except Exception as e:
        results.add_fail("Chat Endpoint", str(e))
    
    # Test weather endpoint
    try:
        response = await client.get(f"{BACKEND_URL}/api/v1/weather/current/95014")
        assert response.status_code == 200
        results.add_pass()
    except Exception as e:
        results.add_fail("Weather Data", str(e))

# ============================
# Integration Tests
# ============================

async def run_integration_tests(client: httpx.AsyncClient, results: TestResults):
    """Run integration tests for end-to-end workflows"""
    print(f"\n{YELLOW}Running Integration Tests...{RESET}")
    
    # Test MCP trading flow
    try:
        # Step 1: Request trade via MCP
        response = await client.post(
            f"{MCP_URL}/api/mcp/trading/place-trade",
            json={
                "contractCode": "NQH25",
                "side": "BUY",
                "quantity": 10,
                "userId": "test_user"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "orderId" in data
        order_id = data["orderId"]
        results.add_pass()
        
        # Step 2: Confirm trade
        response = await client.post(
            f"{MCP_URL}/api/mcp/trading/confirm-trade",
            json={
                "orderId": order_id,
                "approved": True
            }
        )
        assert response.status_code == 200
        results.add_pass()
    except Exception as e:
        results.add_fail("MCP Trading Flow", str(e))
    
    # Test portfolio analysis
    try:
        response = await client.get(f"{MCP_URL}/api/mcp/portfolio/analysis")
        assert response.status_code == 200
        data = response.json()
        assert "totalValue" in data
        results.add_pass()
    except Exception as e:
        results.add_fail("Portfolio Analysis", str(e))
    
    # Test market sentiment
    try:
        response = await client.get(f"{MCP_URL}/api/mcp/market/sentiment")
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
        results.add_pass()
    except Exception as e:
        results.add_fail("Market Sentiment", str(e))
    
    # Test subsidy check
    try:
        response = await client.post(
            f"{MCP_URL}/api/mcp/subsidies/check",
            json={
                "farmerId": "test_farmer",
                "zipCode": "95014"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "eligible" in data
        results.add_pass()
    except Exception as e:
        results.add_fail("Subsidy Check", str(e))
    
    # Test agent action execution
    try:
        response = await client.post(
            f"{BACKEND_URL}/api/v1/agent/action",
            json={
                "action": {
                    "type": "trade",
                    "action": "BUY",
                    "contracts": 5
                },
                "context": {
                    "agentModeEnabled": True,
                    "userId": "test_user"
                }
            }
        )
        assert response.status_code == 200
        results.add_pass()
    except Exception as e:
        results.add_fail("Agent Action", str(e))

# ============================
# Performance Tests
# ============================

async def run_performance_tests(client: httpx.AsyncClient, results: TestResults):
    """Run basic performance tests"""
    print(f"\n{YELLOW}Running Performance Tests...{RESET}")
    
    import time
    
    # Test response time for critical endpoints
    endpoints = [
        f"{BACKEND_URL}/api/v1/water-futures/contracts",
        f"{MCP_URL}/health",
    ]
    
    for endpoint in endpoints:
        try:
            start = time.time()
            response = await client.get(endpoint)
            elapsed = time.time() - start
            
            assert response.status_code == 200
            assert elapsed < 2.0  # Should respond within 2 seconds
            results.add_pass()
        except Exception as e:
            results.add_fail(f"Performance {endpoint}", str(e))

# ============================
# Main Test Runner
# ============================

async def main():
    """Main test runner"""
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Water Futures AI - Comprehensive Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = TestResults()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check services are running
        print(f"\n{YELLOW}Checking services...{RESET}")
        await test_backend_health(client, results)
        await test_mcp_health(client, results)
        
        # Run test suites
        await run_unit_tests(client, results)
        await run_component_tests(client, results)
        await run_integration_tests(client, results)
        await run_performance_tests(client, results)
    
    # Print results
    results.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
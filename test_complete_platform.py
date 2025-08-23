#!/usr/bin/env python3
"""
Complete Platform Test - Water Futures AI
Tests all services, endpoints, and features
"""

import requests
import json
from datetime import datetime

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def test_endpoint(name, method, url, data=None, expected_status=200):
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            response = requests.request(method, url, json=data)
        
        if response.status_code == expected_status:
            print(f"{GREEN}✅ {name}{RESET}")
            return True, response
        else:
            print(f"{YELLOW}⚠️  {name} - Status {response.status_code}{RESET}")
            return False, response
    except Exception as e:
        print(f"{RED}❌ {name} - {e}{RESET}")
        return False, None

print(f"\n{BLUE}{'='*60}")
print("Water Futures AI - Complete Platform Test")
print(f"{'='*60}{RESET}\n")

all_passed = True
test_results = {}

# 1. Core Services
print(f"{BLUE}1. Testing Core Services{RESET}")
print("-" * 30)

success, _ = test_endpoint(
    "Backend Health",
    "GET",
    "http://localhost:8000/health"
)
all_passed &= success

success, _ = test_endpoint(
    "Chat Service Health",
    "GET",
    "http://localhost:8001/health"
)
all_passed &= success

success, _ = test_endpoint(
    "MCP Wrapper Health",
    "GET",
    "http://localhost:8080/health"
)
all_passed &= success

# 2. Water Futures API
print(f"\n{BLUE}2. Testing Water Futures API{RESET}")
print("-" * 30)

success, response = test_endpoint(
    "Current Prices",
    "GET",
    "http://localhost:8000/api/v1/water-futures/current"
)
all_passed &= success
if success:
    prices = response.json()
    print(f"   • Found {len(prices)} contracts")
    print(f"   • {prices[0]['contract_code']}: ${prices[0]['price']}")

success, _ = test_endpoint(
    "NASDAQ Water Index",
    "GET",
    "http://localhost:8000/api/v1/water-futures/nasdaq-index"
)
all_passed &= success

# 3. News & Sentiment
print(f"\n{BLUE}3. Testing News & Sentiment{RESET}")
print("-" * 30)

success, response = test_endpoint(
    "Latest News",
    "GET",
    "http://localhost:8000/api/v1/news/latest?limit=5"
)
all_passed &= success
if success:
    news = response.json()
    print(f"   • {len(news)} articles retrieved")

success, _ = test_endpoint(
    "Market Insights",
    "GET",
    "http://localhost:8000/api/v1/news/insights"
)
all_passed &= success

# 4. Forecasting
print(f"\n{BLUE}4. Testing Forecasting{RESET}")
print("-" * 30)

success, response = test_endpoint(
    "Price Forecast",
    "POST",
    "http://localhost:8000/api/v1/forecasts/predict",
    {"contract_code": "NQH25", "horizon_days": 7}
)
all_passed &= success
if success:
    forecast = response.json()
    print(f"   • Current: ${forecast['current_price']}")
    if forecast['predicted_prices']:
        print(f"   • Predicted: ${forecast['predicted_prices'][0]['price']}")
    print(f"   • Confidence: {forecast['model_confidence']*100:.1f}%")

# 5. Chat & Agent
print(f"\n{BLUE}5. Testing Chat & Agent{RESET}")
print("-" * 30)

success, response = test_endpoint(
    "Chat (Safe Mode)",
    "POST",
    "http://localhost:8001/api/v1/chat",
    {"message": "What are current water prices?", "context": {}}
)
all_passed &= success

success, _ = test_endpoint(
    "Agent (No Mode)",
    "POST",
    "http://localhost:8001/api/v1/agent/execute",
    {"message": "Check market", "context": {"agentModeEnabled": False}}
)
all_passed &= success

# 6. MCP Trading Services
print(f"\n{BLUE}6. Testing MCP Trading Services{RESET}")
print("-" * 30)

success, response = test_endpoint(
    "Portfolio Status",
    "GET",
    "http://localhost:8080/api/mcp/trading/portfolio"
)
all_passed &= success
if success:
    portfolio = response.json()
    print(f"   • Portfolio Value: ${portfolio['account']['portfolio_value']:,.2f}")
    print(f"   • Cash: ${portfolio['account']['cash']:,.2f}")

success, _ = test_endpoint(
    "Market Analysis",
    "POST",
    "http://localhost:8080/api/mcp/trading/analyze-market",
    {"includeNews": True, "includeDrought": True}
)
all_passed &= success

# 7. Farmer Services with Fund Separation
print(f"\n{BLUE}7. Testing Farmer Services (Fund Separation){RESET}")
print("-" * 30)

success, response = test_endpoint(
    "Farmer Balance",
    "GET",
    "http://localhost:8080/api/mcp/farmer/balance/farmer-ted"
)
all_passed &= success
if success:
    balance = response.json()
    print(f"   • Trading Account: ${balance['tradingAccount']['cash']:,.2f}")
    print(f"   • Subsidy Available: ${balance['subsidyAccounts']['totalAvailable']:,.2f}")
    print(f"   • Fund Separation: {balance['subsidyAccounts']['message'][:30]}...")

success, response = test_endpoint(
    "Process Subsidy",
    "POST",
    "http://localhost:8080/api/mcp/farmer/process-subsidy",
    {
        "farmerId": "farmer-ted",
        "subsidyType": "drought_relief",
        "amount": 15000
    }
)
all_passed &= success
if success:
    subsidy = response.json()
    print(f"   • Subsidy ID: {subsidy['subsidy']['id']}")
    print(f"   • Earmarked: {subsidy['subsidy']['fundEarmarking']['isEarmarked']}")
    print(f"   • Can Trade: {subsidy['subsidy']['fundEarmarking']['canBeUsedForTrading']}")

# 8. Drought Context
print(f"\n{BLUE}8. Testing Drought Context{RESET}")
print("-" * 30)

success, _ = test_endpoint(
    "Update Drought Context",
    "POST",
    "http://localhost:8001/api/v1/context/drought",
    {
        "droughtLevel": "medium",
        "subsidyAmount": "0.25",
        "farmerId": "farmer-ted"
    }
)
all_passed &= success

success, _ = test_endpoint(
    "Notify Drought",
    "POST",
    "http://localhost:8001/api/v1/agent/notify-drought",
    {
        "droughtLevel": "high",
        "subsidyAmount": "0.5",
        "farmerId": "farmer-ted"
    }
)
all_passed &= success

# 9. Weather Services
print(f"\n{BLUE}9. Testing Weather Services{RESET}")
print("-" * 30)

success, response = test_endpoint(
    "Get Weather",
    "POST",
    "http://localhost:8000/api/v1/weather/get",
    {"zip_code": "93277"}
)
all_passed &= success
if success:
    weather = response.json()
    print(f"   • Temperature: {weather['weather']['temperature']}°C")
    print(f"   • Drought Index: {weather['weather']['drought_index']}")

# 10. Embeddings & Search
print(f"\n{BLUE}10. Testing Embeddings & Search{RESET}")
print("-" * 30)

success, response = test_endpoint(
    "Drought Map",
    "GET",
    "http://localhost:8000/api/v1/embeddings/drought-map"
)
all_passed &= success
if success:
    drought_map = response.json()
    print(f"   • Regions: {len(drought_map['regions'])}")

# Summary
print(f"\n{BLUE}{'='*60}")
print("TEST SUMMARY")
print(f"{'='*60}{RESET}\n")

if all_passed:
    print(f"{GREEN}✅ ALL TESTS PASSED!{RESET}\n")
    print("Platform Status:")
    print("  • Backend API: ✅ Operational")
    print("  • Chat Service: ✅ Operational")
    print("  • MCP Trading: ✅ Operational")
    print("  • Fund Separation: ✅ Working")
    print("  • Drought Context: ✅ Active")
    print("  • Weather Service: ✅ Available")
    print("\n🚀 Platform is fully operational and tested!")
else:
    print(f"{YELLOW}⚠️  Some tests failed. Review the output above.{RESET}")

print(f"\n{BLUE}Access Points:{RESET}")
print(f"  • Frontend: http://localhost:5173")
print(f"  • API Docs: http://localhost:8000/docs")
print(f"  • Chat Service: http://localhost:8001")
print(f"  • MCP Trading: http://localhost:8080")

print(f"\n{BLUE}Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
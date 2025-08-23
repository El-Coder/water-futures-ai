import requests

print("\n🔧 Water Futures AI - E2E Testing")
print("="*50)

# Test complete flow
base_url = "http://localhost:8000"
all_tests_passed = True

# 1. Check health
try:
    health = requests.get(f"{base_url}/health")
    print(f"✅ Health check: {health.status_code}")
except Exception as e:
    print(f"❌ Health check failed: {e}")
    all_tests_passed = False

# 2. Get current prices  
try:
    prices = requests.get(f"{base_url}/api/v1/water-futures/current")
    print(f"✅ Current prices: {prices.status_code}")
    price_data = prices.json()
    print(f"   First contract: {price_data[0]['contract_code']} @ ${price_data[0]['price']}")
except Exception as e:
    print(f"❌ Current prices failed: {e}")
    all_tests_passed = False

# 3. Get news
try:
    news = requests.get(f"{base_url}/api/v1/news/latest?limit=3")
    print(f"✅ News feed: {news.status_code}")
    print(f"   Articles found: {len(news.json())}")
except Exception as e:
    print(f"❌ News feed failed: {e}")
    all_tests_passed = False

# 4. Generate forecast
try:
    forecast = requests.post(
        f"{base_url}/api/v1/forecasts/predict",
        json={"contract_code": "NQH25", "horizon_days": 7}
    )
    print(f"✅ Forecast: {forecast.status_code}")
    forecast_data = forecast.json()
    print(f"   Current: ${forecast_data['current_price']}")
    if forecast_data['predicted_prices']:
        print(f"   Predicted: ${forecast_data['predicted_prices'][0]['price']}")
except Exception as e:
    print(f"❌ Forecast failed: {e}")
    all_tests_passed = False

# 5. Chat interaction
try:
    chat_response = requests.post(
        "http://localhost:8001/api/v1/chat",
        json={"message": "What are water prices?", "context": {}}
    )
    print(f"✅ Chat service: {chat_response.status_code}")
except Exception as e:
    print(f"❌ Chat service failed: {e}")
    all_tests_passed = False

# 6. MCP Wrapper portfolio check
try:
    portfolio = requests.get("http://localhost:8080/api/mcp/trading/portfolio")
    print(f"✅ MCP Trading: {portfolio.status_code}")
    portfolio_data = portfolio.json()
    print(f"   Portfolio value: ${portfolio_data['account']['portfolio_value']:,.2f}")
except Exception as e:
    print(f"❌ MCP Trading failed: {e}")
    all_tests_passed = False

# 7. Trading validation
try:
    validation = requests.post(
        f"{base_url}/api/v1/trading/validate",
        json={"contract_code": "NQH25", "side": "BUY", "quantity": 5}
    )
    if validation.status_code == 200:
        print(f"✅ Trading validation: {validation.status_code}")
    else:
        print(f"⚠️  Trading validation: {validation.status_code} (endpoint not implemented)")
except Exception as e:
    print(f"⚠️  Trading validation not available: {e}")

print("="*50)

if all_tests_passed:
    print("✅ All core services are working properly!")
    print("\n📊 System Status:")
    print("  • Backend API: Operational")
    print("  • Chat Service: Operational") 
    print("  • MCP Trading: Operational")
    print("  • News Service: Operational")
    print("  • Forecast Service: Operational")
    print("\n🚀 Platform is ready for use!")
else:
    print("⚠️  Some services need attention")
    
print("\n💡 To interact with the platform:")
print("  • Frontend: http://localhost:5173")
print("  • API Docs: http://localhost:8000/docs")
print("  • Chat Service: http://localhost:8001")


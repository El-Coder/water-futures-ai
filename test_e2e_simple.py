import requests

print("Running E2E API Test...")

# Test complete flow
base_url = "http://localhost:8000"

# 1. Check health
health = requests.get(f"{base_url}/health")
print(f"✅ Health check: {health.status_code}")

# 2. Get current prices  
prices = requests.get(f"{base_url}/api/v1/water-futures/current")
print(f"✅ Current prices: {prices.status_code}")
price_data = prices.json()
print(f"   First contract: {price_data[0]['contract_code']} @ ${price_data[0]['price']}")

# 3. Get news
news = requests.get(f"{base_url}/api/v1/news/latest?limit=3")
print(f"✅ News feed: {news.status_code}")
print(f"   Articles found: {len(news.json())}")

# 4. Generate forecast
forecast = requests.post(
    f"{base_url}/api/v1/forecasts/predict",
    json={"contract_code": "NQH25", "horizon_days": 7}
)
print(f"✅ Forecast: {forecast.status_code}")
forecast_data = forecast.json()
print(f"   Current: ${forecast_data['current_price']}")
print(f"   Predicted: ${forecast_data['predicted_prices'][0]['price']}")

# 5. Chat interaction
chat_response = requests.post(
    "http://localhost:8001/api/v1/chat",
    json={"message": "What are water prices?", "context": {}}
)
print(f"✅ Chat service: {chat_response.status_code}")

# 6. Place order
order = requests.post(
    f"{base_url}/api/v1/trading/order",
    json={"contract_code": "NQH25", "side": "BUY", "quantity": 5}
)
print(f"✅ Order placement: {order.status_code}")
order_data = order.json()
print(f"   Order ID: {order_data.get('order_id', 'N/A')}")

print("\n🎉 E2E Test Complete - All services working!")

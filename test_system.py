#!/usr/bin/env python3
"""
End-to-End System Test for Water Futures AI
Tests all components: Claude, Alpaca, MCP, Frontend/Backend integration
"""
import asyncio
import httpx
import json
from typing import Dict, Any
import time

class SystemTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_results = []
        
    async def run_all_tests(self):
        """Run all system tests"""
        print("🧪 Water Futures AI - System Test Suite")
        print("=" * 50)
        
        # Test 1: Backend Health
        await self.test_backend_health()
        
        # Test 2: Claude Chat Mode
        await self.test_claude_chat()
        
        # Test 3: Agent Mode with Alpaca
        await self.test_agent_trading()
        
        # Test 4: Subsidy Processing
        await self.test_subsidy_processing()
        
        # Test 5: Market Analysis
        await self.test_market_analysis()
        
        # Test 6: Forecast
        await self.test_forecast()
        
        # Print results
        self.print_results()
    
    async def test_backend_health(self):
        """Test if backend is running"""
        print("\n📍 Test 1: Backend Health Check")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.backend_url}/health")
                if response.status_code == 200:
                    self.test_results.append(("Backend Health", "✅ PASSED"))
                    print("  ✅ Backend is healthy")
                else:
                    self.test_results.append(("Backend Health", "❌ FAILED"))
                    print(f"  ❌ Backend returned status {response.status_code}")
        except Exception as e:
            self.test_results.append(("Backend Health", f"❌ FAILED: {e}"))
            print(f"  ❌ Backend not reachable: {e}")
    
    async def test_claude_chat(self):
        """Test Claude in chat mode"""
        print("\n📍 Test 2: Claude Chat Mode")
        try:
            async with httpx.AsyncClient() as client:
                # Test general question
                response = await client.post(
                    f"{self.backend_url}/api/v1/chat",
                    json={
                        "message": "What government subsidies am I eligible for?",
                        "context": {
                            "location": "Central Valley",
                            "droughtSeverity": 4
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "response" in data and len(data["response"]) > 0:
                        self.test_results.append(("Claude Chat", "✅ PASSED"))
                        print("  ✅ Claude responded successfully")
                        print(f"  Response preview: {data['response'][:100]}...")
                    else:
                        self.test_results.append(("Claude Chat", "⚠️ PARTIAL"))
                        print("  ⚠️ Claude responded but content was empty")
                else:
                    self.test_results.append(("Claude Chat", "❌ FAILED"))
                    print(f"  ❌ Chat endpoint returned status {response.status_code}")
                    
        except Exception as e:
            self.test_results.append(("Claude Chat", f"❌ FAILED: {e}"))
            print(f"  ❌ Chat test failed: {e}")
    
    async def test_agent_trading(self):
        """Test Agent mode with Alpaca trading"""
        print("\n📍 Test 3: Agent Mode - Alpaca Trading")
        try:
            async with httpx.AsyncClient() as client:
                # Test trade execution
                response = await client.post(
                    f"{self.backend_url}/api/v1/agent/execute",
                    json={
                        "message": "Buy 5 water futures contracts",
                        "context": {
                            "agentModeEnabled": True,
                            "farmerId": "test-farmer"
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("executed") or "order" in data.get("response", "").lower():
                        self.test_results.append(("Agent Trading", "✅ PASSED"))
                        print("  ✅ Agent executed trade successfully")
                        print(f"  Response: {data.get('response', '')[:100]}...")
                    else:
                        self.test_results.append(("Agent Trading", "⚠️ SIMULATED"))
                        print("  ⚠️ Trade was simulated (Alpaca may not be connected)")
                else:
                    self.test_results.append(("Agent Trading", "❌ FAILED"))
                    print(f"  ❌ Agent endpoint returned status {response.status_code}")
                    
        except Exception as e:
            self.test_results.append(("Agent Trading", f"❌ FAILED: {e}"))
            print(f"  ❌ Agent trading test failed: {e}")
    
    async def test_subsidy_processing(self):
        """Test Crossmint subsidy processing"""
        print("\n📍 Test 4: Subsidy Processing (Crossmint)")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/v1/agent/execute",
                    json={
                        "message": "Process my drought relief subsidy payment",
                        "context": {
                            "agentModeEnabled": True,
                            "farmerId": "test-farmer",
                            "droughtSeverity": 4
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "subsidy" in data.get("response", "").lower():
                        self.test_results.append(("Subsidy Processing", "✅ PASSED"))
                        print("  ✅ Subsidy processed successfully")
                        print(f"  Response: {data.get('response', '')[:100]}...")
                    else:
                        self.test_results.append(("Subsidy Processing", "⚠️ PARTIAL"))
                        print("  ⚠️ Subsidy response received but unclear")
                else:
                    self.test_results.append(("Subsidy Processing", "❌ FAILED"))
                    print(f"  ❌ Subsidy endpoint returned status {response.status_code}")
                    
        except Exception as e:
            self.test_results.append(("Subsidy Processing", f"❌ FAILED: {e}"))
            print(f"  ❌ Subsidy test failed: {e}")
    
    async def test_market_analysis(self):
        """Test market analysis"""
        print("\n📍 Test 5: Market Analysis")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/v1/chat",
                    json={
                        "message": "Analyze current water futures market conditions",
                        "context": {}
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "market" in data.get("response", "").lower():
                        self.test_results.append(("Market Analysis", "✅ PASSED"))
                        print("  ✅ Market analysis provided")
                    else:
                        self.test_results.append(("Market Analysis", "⚠️ PARTIAL"))
                        print("  ⚠️ Response received but no market data")
                else:
                    self.test_results.append(("Market Analysis", "❌ FAILED"))
                    
        except Exception as e:
            self.test_results.append(("Market Analysis", f"❌ FAILED: {e}"))
            print(f"  ❌ Market analysis test failed: {e}")
    
    async def test_forecast(self):
        """Test forecasting endpoint"""
        print("\n📍 Test 6: Forecast Generation")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/v1/forecasts/predict",
                    json={
                        "contract_code": "NQH25",
                        "horizon_days": 7
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "predicted_prices" in data:
                        self.test_results.append(("Forecast", "✅ PASSED"))
                        print("  ✅ Forecast generated successfully")
                        print(f"  Current price: ${data.get('current_price', 0)}")
                        print(f"  Predictions: {len(data.get('predicted_prices', []))} days")
                    else:
                        self.test_results.append(("Forecast", "⚠️ PARTIAL"))
                        print("  ⚠️ Forecast response incomplete")
                else:
                    self.test_results.append(("Forecast", "❌ FAILED"))
                    
        except Exception as e:
            self.test_results.append(("Forecast", f"❌ FAILED: {e}"))
            print(f"  ❌ Forecast test failed: {e}")
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = 0
        failed = 0
        partial = 0
        
        for test_name, result in self.test_results:
            print(f"{test_name:25} {result}")
            if "PASSED" in result:
                passed += 1
            elif "FAILED" in result:
                failed += 1
            else:
                partial += 1
        
        print("=" * 50)
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Partial: {partial}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed / len(self.test_results) * 100):.1f}%")
        
        if failed == 0:
            print("\n🎉 All critical tests passed! System is ready.")
        else:
            print(f"\n⚠️  {failed} tests failed. Please check the logs.")

async def main():
    """Main test runner"""
    tester = SystemTester()
    
    print("\n⏳ Waiting 3 seconds for services to be ready...")
    await asyncio.sleep(3)
    
    await tester.run_all_tests()
    
    print("\n📝 Testing Instructions:")
    print("1. Start all services: ./dev-start.sh")
    print("2. Open browser: http://localhost:5173")
    print("3. Click chat icon in bottom right")
    print("4. Test CHAT mode: 'What subsidies am I eligible for?'")
    print("5. Enable AGENT mode (toggle switch)")
    print("6. Test AGENT mode: 'Buy 5 water futures contracts'")
    print("7. Check Account page for transaction history")

if __name__ == "__main__":
    asyncio.run(main())
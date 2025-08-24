#!/usr/bin/env python3
"""
Complete End-to-End Test for Water Futures AI Platform
Tests the full flow: Frontend → Backend → Vertex AI → MCP → Trading/Subsidies
"""

import asyncio
import httpx
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, List

# ANSI colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
MAGENTA = '\033[0;35m'
CYAN = '\033[0;36m'
NC = '\033[0m'  # No Color
BOLD = '\033[1m'

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
MCP_URL = "http://localhost:8080"
CHAT_SERVICE_URL = "http://localhost:8001"

class E2ETestSuite:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        self.session_context = {
            "location": "Central Valley",
            "farmSize": 500,
            "currentBalance": 125000,
            "droughtSeverity": 4,
            "farmer_id": "farmer-ted"
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def print_header(self, title: str):
        """Print formatted section header"""
        print(f"\n{BLUE}{'='*60}{NC}")
        print(f"{BLUE}{BOLD}{title}{NC}")
        print(f"{BLUE}{'='*60}{NC}\n")
    
    def print_test(self, name: str, passed: bool, details: str = ""):
        """Print test result"""
        status = f"{GREEN}✅ PASSED{NC}" if passed else f"{RED}❌ FAILED{NC}"
        print(f"  {name}: {status}")
        if details:
            print(f"    {CYAN}{details}{NC}")
        self.test_results.append({"name": name, "passed": passed})
    
    async def check_services(self) -> bool:
        """Check if all required services are running"""
        self.print_header("1. SERVICE HEALTH CHECK")
        all_healthy = True
        
        services = [
            ("Backend API", f"{BACKEND_URL}/health"),
            ("Chat Service", f"{CHAT_SERVICE_URL}/health"),
            ("MCP Wrapper", f"{MCP_URL}/health"),
        ]
        
        for name, url in services:
            try:
                response = await self.client.get(url)
                self.print_test(name, response.status_code == 200, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(name, False, f"Error: {e}")
                all_healthy = False
        
        # Check Vertex AI
        try:
            result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'project'],
                capture_output=True, text=True, check=True
            )
            is_vertex_ready = result.stdout.strip() == "water-futures-ai"
            self.print_test("Vertex AI", is_vertex_ready, 
                          "Project: water-futures-ai" if is_vertex_ready else "Not configured")
        except:
            self.print_test("Vertex AI", False, "gcloud not available")
            all_healthy = False
        
        return all_healthy
    
    async def test_chat_mode(self) -> Dict[str, Any]:
        """Test chat mode interactions"""
        self.print_header("2. CHAT MODE (SAFE) TESTING")
        
        # Test 1: General conversation
        print(f"{YELLOW}Test 2.1: General Conversation{NC}")
        response = await self.client.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={
                "message": "Hello, tell me about water futures",
                "mode": "chat",
                "context": self.session_context
            }
        )
        
        result = response.json()
        has_response = bool(result.get("response"))
        self.print_test("General chat response", has_response,
                       f"Response length: {len(result.get('response', ''))} chars")
        
        # Test 2: Market analysis request
        print(f"\n{YELLOW}Test 2.2: Market Analysis Request{NC}")
        response = await self.client.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={
                "message": "What's the forecast for water prices given the drought?",
                "mode": "chat",
                "context": self.session_context
            }
        )
        
        result = response.json()
        mentions_drought = "drought" in result.get("response", "").lower()
        mentions_price = any(word in result.get("response", "").lower() 
                           for word in ["price", "forecast", "predict"])
        
        self.print_test("Drought context recognized", mentions_drought)
        self.print_test("Price forecast mentioned", mentions_price)
        
        # Test 3: Trade request in chat mode (should not execute)
        print(f"\n{YELLOW}Test 2.3: Trade Request (Should Not Execute){NC}")
        response = await self.client.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={
                "message": "Buy 10 NQH25 water futures contracts",
                "mode": "chat",
                "context": self.session_context
            }
        )
        
        result = response.json()
        not_executed = not result.get("executed", False)
        suggests_agent = "agent mode" in result.get("response", "").lower()
        
        self.print_test("Trade NOT executed", not_executed)
        self.print_test("Suggests Agent Mode", suggests_agent)
        
        return result
    
    async def test_vertex_ai_integration(self) -> Dict[str, Any]:
        """Test Vertex AI predictions"""
        self.print_header("3. VERTEX AI INTEGRATION")
        
        # Test direct forecast endpoint
        print(f"{YELLOW}Test 3.1: Direct Forecast API{NC}")
        response = await self.client.post(
            f"{BACKEND_URL}/api/v1/forecasts/predict",
            json={
                "contract_code": "NQH25",
                "horizon_days": 7,
                "include_confidence": True
            }
        )
        
        if response.status_code == 200:
            forecast = response.json()
            has_predictions = bool(forecast.get("predicted_prices"))
            using_vertex = forecast.get("using_vertex_ai", False)
            has_confidence = forecast.get("model_confidence", 0) > 0
            
            self.print_test("Forecast generated", has_predictions,
                          f"{len(forecast.get('predicted_prices', []))} days predicted")
            self.print_test("Using Vertex AI", using_vertex,
                          "Real model" if using_vertex else "Fallback model")
            self.print_test("Confidence score", has_confidence,
                          f"{forecast.get('model_confidence', 0)*100:.0f}%")
            
            if has_predictions:
                current = forecast.get("current_price", 0)
                future = forecast["predicted_prices"][-1]["price"]
                change = ((future - current) / current * 100) if current else 0
                print(f"\n  {CYAN}Price Prediction:{NC}")
                print(f"    Current: ${current:.2f}")
                print(f"    7-day forecast: ${future:.2f}")
                print(f"    Expected change: {change:+.1f}%")
        else:
            self.print_test("Forecast API", False, f"Status: {response.status_code}")
            forecast = {}
        
        # Test trading signals
        print(f"\n{YELLOW}Test 3.2: Trading Signals with ML{NC}")
        response = await self.client.get(f"{BACKEND_URL}/api/v1/forecasts/signals")
        
        if response.status_code == 200:
            signals = response.json()
            has_signals = signals.get("total_signals", 0) > 0
            self.print_test("Trading signals generated", has_signals,
                          f"{signals.get('total_signals', 0)} signals")
            
            if has_signals and signals.get("signals"):
                signal = signals["signals"][0]
                print(f"\n  {CYAN}Top Signal:{NC}")
                print(f"    Contract: {signal.get('contract_code')}")
                print(f"    Action: {signal.get('signal')} ({signal.get('strength')})")
                print(f"    Confidence: {signal.get('confidence')}%")
                print(f"    Model: {signal.get('model')}")
        else:
            self.print_test("Trading signals", False, f"Status: {response.status_code}")
        
        return forecast
    
    async def test_agent_mode(self) -> Dict[str, Any]:
        """Test agent mode with real execution"""
        self.print_header("4. AGENT MODE (LIVE) TESTING")
        
        # Test 1: Account check
        print(f"{YELLOW}Test 4.1: Account Information{NC}")
        response = await self.client.post(
            f"{BACKEND_URL}/api/v1/agent/execute",
            json={
                "message": "Check my account balance and positions",
                "mode": "agent",
                "context": {**self.session_context, "agentModeEnabled": True}
            }
        )
        
        result = response.json()
        has_response = bool(result.get("response"))
        executed = result.get("executed", False)
        
        self.print_test("Account check response", has_response)
        self.print_test("Tools executed", executed,
                       f"Executed: {', '.join([str(d.get('tool', 'unknown')) for d in result.get('executionDetails', [])])}")
        
        # Test 2: Price forecast with Vertex AI
        print(f"\n{YELLOW}Test 4.2: AI-Powered Price Forecast{NC}")
        response = await self.client.post(
            f"{BACKEND_URL}/api/v1/agent/execute",
            json={
                "message": "Give me a forecast for NQH25 water futures",
                "mode": "agent",
                "context": {**self.session_context, "agentModeEnabled": True}
            }
        )
        
        result = response.json()
        mentions_forecast = any(word in result.get("response", "").lower() 
                              for word in ["forecast", "predict", "expect", "likely"])
        self.print_test("Forecast in response", mentions_forecast)
        
        # Test 3: Trade execution (simulated)
        print(f"\n{YELLOW}Test 4.3: Trade Execution Flow{NC}")
        response = await self.client.post(
            f"{BACKEND_URL}/api/v1/agent/execute",
            json={
                "message": "Buy 3 NQH25 water futures contracts",
                "mode": "agent",
                "context": {**self.session_context, "agentModeEnabled": True}
            }
        )
        
        result = response.json()
        trade_mentioned = "trade" in result.get("response", "").lower() or "order" in result.get("response", "").lower()
        is_agent_action = result.get("isAgentAction", False)
        
        self.print_test("Trade response generated", trade_mentioned)
        self.print_test("Marked as agent action", is_agent_action)
        
        if result.get("executionDetails"):
            details = result["executionDetails"][0]
            print(f"\n  {CYAN}Trade Details:{NC}")
            print(f"    Success: {details.get('success', False)}")
            print(f"    Order ID: {details.get('order_id', 'N/A')}")
            print(f"    Symbol: {details.get('symbol', 'N/A')}")
            print(f"    Quantity: {details.get('quantity', 'N/A')}")
        
        return result
    
    async def test_subsidy_flow(self) -> Dict[str, Any]:
        """Test government subsidy processing"""
        self.print_header("5. SUBSIDY PROCESSING (CROSSMINT)")
        
        # Check eligibility
        print(f"{YELLOW}Test 5.1: Check Subsidy Eligibility{NC}")
        response = await self.client.get(
            f"{BACKEND_URL}/api/v1/mcp/farmer/subsidies/{self.session_context['farmer_id']}"
        )
        
        if response.status_code == 200:
            eligibility = response.json()
            is_eligible = eligibility.get("eligible", False)
            total_available = eligibility.get("total_available", 0)
            
            self.print_test("Eligibility check", is_eligible,
                          f"Amount available: ${total_available:,}")
            
            if eligibility.get("programs"):
                print(f"\n  {CYAN}Available Programs:{NC}")
                for program in eligibility["programs"]:
                    print(f"    • {program['name']}: ${program['amount']:,}")
        else:
            self.print_test("Eligibility check", False, f"Status: {response.status_code}")
            eligibility = {}
        
        # Process subsidy claim
        print(f"\n{YELLOW}Test 5.2: Process Subsidy Claim{NC}")
        response = await self.client.post(
            f"{BACKEND_URL}/api/v1/agent/execute",
            json={
                "message": "Process my drought relief subsidy",
                "mode": "agent",
                "context": {**self.session_context, "agentModeEnabled": True}
            }
        )
        
        result = response.json()
        subsidy_mentioned = "subsidy" in result.get("response", "").lower()
        self.print_test("Subsidy processing response", subsidy_mentioned)
        
        return eligibility
    
    async def test_full_conversation_flow(self):
        """Test a complete user conversation flow"""
        self.print_header("6. COMPLETE CONVERSATION FLOW")
        
        conversation = [
            ("Hello, I'm a farmer in Central Valley", "chat"),
            ("What's the current drought situation?", "chat"),
            ("Should I buy water futures to hedge my risk?", "chat"),
            ("What's the price forecast for next week?", "agent"),
            ("Buy 5 NQH25 contracts", "agent"),
            ("Can I get government assistance?", "agent"),
        ]
        
        print(f"{YELLOW}Simulating {len(conversation)}-step conversation:{NC}\n")
        
        for i, (message, mode) in enumerate(conversation, 1):
            print(f"{MAGENTA}Step {i}: [{mode.upper()}] {message}{NC}")
            
            endpoint = f"{BACKEND_URL}/api/v1/{'agent/execute' if mode == 'agent' else 'chat'}"
            response = await self.client.post(
                endpoint,
                json={
                    "message": message,
                    "mode": mode,
                    "context": {
                        **self.session_context,
                        "agentModeEnabled": mode == "agent"
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")[:150] + "..."
                print(f"  {GREEN}Response: {response_text}{NC}")
                
                if result.get("executed"):
                    print(f"  {CYAN}Executed: {result.get('actionType', 'unknown')} action{NC}")
            else:
                print(f"  {RED}Failed: Status {response.status_code}{NC}")
            
            await asyncio.sleep(1)  # Rate limiting
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = len(self.test_results)
        passed = sum(1 for t in self.test_results if t["passed"])
        failed = total - passed
        
        print(f"{GREEN}Passed: {passed}/{total}{NC}")
        print(f"{RED}Failed: {failed}/{total}{NC}")
        
        if failed > 0:
            print(f"\n{RED}Failed Tests:{NC}")
            for test in self.test_results:
                if not test["passed"]:
                    print(f"  • {test['name']}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        if success_rate == 100:
            print(f"\n{GREEN}{BOLD}🎉 ALL TESTS PASSED!{NC}")
            print(f"{GREEN}The platform is fully operational with Vertex AI integration.{NC}")
        elif success_rate >= 80:
            print(f"\n{YELLOW}⚠️ Most tests passed ({success_rate:.0f}%){NC}")
            print(f"{YELLOW}Some features may need attention.{NC}")
        else:
            print(f"\n{RED}❌ Multiple failures detected ({success_rate:.0f}% pass rate){NC}")
            print(f"{RED}Please check service configurations.{NC}")
        
        return success_rate

async def main():
    """Run the complete E2E test suite"""
    print(f"{BLUE}{BOLD}")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║     WATER FUTURES AI - END-TO-END TEST SUITE         ║")
    print("║         Testing: Frontend → Backend → AI → Trading    ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print(f"{NC}")
    
    async with E2ETestSuite() as suite:
        # Check services first
        if not await suite.check_services():
            print(f"\n{RED}Some services are not running.{NC}")
            print(f"{YELLOW}Run ./dev-start.sh to start all services.{NC}")
            return 1
        
        # Run test suites
        await suite.test_chat_mode()
        await suite.test_vertex_ai_integration()
        await suite.test_agent_mode()
        await suite.test_subsidy_flow()
        await suite.test_full_conversation_flow()
        
        # Print summary
        success_rate = suite.print_summary()
        
        return 0 if success_rate == 100 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
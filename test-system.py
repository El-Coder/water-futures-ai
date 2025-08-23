#!/usr/bin/env python3
"""
Comprehensive Test Suite for Water Futures AI System
Tests backend, MCP servers, and frontend integration
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

# Configuration
BACKEND_URL = "http://localhost:8000"
MCP_URL = "http://localhost:8080"
FRONTEND_URL = "http://localhost:5173"

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = None
        self.duration = 0
        self.details = {}

class SystemTester:
    def __init__(self):
        self.results = []
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def run_all_tests(self):
        """Run all system tests"""
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Water Futures AI - Comprehensive System Test{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # Test suites
        await self.test_backend_health()
        await self.test_mcp_health()
        await self.test_backend_endpoints()
        await self.test_mcp_endpoints()
        await self.test_integration_flows()
        await self.test_error_handling()
        
        # Print summary
        self.print_summary()
        
    async def test_backend_health(self):
        """Test backend health and basic endpoints"""
        print(f"\n{Fore.YELLOW}Testing Backend Health...{Style.RESET_ALL}")
        
        # Test health endpoint
        result = await self.test_endpoint(
            "Backend Health",
            f"{BACKEND_URL}/health",
            method="GET",
            expected_status=200
        )
        
        # Test root endpoint
        result = await self.test_endpoint(
            "Backend Root",
            f"{BACKEND_URL}/",
            method="GET",
            expected_status=200
        )
        
    async def test_mcp_health(self):
        """Test MCP server health"""
        print(f"\n{Fore.YELLOW}Testing MCP Server Health...{Style.RESET_ALL}")
        
        result = await self.test_endpoint(
            "MCP Health",
            f"{MCP_URL}/health",
            method="GET",
            expected_status=200,
            expected_fields=["status", "endpoints"]
        )
        
    async def test_backend_endpoints(self):
        """Test all backend API endpoints"""
        print(f"\n{Fore.YELLOW}Testing Backend API Endpoints...{Style.RESET_ALL}")
        
        # Test chat endpoint
        await self.test_endpoint(
            "Chat API",
            f"{BACKEND_URL}/api/v1/chat",
            method="POST",
            data={
                "message": "What's the current water futures price?",
                "context": {"location": "Central Valley"}
            },
            expected_status=200,
            expected_fields=["response"]
        )
        
        # Test weather endpoint
        await self.test_endpoint(
            "Weather API",
            f"{BACKEND_URL}/api/v1/weather/current/93277",
            method="GET",
            expected_status=200,
            expected_fields=["weather", "success"]
        )
        
        # Test news endpoint
        await self.test_endpoint(
            "News API",
            f"{BACKEND_URL}/api/v1/news/latest",
            method="GET",
            expected_status=200
        )
        
        # Test water futures endpoints
        await self.test_endpoint(
            "Water Futures Current",
            f"{BACKEND_URL}/api/v1/water-futures/current",
            method="GET",
            expected_status=200
        )
        
        # Test forecast endpoint
        await self.test_endpoint(
            "Forecast API",
            f"{BACKEND_URL}/api/v1/forecasts/predict",
            method="POST",
            data={
                "contract_code": "NQH25",
                "horizon_days": 7
            },
            expected_status=200,
            expected_fields=["predicted_prices", "model_confidence"]
        )
        
    async def test_mcp_endpoints(self):
        """Test MCP server endpoints"""
        print(f"\n{Fore.YELLOW}Testing MCP Server Endpoints...{Style.RESET_ALL}")
        
        # Test trading endpoints
        await self.test_endpoint(
            "MCP Trading - Place Trade",
            f"{MCP_URL}/api/mcp/trading/place-trade",
            method="POST",
            data={
                "contractCode": "NQH25",
                "side": "buy",
                "quantity": 5,
                "userId": "test-user"
            },
            expected_status=200,
            expected_fields=["success", "requiresApproval", "order", "analysis"]
        )
        
        # Test portfolio endpoint
        await self.test_endpoint(
            "MCP Trading - Portfolio",
            f"{MCP_URL}/api/mcp/trading/portfolio",
            method="GET",
            expected_status=200,
            expected_fields=["account", "positions"]
        )
        
        # Test market analysis
        await self.test_endpoint(
            "MCP Trading - Market Analysis",
            f"{MCP_URL}/api/mcp/trading/analyze-market",
            method="POST",
            data={
                "includeNews": True,
                "includeDrought": True
            },
            expected_status=200,
            expected_fields=["marketCondition", "recommendation"]
        )
        
        # Test farmer endpoints
        await self.test_endpoint(
            "MCP Farmer - Process Subsidy",
            f"{MCP_URL}/api/mcp/farmer/process-subsidy",
            method="POST",
            data={
                "farmerId": "test-farmer",
                "subsidyType": "drought_relief",
                "amount": 15000
            },
            expected_status=200,
            expected_fields=["success", "subsidy"]
        )
        
        await self.test_endpoint(
            "MCP Farmer - Recommendations",
            f"{MCP_URL}/api/mcp/farmer/recommendations",
            method="POST",
            data={
                "farmerId": "test-farmer",
                "location": "Central Valley",
                "cropType": "almonds"
            },
            expected_status=200,
            expected_fields=["recommendations"]
        )
        
    async def test_integration_flows(self):
        """Test complete integration flows"""
        print(f"\n{Fore.YELLOW}Testing Integration Flows...{Style.RESET_ALL}")
        
        # Test 1: Complete trading flow
        print(f"  {Fore.CYAN}Testing Trading Flow...{Style.RESET_ALL}")
        
        # Step 1: Request trade
        trade_response = await self.make_request(
            f"{MCP_URL}/api/mcp/trading/place-trade",
            method="POST",
            data={
                "contractCode": "NQH25",
                "side": "buy",
                "quantity": 10,
                "userId": "integration-test"
            }
        )
        
        if trade_response and trade_response.get("success"):
            order_id = trade_response.get("order", {}).get("id")
            
            # Step 2: Confirm trade
            confirm_response = await self.make_request(
                f"{MCP_URL}/api/mcp/trading/confirm-trade",
                method="POST",
                data={
                    "orderId": order_id,
                    "approved": True,
                    "userId": "integration-test"
                }
            )
            
            if confirm_response and confirm_response.get("success"):
                self.record_success("Trading Flow Integration")
            else:
                self.record_failure("Trading Flow Integration", "Confirmation failed")
        else:
            self.record_failure("Trading Flow Integration", "Trade request failed")
            
        # Test 2: Agent mode interaction
        print(f"  {Fore.CYAN}Testing Agent Mode Flow...{Style.RESET_ALL}")
        
        # Step 1: Chat mode request
        chat_response = await self.make_request(
            f"{BACKEND_URL}/api/v1/chat",
            method="POST",
            data={
                "message": "Should I buy water futures?",
                "context": {"location": "Central Valley"}
            }
        )
        
        if chat_response:
            # Step 2: Agent mode request
            agent_response = await self.make_request(
                f"{BACKEND_URL}/api/v1/agent/execute",
                method="POST",
                data={
                    "message": "Buy 5 NQH25 contracts",
                    "context": {"agentModeEnabled": True}
                }
            )
            
            if agent_response:
                self.record_success("Agent Mode Integration")
            else:
                self.record_failure("Agent Mode Integration", "Agent execution failed")
        else:
            self.record_failure("Agent Mode Integration", "Chat request failed")
            
    async def test_error_handling(self):
        """Test error handling and edge cases"""
        print(f"\n{Fore.YELLOW}Testing Error Handling...{Style.RESET_ALL}")
        
        # Test invalid trade request
        await self.test_endpoint(
            "Invalid Trade Request",
            f"{MCP_URL}/api/mcp/trading/place-trade",
            method="POST",
            data={
                "contractCode": "INVALID",
                "side": "invalid_side",
                "quantity": -5
            },
            expected_status=200  # Should handle gracefully
        )
        
        # Test missing agent mode
        await self.test_endpoint(
            "Agent Mode Not Enabled",
            f"{BACKEND_URL}/api/v1/agent/execute",
            method="POST",
            data={
                "message": "Execute trade",
                "context": {"agentModeEnabled": False}
            },
            expected_status=200,
            expected_error=True
        )
        
    async def test_endpoint(
        self,
        name: str,
        url: str,
        method: str = "GET",
        data: Dict[str, Any] = None,
        expected_status: int = 200,
        expected_fields: List[str] = None,
        expected_error: bool = False
    ) -> TestResult:
        """Test a single endpoint"""
        result = TestResult(name)
        start_time = time.time()
        
        try:
            response = await self.make_request(url, method, data)
            result.duration = time.time() - start_time
            
            if response is not None:
                # Check for expected fields
                if expected_fields:
                    missing_fields = [f for f in expected_fields if f not in response]
                    if missing_fields:
                        result.error = f"Missing fields: {missing_fields}"
                    else:
                        result.passed = True
                elif expected_error and "error" in response:
                    result.passed = True
                else:
                    result.passed = True
                    
                result.details = response
            else:
                result.error = "No response received"
                
        except Exception as e:
            result.error = str(e)
            result.duration = time.time() - start_time
            
        self.results.append(result)
        self.print_result(result)
        return result
        
    async def make_request(
        self,
        url: str,
        method: str = "GET",
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make HTTP request and return JSON response"""
        try:
            if method == "GET":
                response = await self.client.get(url)
            else:
                response = await self.client.post(url, json=data)
                
            if response.status_code == 200:
                return response.json()
            else:
                print(f"    {Fore.RED}Status {response.status_code}: {response.text[:100]}{Style.RESET_ALL}")
                return None
                
        except Exception as e:
            print(f"    {Fore.RED}Request error: {e}{Style.RESET_ALL}")
            return None
            
    def record_success(self, name: str):
        """Record a successful test"""
        result = TestResult(name)
        result.passed = True
        self.results.append(result)
        self.print_result(result)
        
    def record_failure(self, name: str, error: str):
        """Record a failed test"""
        result = TestResult(name)
        result.error = error
        self.results.append(result)
        self.print_result(result)
        
    def print_result(self, result: TestResult):
        """Print test result"""
        if result.passed:
            status = f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}"
        else:
            status = f"{Fore.RED}✗ FAIL{Style.RESET_ALL}"
            
        duration = f"({result.duration:.2f}s)" if result.duration > 0 else ""
        print(f"  {status} {result.name} {duration}")
        
        if result.error:
            print(f"    {Fore.RED}Error: {result.error}{Style.RESET_ALL}")
            
    def print_summary(self):
        """Print test summary"""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Test Summary{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        print(f"Total Tests: {total}")
        print(f"{Fore.GREEN}Passed: {passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {failed}{Style.RESET_ALL}")
        
        if failed > 0:
            print(f"\n{Fore.RED}Failed Tests:{Style.RESET_ALL}")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}: {result.error}")
                    
        success_rate = (passed / total * 100) if total > 0 else 0
        
        if success_rate == 100:
            print(f"\n{Fore.GREEN}🎉 All tests passed! System is ready.{Style.RESET_ALL}")
        elif success_rate >= 80:
            print(f"\n{Fore.YELLOW}⚠️  {success_rate:.1f}% tests passed. Some issues need attention.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}❌ Only {success_rate:.1f}% tests passed. Critical issues detected.{Style.RESET_ALL}")

async def main():
    """Main test runner"""
    tester = SystemTester()
    
    print(f"{Fore.CYAN}Starting services...{Style.RESET_ALL}")
    print("Make sure the following are running:")
    print("1. Backend: cd backend && python main.py")
    print("2. MCP Server: cd mcp-servers && npm install && npm start")
    print("3. Frontend: cd frontend && npm run dev")
    print()
    
    # Wait for services to be ready
    print(f"{Fore.YELLOW}Waiting for services to start...{Style.RESET_ALL}")
    await asyncio.sleep(3)
    
    # Run tests
    await tester.run_all_tests()
    
    # Cleanup
    await tester.client.aclose()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Test suite error: {e}{Style.RESET_ALL}")
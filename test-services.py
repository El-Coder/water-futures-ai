#!/usr/bin/env python3
"""
Test script to verify all services are working properly
"""

import requests
import json
import time
from colorama import init, Fore, Style

init(autoreset=True)

def test_service(name, url, method="GET", data=None):
    """Test a service endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            print(f"{Fore.GREEN}✅ {name}: SUCCESS{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️  {name}: Status {response.status_code}{Style.RESET_ALL}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}❌ {name}: NOT RUNNING{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ {name}: ERROR - {e}{Style.RESET_ALL}")
        return False

def main():
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"Water Futures AI - Service Health Check")
    print(f"{'='*50}{Style.RESET_ALL}\n")
    
    all_tests_passed = True
    
    # Test Backend API
    print(f"{Fore.BLUE}Testing Backend Services...{Style.RESET_ALL}")
    all_tests_passed &= test_service(
        "Backend Health", 
        "http://localhost:8000/health"
    )
    all_tests_passed &= test_service(
        "Water Futures API", 
        "http://localhost:8000/api/v1/water-futures/current"
    )
    all_tests_passed &= test_service(
        "News API", 
        "http://localhost:8000/api/v1/news/latest?limit=5"
    )
    
    print()
    
    # Test Chat Service
    print(f"{Fore.BLUE}Testing Chat Service...{Style.RESET_ALL}")
    all_tests_passed &= test_service(
        "Chat Service Health", 
        "http://localhost:8001/health"
    )
    all_tests_passed &= test_service(
        "Chat Endpoint", 
        "http://localhost:8001/api/v1/chat",
        method="POST",
        data={"message": "Hello", "context": {}}
    )
    
    print()
    
    # Test MCP Wrapper
    print(f"{Fore.BLUE}Testing MCP Wrapper...{Style.RESET_ALL}")
    all_tests_passed &= test_service(
        "MCP Wrapper Health", 
        "http://localhost:8080/health"
    )
    all_tests_passed &= test_service(
        "Portfolio Endpoint", 
        "http://localhost:8080/api/mcp/trading/portfolio"
    )
    
    print()
    
    # Test Frontend
    print(f"{Fore.BLUE}Testing Frontend...{Style.RESET_ALL}")
    all_tests_passed &= test_service(
        "Frontend", 
        "http://localhost:5173"
    )
    
    # Summary
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    if all_tests_passed:
        print(f"{Fore.GREEN}✅ All services are working properly!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}You can now:{Style.RESET_ALL}")
        print(f"  • Open the frontend at http://localhost:5173")
        print(f"  • Use the chat feature (both safe and agent modes)")
        print(f"  • View water futures prices and news")
        print(f"  • Execute trades and process subsidies in agent mode")
    else:
        print(f"{Fore.YELLOW}⚠️  Some services are not working properly.{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}To start all services, run:{Style.RESET_ALL}")
        print(f"  ./start-local.sh")
        print(f"\n{Fore.CYAN}Or with Docker:{Style.RESET_ALL}")
        print(f"  docker-compose up")
    
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
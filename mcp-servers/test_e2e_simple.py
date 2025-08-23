#!/usr/bin/env python3
"""
Simple end-to-end test to verify API keys and balance fetching
Tests both Alpaca and Crossmint APIs directly
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_alpaca_api():
    """Test Alpaca API with current keys"""
    print("\n🔍 Testing Alpaca API...")
    
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Alpaca API keys not found in environment")
        return False
    
    # Check for special characters that might cause issues
    print(f"   API Key length: {len(api_key)} chars")
    print(f"   Secret Key length: {len(secret_key)} chars")
    
    # Test the API
    headers = {
        'APCA-API-KEY-ID': api_key,
        'APCA-API-SECRET-KEY': secret_key
    }
    
    try:
        response = requests.get(
            'https://paper-api.alpaca.markets/v2/account',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Alpaca API working!")
            print(f"   Cash: ${float(data.get('cash', 0)):,.2f}")
            print(f"   Buying Power: ${float(data.get('buying_power', 0)):,.2f}")
            return True
        else:
            print(f"❌ Alpaca API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Alpaca API error: {str(e)}")
        return False

def test_crossmint_api():
    """Test Crossmint API with current key"""
    print("\n🔍 Testing Crossmint API...")
    
    api_key = os.getenv('CROSSMINT_API_KEY')
    
    if not api_key:
        print("❌ Crossmint API key not found in environment")
        return False
    
    # Check for special characters
    print(f"   API Key length: {len(api_key)} chars")
    
    # Test the API
    headers = {
        'X-API-KEY': api_key
    }
    
    try:
        response = requests.get(
            'https://staging.crossmint.com/api/2025-06-09/wallets/userId:farmerted:evm/balances',
            params={'tokens': 'usdc', 'chains': 'ethereum-sepolia'},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Crossmint API working!")
            if data and len(data) > 0:
                usdc_balance = float(data[0].get('amount', 0))
                print(f"   USDC Balance: {usdc_balance} USDC")
            return True
        else:
            print(f"❌ Crossmint API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Crossmint API error: {str(e)}")
        return False

def test_mcp_server():
    """Test local MCP server if running"""
    print("\n🔍 Testing MCP Server (localhost:8080)...")
    
    try:
        response = requests.get('http://localhost:8080/health')
        if response.status_code == 200:
            print("✅ MCP Server is running")
            
            # Test balance endpoint
            balance_response = requests.get('http://localhost:8080/tools/getAccountBalance')
            if balance_response.status_code == 200:
                data = balance_response.json()
                print(f"✅ Balance endpoint working")
                if 'subsidyAccounts' in data:
                    crossmint_balance = data['subsidyAccounts'].get('crossmint', {}).get('available', 0)
                    print(f"   Crossmint via MCP: ${crossmint_balance:,.2f}")
            return True
        else:
            print("⚠️  MCP Server not running locally")
            return False
    except:
        print("⚠️  MCP Server not running locally")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Water Futures AI - API Key Verification")
    print("=" * 50)
    
    # Test each API
    alpaca_ok = test_alpaca_api()
    crossmint_ok = test_crossmint_api()
    mcp_ok = test_mcp_server()
    
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Alpaca API: {'✅ Working' if alpaca_ok else '❌ Failed'}")
    print(f"  Crossmint API: {'✅ Working' if crossmint_ok else '❌ Failed'}")
    print(f"  MCP Server: {'✅ Running' if mcp_ok else '⚠️ Not Running'}")
    print("=" * 50)
    
    # Exit with error if any API failed
    if not (alpaca_ok and crossmint_ok):
        sys.exit(1)
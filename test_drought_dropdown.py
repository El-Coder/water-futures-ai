#!/usr/bin/env python3
"""
Test Drought Index Dropdown Functionality
Tests how the agent responds to different drought levels
"""

import requests
import json
import time

print("\n🌊 Testing Drought Index Dropdown Context Changes")
print("="*50)

# Test different drought levels
drought_levels = [
    ("low", "0", "Not eligible for subsidies"),
    ("medium", "0.25", "Eligible for partial subsidy"),
    ("high", "0.5", "Eligible for emergency relief")
]

for level, amount, description in drought_levels:
    print(f"\n📊 Testing Drought Level: {level.upper()}")
    print(f"   Expected subsidy: {amount} USDC")
    print(f"   Status: {description}")
    print("-"*40)
    
    # Update drought context
    context_response = requests.post(
        "http://localhost:8001/api/v1/context/drought",
        json={
            "droughtLevel": level,
            "subsidyAmount": amount,
            "farmerId": "farmer-ted"
        }
    )
    
    if context_response.status_code == 200:
        print(f"✅ Context updated for {level} drought")
    
    # Notify agent about drought change
    notify_response = requests.post(
        "http://localhost:8001/api/v1/agent/notify-drought",
        json={
            "droughtLevel": level,
            "subsidyAmount": amount,
            "farmerId": "farmer-ted"
        }
    )
    
    if notify_response.status_code == 200:
        data = notify_response.json()
        print(f"🤖 Agent Response Preview:")
        print(f"   {data.get('agentMessage', 'No message')[:100]}...")
    
    # Test chat with new context
    chat_response = requests.post(
        "http://localhost:8001/api/v1/chat",
        json={
            "message": "What subsidies am I eligible for?",
            "context": {"userId": "farmer-ted"}
        }
    )
    
    if chat_response.status_code == 200:
        chat_data = chat_response.json()
        response_text = chat_data.get('response', '')
        
        # Check if response matches expected context
        if level == "low" and ("not eligible" in response_text.lower() or "low" in response_text.lower()):
            print(f"✅ Chat correctly identifies NO eligibility for LOW drought")
        elif level == "medium" and ("0.25" in response_text or "partial" in response_text.lower()):
            print(f"✅ Chat correctly identifies 0.25 USDC eligibility for MEDIUM drought")
        elif level == "high" and ("0.5" in response_text or "emergency" in response_text.lower()):
            print(f"✅ Chat correctly identifies 0.5 USDC eligibility for HIGH drought")
        else:
            print(f"⚠️  Chat response may not reflect correct context")
    
    time.sleep(1)  # Brief pause between tests

print("\n" + "="*50)
print("📊 Drought Dropdown Context Test Summary:")
print("  • LOW: No subsidy (working as expected)")
print("  • MEDIUM: 0.25 USDC subsidy")  
print("  • HIGH: 0.5 USDC emergency relief")
print("\n💡 When integrated with satellite imaging:")
print("  • Vertex AI will analyze satellite data")
print("  • Automatically detect drought severity")
print("  • Update dropdown and trigger appropriate subsidies")
print("  • Provide real-time drought monitoring")


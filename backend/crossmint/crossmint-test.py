import requests

url = "https://staging.crossmint.com/api/2025-06-09/wallets/userId:unclesam:evm/tokens/ethereum-sepolia:usdc/transfers"

payload = {
    "recipient": "0x639A356DB809fA45A367Bc71A6D766dF2e9C6D15",  
    "amount": "0.5", 
}

import os

headers = {
    "x-api-key": os.getenv("CROSSMINT_API_KEY", "your_crossmint_api_key_here"),
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
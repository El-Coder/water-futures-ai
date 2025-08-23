import requests

url = "https://staging.crossmint.com/api/2025-06-09/wallets/userId:unclesam:evm/balances"

querystring = {"tokens":"usdc","chains":"ethereum-sepolia"}

import os

headers = {"X-API-KEY": os.getenv("CROSSMINT_API_KEY", "your_crossmint_api_key_here")}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())

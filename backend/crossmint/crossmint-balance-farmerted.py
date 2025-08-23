import requests

url = "https://staging.crossmint.com/api/2025-06-09/wallets/user:unclesam:evm/balances"

querystring = {"tokens":"usdc","chains":"ethereum-sepolia"}

headers = {"X-API-KEY": "<x-api-key>"}

response = requests.post(url, json=payload, headers=headers)

print(response.json())

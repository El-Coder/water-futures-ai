import requests
import os
from dotenv import load_dotenv

load_dotenv("../.env")

url = "https://staging.crossmint.com/api/2025-06-09/wallets/email:farmerted@example.com:evm/balances"

querystring = {"tokens":"usdc","chains":"ethereum-sepolia"}

headers = {"X-API-KEY": os.getenv("CROSSMINT_API_KEY")}

response = requests.get(url, params=querystring, headers=headers)

print(response.json())

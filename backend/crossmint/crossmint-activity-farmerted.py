import requests
import os
from dotenv import load_dotenv

load_dotenv("../.env")

url = "https://staging.crossmint.com/api/unstable/wallets/userId:farmerted:evm/activity"

querystring = {"chain":"ethereum-sepolia"}

headers = {"X-API-KEY": os.getenv("CROSSMINT_API_KEY")}

response = requests.get(url, params=querystring, headers=headers)

print(response.json())

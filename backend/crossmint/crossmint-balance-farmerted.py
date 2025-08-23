import os
import sys
from pathlib import Path
import requests

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

url = "https://staging.crossmint.com/api/2025-06-09/wallets/email:farmerted@example.com:evm/balances"

querystring = {"tokens":"usdc","chains":"ethereum-sepolia"}

headers = {"X-API-KEY": os.getenv("CROSSMINT_API_KEY")}

response = requests.get(url, params=querystring, headers=headers)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.json())

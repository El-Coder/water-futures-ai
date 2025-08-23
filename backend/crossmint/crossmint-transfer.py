import os
import sys
from pathlib import Path
import requests

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

url = "https://staging.crossmint.com/api/2025-06-09/wallets/userId:unclesam:evm/tokens/ethereum-sepolia:usdc/transfers"

payload = {
    "recipient": "0x639A356DB809fA45A367Bc71A6D766dF2e9C6D15",  
    "amount": "0.5", 
}

headers = {
    "x-api-key": os.getenv("CROSSMINT_API_KEY"),
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print("Transfer successful!")
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.json())
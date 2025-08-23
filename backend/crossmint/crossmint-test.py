import requests

url = "https://staging.crossmint.com/api/2025-06-09/wallets/userId:unclesam:evm/tokens/ethereum-sepolia:usdc/transfers"

payload = {
    "recipient": "0x639A356DB809fA45A367Bc71A6D766dF2e9C6D15",  
    "amount": "0.5", 
}

headers = {
    "x-api-key": "sk_staging_9ymj6pzDVzTXAJxEHx2Eiaudh7Bv9tAZYkbC7oJyXxQUupx3fi4pQyNmShEZ7BMDSkT2DGw8EyxcPUvqLyVoJTP3DQQ2JQya8iB7eTK95tWKHDK9xMGapfbgoYBvY8ettfPjCw2Sm9kxEMxEe3iWAvWEPrW3PuQUXAzjppFbauu5uHNK1rDdiQ2XoKecGbMre99jNGmdVQkabJ84QYPbzMBj",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
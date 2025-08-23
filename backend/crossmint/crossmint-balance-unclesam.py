import requests

url = "https://staging.crossmint.com/api/2025-06-09/wallets/userId:unclesam:evm/balances"

querystring = {"tokens":"usdc","chains":"ethereum-sepolia"}

headers = {"X-API-KEY": "sk_staging_9ymj6pzDVzTXAJxEHx2Eiaudh7Bv9tAZYkbC7oJyXxQUupx3fi4pQyNmShEZ7BMDSkT2DGw8EyxcPUvqLyVoJTP3DQQ2JQya8iB7eTK95tWKHDK9xMGapfbgoYBvY8ettfPjCw2Sm9kxEMxEe3iWAvWEPrW3PuQUXAzjppFbauu5uHNK1rDdiQ2XoKecGbMre99jNGmdVQkabJ84QYPbzMBj"}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())

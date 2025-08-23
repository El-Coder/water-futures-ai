# Crossmint Integration Scripts

These scripts demonstrate integration with Crossmint API for blockchain payments and wallet management.

## Prerequisites

Make sure you have the required dependencies installed:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

Required packages:
- `requests` - HTTP client for API calls
- `python-dotenv` - Environment variable management

## Environment Setup

Set your Crossmint API key in `backend/.env`:

```
CROSSMINT_API_KEY=sk_staging_your_key_here
```

## Scripts

### 1. Balance Checkers
- `crossmint-balance-farmerted.py` - Check farmer's wallet balance
- `crossmint-balance-unclesam.py` - Check government wallet balance

### 2. Activity Monitor
- `crossmint-activity-farmerted.py` - View transaction history

### 3. Transfer
- `crossmint-transfer.py` - Send USDC payments

## Usage

```bash
# Check farmer balance
python crossmint/crossmint-balance-farmerted.py

# View transaction history  
python crossmint/crossmint-activity-farmerted.py

# Send payment
python crossmint/crossmint-transfer.py
```

## API Integration

All scripts use environment variables for secure API key management and follow best practices for blockchain integration.

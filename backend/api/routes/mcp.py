"""
MCP (Model Context Protocol) Routes for farmer balance and subsidy management
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from services.crossmint_service import crossmint_service
from services.farmer_agent import farmer_agent

router = APIRouter()

# Farmer wallet mappings
FARMER_WALLETS = {
    "farmer-ted": "0xfarmerted123456789",
    "farmer-alice": "0xfarmeralice987654321",
    "farmer-bob": "0xfarmerbob555666777"
}

@router.get("/farmer/balance/{farmer_id}")
async def get_farmer_balance(farmer_id: str) -> Dict[str, Any]:
    """Get farmer's wallet balance"""
    try:
        # Get farmer's wallet address
        wallet_address = FARMER_WALLETS.get(farmer_id)
        if not wallet_address:
            raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")
        
        # Get balance from Crossmint service
        balance_data = await crossmint_service.get_wallet_balance(wallet_address)
        
        # Return farmer-specific balance data
        return {
            "farmer_id": farmer_id,
            "wallet": wallet_address,
            "balance": balance_data.get("balance", 0),
            "currency": balance_data.get("currency", "USD"),
            "last_updated": balance_data.get("last_updated"),
            "pending_subsidies": 0,
            "available_subsidies": await _get_available_subsidies(farmer_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/farmer/subsidies/{farmer_id}")
async def get_farmer_subsidies(farmer_id: str) -> Dict[str, Any]:
    """Get available subsidies for farmer"""
    try:
        # Check eligibility based on location and conditions
        eligibility = await crossmint_service.check_eligibility(
            farmer_id=farmer_id,
            drought_severity=4,  # This would come from weather data
            location="California"
        )
        
        return {
            "farmer_id": farmer_id,
            "eligible": eligibility["eligible"],
            "programs": eligibility["programs"],
            "total_available": eligibility["total_available"],
            "drought_severity": eligibility["drought_severity"],
            "location": eligibility["location"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/farmer/claim-subsidy")
async def claim_subsidy(request: Dict[str, Any]) -> Dict[str, Any]:
    """Process subsidy claim for farmer"""
    try:
        farmer_id = request.get("farmer_id")
        subsidy_type = request.get("subsidy_type", "drought_relief")
        amount = request.get("amount", 15000)
        
        wallet_address = FARMER_WALLETS.get(farmer_id)
        if not wallet_address:
            raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")
        
        # Process the subsidy payment
        result = await crossmint_service.process_subsidy_payment(
            farmer_wallet=wallet_address,
            amount=amount,
            subsidy_type=subsidy_type,
            metadata={
                "farmer_id": farmer_id,
                "claim_date": request.get("claim_date"),
                "reason": request.get("reason", "Drought relief assistance")
            }
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _get_available_subsidies(farmer_id: str) -> int:
    """Helper function to get available subsidies for a farmer"""
    try:
        eligibility = await crossmint_service.check_eligibility(
            farmer_id=farmer_id,
            drought_severity=4,  # Would be dynamic based on actual conditions
            location="California"
        )
        return eligibility.get("total_available", 0)
    except:
        return 0
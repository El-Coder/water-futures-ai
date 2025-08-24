"""
Crossmint Service for processing government subsidies
"""
import os
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
import json

class CrossmintService:
    def __init__(self):
        self.api_key = os.getenv("CROSSMINT_API_KEY")
        self.uncle_sam_wallet = os.getenv("UNCLE_SAM_WALLET_ADDRESS")
        self.base_url = "https://staging.crossmint.com/api"
        
        if not self.api_key:
            print("⚠️ Crossmint API key not found in environment variables")
        if not self.uncle_sam_wallet:
            print("⚠️ Uncle Sam wallet address not found in environment variables")
    
    async def get_transaction_history(self, wallet_address: str) -> list:
        """
        Get transaction history for a wallet from Crossmint
        """
        try:
            # Return empty list for now - Crossmint transaction history implementation pending
            return []
        except Exception as e:
            print(f"Error getting transaction history: {e}")
            return []
    
    async def process_subsidy_payment(
        self, 
        farmer_wallet: str,
        amount: float,
        subsidy_type: str = "drought_relief",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a government subsidy payment from Uncle Sam to farmer
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Crossmint API key not configured",
                "simulated": True,
                "payment_id": f"SIM-{datetime.now().timestamp():.0f}",
                "amount": amount,
                "type": subsidy_type
            }
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payment_data = {
            "from": self.uncle_sam_wallet,
            "to": farmer_wallet,
            "amount": str(amount),
            "currency": "usd",
            "type": "subsidy",
            "metadata": {
                "subsidy_type": subsidy_type,
                "processor": "Water Futures AI",
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # For hackathon, we'll simulate the payment
                # In production, this would be the actual Crossmint API call
                # response = await client.post(
                #     f"{self.base_url}/payments/transfer",
                #     headers=headers,
                #     json=payment_data
                # )
                
                # Simulated successful response
                return {
                    "success": True,
                    "payment_id": f"CROSS-{datetime.now().timestamp():.0f}",
                    "transaction_hash": f"0x{''.join(['abcdef0123456789'[i % 16] for i in range(64)])}",
                    "from_wallet": self.uncle_sam_wallet,
                    "to_wallet": farmer_wallet,
                    "amount": amount,
                    "type": subsidy_type,
                    "processor": "Crossmint",
                    "source": "US Government (Uncle Sam)",
                    "status": "completed",
                    "timestamp": datetime.now().isoformat(),
                    "message": f"${amount:,.2f} subsidy successfully transferred from Uncle Sam"
                }
                
        except Exception as e:
            print(f"Crossmint payment error: {e}")
            return {
                "success": False,
                "error": str(e),
                "simulated": True,
                "payment_id": f"SIM-{datetime.now().timestamp():.0f}",
                "amount": amount,
                "type": subsidy_type
            }
    
    async def check_eligibility(
        self,
        farmer_id: str,
        drought_severity: int,
        location: str
    ) -> Dict[str, Any]:
        """
        Check farmer's eligibility for subsidies
        """
        # Simple eligibility check based on drought severity
        eligible_programs = []
        
        if drought_severity >= 3:
            eligible_programs.append({
                "program": "Federal Drought Relief",
                "amount": 15000,
                "requirements": "Drought severity 3+"
            })
        
        if drought_severity >= 4:
            eligible_programs.append({
                "program": "Emergency Water Assistance",
                "amount": 25000,
                "requirements": "Drought severity 4+"
            })
        
        if drought_severity == 5:
            eligible_programs.append({
                "program": "Critical Drought Aid",
                "amount": 50000,
                "requirements": "Drought severity 5"
            })
        
        return {
            "eligible": len(eligible_programs) > 0,
            "programs": eligible_programs,
            "total_available": sum(p["amount"] for p in eligible_programs),
            "farmer_id": farmer_id,
            "location": location,
            "drought_severity": drought_severity
        }
    
    async def get_wallet_balance(self, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get wallet balance (defaults to Uncle Sam's wallet)
        """
        wallet = wallet_address or self.uncle_sam_wallet
        
        if not self.api_key:
            return {
                "wallet": wallet,
                "balance": 1000000000,  # $1B for Uncle Sam
                "currency": "USD",
                "simulated": True
            }
        
        headers = {"X-API-KEY": self.api_key}
        
        try:
            async with httpx.AsyncClient() as client:
                # For Uncle Sam, keep the large balance
                if wallet == self.uncle_sam_wallet:
                    balance = 1000000000  # $1B for Uncle Sam
                    return {
                        "wallet": wallet,
                        "balance": balance,
                        "currency": "USD",
                        "available_for_subsidies": 500000000,
                        "pending_payments": 0,
                        "last_updated": datetime.now().isoformat()
                    }
                
                # For farmer wallets, get REAL balance from Crossmint API
                user_id = "farmerted" if "farmerted" in wallet else "farmeralice"
                url = f"https://staging.crossmint.com/api/2025-06-09/wallets/userId:{user_id}:evm/balances"
                params = {"tokens": "usdc", "chains": "ethereum-sepolia"}
                
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        # Get real USDC balance
                        usdc_balance = float(data[0].get("amount", 0))
                        return {
                            "wallet": wallet,
                            "balance": usdc_balance,  # Real balance from Crossmint
                            "currency": "USDC",
                            "available_for_subsidies": 0,
                            "pending_payments": 0,
                            "last_updated": datetime.now().isoformat()
                        }
                
                # Fallback if API fails
                return {
                    "wallet": wallet,
                    "balance": 0,
                    "currency": "USDC",
                    "available_for_subsidies": 0,
                    "pending_payments": 0,
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "wallet": wallet,
                "balance": 0,
                "error": str(e),
                "simulated": True
            }

# Singleton instance
crossmint_service = CrossmintService()
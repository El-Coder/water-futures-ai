"""
Direct Crossmint API routes that call the Python scripts
"""
from fastapi import APIRouter, HTTPException
import subprocess
import json
import os
from pathlib import Path

router = APIRouter()

@router.get("/balance/{user_id}")
async def get_crossmint_balance_direct(user_id: str):
    """Get Crossmint balance by directly calling the Python script"""
    try:
        # Map user IDs to script names
        script_map = {
            "farmerted": "crossmint-balance-farmerted.py",
            "farmer-ted": "crossmint-balance-farmerted.py",
            "unclesam": "crossmint-balance-unclesam.py"
        }
        
        script_name = script_map.get(user_id)
        if not script_name:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Get the script path
        backend_dir = Path(__file__).parent.parent.parent
        script_path = backend_dir / "crossmint" / script_name
        
        if not script_path.exists():
            raise HTTPException(status_code=404, detail=f"Script not found: {script_path}")
        
        # Run the script
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True,
            text=True,
            cwd=str(backend_dir)
        )
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Script error: {result.stderr}")
        
        # Parse the output
        output = result.stdout.strip()
        data = json.loads(output.replace("'", '"'))
        
        # Extract USDC balance
        usdc_balance = 0
        if isinstance(data, list) and len(data) > 0:
            for token in data:
                if token.get("symbol") == "usdc":
                    # The amount field contains the balance as a string
                    usdc_balance = float(token.get("amount", 0))
                    break
        
        return {
            "user_id": user_id,
            "balance": usdc_balance,
            "currency": "USDC",
            "network": "ethereum-sepolia",
            "raw_data": data
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse script output: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
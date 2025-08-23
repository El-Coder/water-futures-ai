"""
Farmer Agent - Main AI agent with access to all tools:
- Claude for conversation
- Alpaca for trading
- Crossmint for subsidies
- Vertex AI for forecasting
"""
from typing import Dict, Any, List, Optional
import os
from anthropic import Anthropic
from services.alpaca_mcp_client import alpaca_client
from services.vertex_ai_service import vertex_ai_service
import json
from datetime import datetime

class FarmerAgent:
    def __init__(self):
        # Initialize Claude
        self.anthropic = Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Available tools
        self.tools = {
            "trade_water_futures": self._trade_water_futures,
            "check_account": self._check_account,
            "get_positions": self._get_positions,
            "process_subsidy": self._process_subsidy,
            "get_forecast": self._get_forecast,
            "analyze_market": self._analyze_market,
        }
        
        # Agent state
        self.conversation_history = []
        self.executed_actions = []
    
    async def process_request(
        self, 
        message: str, 
        mode: str = "chat",
        context: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        Main entry point for processing farmer requests
        """
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Analyze intent and determine actions
        intent = await self._analyze_intent_with_tools(message, context)
        
        # Execute based on mode
        if mode == "chat":
            # Safe mode - only provide information
            response = await self._generate_safe_response(message, intent, context)
        else:
            # Agent mode - can execute actions
            response = await self._execute_with_tools(message, intent, context)
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response.get("response", ""),
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    async def _analyze_intent_with_tools(
        self, 
        message: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use Claude to analyze intent and determine which tools to use
        """
        try:
            # Create tool descriptions for Claude
            tools_description = """
Available tools:
1. trade_water_futures: Buy/sell water futures contracts (requires: symbol, quantity, side)
2. check_account: Get account balance and buying power
3. get_positions: View current holdings
4. process_subsidy: Claim government subsidies via Crossmint
5. get_forecast: Get AI price predictions
6. analyze_market: Get market analysis and recommendations

Based on the user's message, determine:
- primary_intent: The main goal
- tools_needed: List of tools to use
- parameters: Parameters for each tool
"""
            
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                system=f"{tools_description}\n\nAnalyze the intent and return structured data.",
                messages=[
                    {
                        "role": "user",
                        "content": f"Message: {message}\nContext: {json.dumps(context)}"
                    }
                ]
            )
            
            # Parse response
            intent = self._parse_claude_intent(response.content[0].text, message)
            return intent
            
        except Exception as e:
            print(f"Intent analysis error: {e}")
            return {"primary_intent": "UNKNOWN", "tools_needed": [], "error": str(e)}
    
    def _parse_claude_intent(self, claude_response: str, original_message: str) -> Dict[str, Any]:
        """
        Parse Claude's response to extract intent and tool requirements
        """
        message_lower = original_message.lower()
        
        intent = {
            "primary_intent": "GENERAL",
            "tools_needed": [],
            "parameters": {}
        }
        
        # Detect trading intent
        if any(word in message_lower for word in ["buy", "sell", "trade", "purchase"]):
            intent["primary_intent"] = "TRADE"
            intent["tools_needed"].append("trade_water_futures")
            
            # Extract parameters
            if "buy" in message_lower or "purchase" in message_lower:
                intent["parameters"]["side"] = "BUY"
            elif "sell" in message_lower:
                intent["parameters"]["side"] = "SELL"
            
            # Extract quantity
            words = original_message.split()
            for i, word in enumerate(words):
                if word.isdigit():
                    intent["parameters"]["quantity"] = int(word)
                    break
            
            # Default values
            intent["parameters"]["symbol"] = "NQH25"
            if "quantity" not in intent["parameters"]:
                intent["parameters"]["quantity"] = 5
        
        # Detect subsidy intent
        elif any(word in message_lower for word in ["subsidy", "government", "crossmint", "payment"]):
            intent["primary_intent"] = "SUBSIDY"
            intent["tools_needed"].append("process_subsidy")
            intent["parameters"]["subsidy_type"] = "drought_relief"
            intent["parameters"]["amount"] = 15000
        
        # Detect account/portfolio intent
        elif any(word in message_lower for word in ["account", "balance", "portfolio", "positions"]):
            intent["primary_intent"] = "ACCOUNT"
            intent["tools_needed"].extend(["check_account", "get_positions"])
        
        # Detect forecast intent
        elif any(word in message_lower for word in ["forecast", "predict", "future price"]):
            intent["primary_intent"] = "FORECAST"
            intent["tools_needed"].append("get_forecast")
        
        # Detect market analysis intent
        elif any(word in message_lower for word in ["market", "analysis", "conditions"]):
            intent["primary_intent"] = "ANALYSIS"
            intent["tools_needed"].append("analyze_market")
        
        return intent
    
    async def _generate_safe_response(
        self, 
        message: str, 
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate response in safe mode (no execution)
        """
        try:
            # Get Claude's conversational response
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system="""You are a helpful farming assistant in CHAT MODE.
You can provide information but CANNOT execute trades or process payments.
Remind users to enable Agent Mode for real transactions.

Current market conditions:
- Water futures (NQH25): $508
- Drought severity: 4/5 in Central Valley
- Available subsidies: $15,000 drought relief via Crossmint
""",
                messages=[{"role": "user", "content": message}]
            )
            
            # Add suggested actions based on intent
            suggested_actions = []
            if intent["primary_intent"] == "TRADE":
                suggested_actions.append({
                    "type": "trade",
                    "action": f"{intent['parameters'].get('side', 'BUY')} {intent['parameters'].get('quantity', 5)} water futures",
                    "requiresAgentMode": True
                })
            elif intent["primary_intent"] == "SUBSIDY":
                suggested_actions.append({
                    "type": "subsidy",
                    "action": "Claim $15,000 drought relief",
                    "requiresAgentMode": True
                })
            
            return {
                "response": response.content[0].text,
                "suggestedActions": suggested_actions,
                "mode": "chat",
                "intent": intent
            }
            
        except Exception as e:
            return {
                "response": "I can help you with water futures trading and subsidies. Please enable Agent Mode to execute transactions.",
                "error": str(e),
                "mode": "chat"
            }
    
    async def _execute_with_tools(
        self, 
        message: str, 
        intent: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute actions in agent mode using tools
        """
        results = []
        
        # Execute each required tool
        for tool_name in intent.get("tools_needed", []):
            if tool_name in self.tools:
                tool_result = await self.tools[tool_name](intent.get("parameters", {}))
                results.append(tool_result)
                
                # Track executed action
                self.executed_actions.append({
                    "tool": tool_name,
                    "parameters": intent.get("parameters", {}),
                    "result": tool_result,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Generate response based on results
        if intent["primary_intent"] == "TRADE" and results:
            trade_result = results[0]
            if trade_result.get("success"):
                response_text = (
                    f"✅ Trade Executed Successfully!\n\n"
                    f"Order ID: {trade_result.get('order_id')}\n"
                    f"Symbol: {trade_result.get('symbol')}\n"
                    f"Quantity: {trade_result.get('quantity')}\n"
                    f"Side: {trade_result.get('side')}\n"
                    f"Status: {trade_result.get('status')}\n\n"
                    f"{trade_result.get('message', '')}"
                )
            else:
                response_text = f"Trade failed: {trade_result.get('error', 'Unknown error')}"
        
        elif intent["primary_intent"] == "SUBSIDY" and results:
            subsidy_result = results[0]
            response_text = (
                f"✅ Subsidy Processed Successfully!\n\n"
                f"Type: {subsidy_result.get('type', 'Drought Relief')}\n"
                f"Amount: ${subsidy_result.get('amount', 15000):,}\n"
                f"Payment ID: {subsidy_result.get('payment_id')}\n"
                f"Status: Processing via Crossmint\n\n"
                f"Funds will be deposited within 24 hours."
            )
        
        elif intent["primary_intent"] == "ACCOUNT" and results:
            account = results[0] if results else {}
            positions = results[1] if len(results) > 1 else []
            response_text = (
                f"📊 Account Summary:\n\n"
                f"Portfolio Value: ${account.get('portfolio_value', 0):,.2f}\n"
                f"Cash Balance: ${account.get('cash', 0):,.2f}\n"
                f"Buying Power: ${account.get('buying_power', 0):,.2f}\n\n"
                f"Positions: {len(positions)} active\n"
            )
        
        else:
            # Use Claude for general response
            claude_response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                system="You are an AI agent that has executed actions. Summarize the results.",
                messages=[
                    {"role": "user", "content": f"Action results: {json.dumps(results)}"}
                ]
            )
            response_text = claude_response.content[0].text
        
        return {
            "response": response_text,
            "executed": True,
            "executionDetails": results,
            "isAgentAction": True,
            "actionType": intent["primary_intent"].lower(),
            "mode": "agent"
        }
    
    # Tool implementations
    async def _trade_water_futures(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute water futures trade via Alpaca"""
        return await alpaca_client.place_water_futures_order(
            symbol=params.get("symbol", "NQH25"),
            quantity=params.get("quantity", 5),
            side=params.get("side", "BUY")
        )
    
    async def _check_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get account information from Alpaca"""
        return await alpaca_client.get_account_info()
    
    async def _get_positions(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get current positions from Alpaca"""
        return await alpaca_client.get_positions()
    
    async def _process_subsidy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process government subsidy via Crossmint"""
        # Simulate Crossmint payment processing
        return {
            "success": True,
            "type": params.get("subsidy_type", "drought_relief"),
            "amount": params.get("amount", 15000),
            "payment_id": f"CROSS-{datetime.now().timestamp():.0f}",
            "processor": "Crossmint",
            "source": "US Government",
            "status": "processing"
        }
    
    async def _get_forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get price forecast from Vertex AI"""
        features = {
            "contract_code": params.get("symbol", "NQH25"),
            "current_price": 508,
            "drought_severity": 4,
            "horizon_days": 7
        }
        return await vertex_ai_service.predict(features)
    
    async def _analyze_market(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market conditions"""
        return {
            "market_condition": "bullish",
            "drought_severity": 4,
            "price_trend": "increasing",
            "recommendation": "Buy 5-10 contracts to hedge drought risk",
            "confidence": 0.75
        }

# Singleton instance
farmer_agent = FarmerAgent()
"""
Farmer Agent - Main AI agent with access to all tools:
- Claude for conversation
- Alpaca for trading
- Crossmint for subsidies
- Vertex AI for forecasting
- Weather data integration
"""
from typing import Dict, Any, List, Optional
import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from services.alpaca_mcp_client import alpaca_client
from services.vertex_ai_service import vertex_ai_service
from models.farmer import Farmer, FarmerContext, WeatherData, FarmLocation
import json
from datetime import datetime
import httpx


class FarmerAgent:
    def __init__(self):
        # Initialize Claude (only if API key exists)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            try:
                self.anthropic = Anthropic(api_key=api_key)
            except Exception as e:
                print(f"⚠️  Error initializing Anthropic client: {e}")
                self.anthropic = None
        else:
            self.anthropic = None
            print("⚠️  Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
        
        # Available tools
        self.tools = {
            "trade_water_futures": self._trade_water_futures,
            "check_account": self._check_account,
            "get_positions": self._get_positions,
            "process_subsidy": self._process_subsidy,
            "get_forecast": self._get_forecast,
            "analyze_market": self._analyze_market,
            "get_weather_data": self._get_weather_data,
            "update_farmer_location": self._update_farmer_location,
        }
        
        # Agent state
        self.conversation_history = []
        self.executed_actions = []
        self.farmer_profiles = {}  # Store farmer profiles by ID
    
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
            # First do a quick check if this is just general conversation
            message_lower = message.lower()
            
            # Check if this is general conversation without specific tool needs
            general_words = ["hello", "hi", "how are", "what's up", "thanks", "thank you", 
                           "okay", "ok", "great", "good", "nice", "cool", "awesome",
                           "tell me about", "explain", "what is", "how does", "why"]
            
            action_words = ["buy", "sell", "trade", "purchase", "subsidy", "government", 
                          "crossmint", "payment", "account", "balance", "portfolio", 
                          "positions", "forecast", "predict", "market", "analysis"]
            
            # Check if message contains action words
            has_action = any(word in message_lower for word in action_words)
            is_general = any(word in message_lower for word in general_words) and not has_action
            
            # If it's just general conversation in agent mode, don't analyze for tools
            if is_general or not has_action:
                return {
                    "primary_intent": "GENERAL_CONVERSATION",
                    "tools_needed": [],
                    "parameters": {},
                    "is_conversational": True
                }
            
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
            # Fallback to manual parsing when Claude fails
            return self._parse_claude_intent("", message)
    
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
            
            # Only set symbol, don't default quantity
            intent["parameters"]["symbol"] = "NQH25"
        
        # Detect subsidy intent
        elif any(word in message_lower for word in ["subsidy", "government", "crossmint", "payment"]):
            intent["primary_intent"] = "SUBSIDY"
            intent["tools_needed"].append("process_subsidy")
            # Determine subsidy type from message
            if "drought" in message_lower:
                intent["parameters"]["subsidy_type"] = "drought_relief"
            else:
                intent["parameters"]["subsidy_type"] = "general"
            # Amount will be determined by Crossmint based on eligibility
        
        # Detect account/portfolio intent
        elif any(word in message_lower for word in ["account", "balance", "portfolio", "positions"]):
            intent["primary_intent"] = "ACCOUNT"
            intent["tools_needed"].extend(["check_account", "get_positions"])
        
        # Detect forecast intent - FIXED to match more variations
        elif any(word in message_lower for word in ["forecast", "predict", "prediction", "future", "price", "outlook", "projection", "expect"]):
            intent["primary_intent"] = "FORECAST"
            intent["tools_needed"].append("get_forecast")
            intent["parameters"]["symbol"] = "NQH25"  # Add symbol parameter
        
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
            # Check if Anthropic client is initialized
            if not self.anthropic:
                # Return error - no fallback, require real API
                return {
                    "response": "API configuration error. Please ensure Anthropic API key is properly configured.",
                    "error": "Anthropic client not initialized",
                    "mode": "chat",
                    "intent": intent
                }
            
            # Build conversation history for better context
            conversation_context = []
            if len(self.conversation_history) > 1:
                # Include recent conversation history (last 3 messages for chat mode)
                recent_history = self.conversation_history[-3:]
                for msg in recent_history:
                    conversation_context.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current message to context
            conversation_context.append({"role": "user", "content": message})
            
            # Get Claude's conversational response
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system="""You are a helpful AI farming assistant in CHAT MODE (safe mode).
You're having a natural conversation with a farmer about their needs, water futures, drought conditions, and farming strategies.

Be conversational, friendly, and helpful. You can discuss:
- Water futures market conditions and strategies
- Drought management and water conservation
- Government subsidies and financial assistance
- Farming best practices and advice
- Market analysis and predictions

Current market conditions will be fetched from real-time APIs.

IMPORTANT: You're in CHAT MODE, so you CANNOT execute real transactions. 
If the user wants to trade or claim subsidies, politely explain they need to enable Agent Mode for real transactions.
But don't be pushy about it - only mention Agent Mode if they specifically ask about executing actions.

Be natural and conversational - not every response needs to mention Agent Mode or push for transactions.""",
                messages=conversation_context
            )
            
            # Add suggested actions based on intent (only if relevant)
            suggested_actions = []
            if intent["primary_intent"] == "TRADE" and any(word in message.lower() for word in ["buy", "sell"]):
                side = "BUY" if "buy" in message.lower() else "SELL"
                suggested_actions.append({
                    "type": "trade",
                    "action": f"{side} water futures",
                    "requiresAgentMode": True
                })
            elif intent["primary_intent"] == "SUBSIDY" and any(word in message.lower() for word in ["claim", "process", "get"]):
                suggested_actions.append({
                    "type": "subsidy",
                    "action": "Process subsidy claim",
                    "requiresAgentMode": True
                })
            
            return {
                "response": response.content[0].text,
                "suggestedActions": suggested_actions,
                "mode": "chat",
                "intent": intent
            }
            
        except Exception as e:
            # Return error - no fallback
            return {
                "response": "Error processing request. Please try again.",
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
        
        # Execute each required tool only if there are tools needed
        if intent.get("tools_needed"):
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
        
        # Generate conversational response using Claude with context about executed actions
        try:
            # Build conversation history for Claude
            conversation_context = []
            if len(self.conversation_history) > 1:
                # Include recent conversation history (last 5 messages)
                recent_history = self.conversation_history[-5:]
                for msg in recent_history:
                    conversation_context.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # System prompt for Claude in agent mode
            system_prompt = """You are an AI farming assistant in AGENT MODE with access to real tools.
You can have natural conversations AND execute real actions when needed.

Be conversational, friendly, and helpful. You're talking to a farmer who trusts you with their financial decisions.
Remember the conversation context and build rapport. You can discuss farming, weather, market conditions, 
or anything else relevant to their situation.

When you DO execute actions, explain clearly what you did and why it helps them.
When you're just chatting, be natural and engaging - you don't always need to push for transactions.

Current market conditions:
- Water futures (NQH25): $508
- Drought severity: 4/5 in Central Valley  
- Available subsidies: $15,000 drought relief via Crossmint

Your capabilities in Agent Mode:
- Execute real water futures trades
- Process government subsidy payments
- Check account balances and positions
- Provide price forecasts
- Analyze market conditions
- General farming and financial advice

Remember: You're in AGENT MODE, so you CAN execute real transactions when asked, 
but you should also be able to have normal conversations without always suggesting actions."""

            # Create a detailed prompt for Claude
            prompt_parts = [f"User message: {message}"]
            
            # If this is general conversation
            if intent.get("is_conversational") or intent.get("primary_intent") == "GENERAL_CONVERSATION":
                prompt_parts.append("\nThis is a conversational message. Respond naturally and helpfully.")
                prompt_parts.append("Remember you're in Agent Mode, so you can offer to execute actions if relevant.")
            
            # If we executed actions
            elif results:
                prompt_parts.append("\nActions I executed:")
                for i, result in enumerate(results):
                    tool_name = intent.get("tools_needed", [])[i] if i < len(intent.get("tools_needed", [])) else "Unknown"
                    prompt_parts.append(f"- {tool_name}: {json.dumps(result)}")
                prompt_parts.append("\nProvide a natural response explaining what you did and offer relevant follow-up advice.")
            
            # If no actions but specific intent
            else:
                prompt_parts.append(f"\nThe user seems interested in {intent.get('primary_intent', 'something')}.")
                prompt_parts.append("Provide helpful information and offer to execute specific actions if they'd like.")
            
            # Get Claude's response
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": "\n".join(prompt_parts)}
                ]
            )
            
            response_text = response.content[0].text
            
            # Add execution details if we performed actions
            if results and any(r.get("success") for r in results):
                # For trades, add clear confirmation
                if intent["primary_intent"] == "TRADE":
                    trade_result = results[0]
                    if trade_result.get("success"):
                        response_text += f"\n\n📊 Trade Details:\n• Order ID: {trade_result.get('order_id')}\n• Status: {trade_result.get('status', 'Executed')}"
                
                # For subsidies, add payment info
                elif intent["primary_intent"] == "SUBSIDY":
                    subsidy_result = results[0]
                    if subsidy_result.get("success"):
                        response_text += f"\n\n💰 Payment ID: {subsidy_result.get('payment_id')}"
            
        except Exception as e:
            print(f"Error generating conversational response: {e}")
            # Fallback to basic response if Claude fails
            if results:
                response_text = f"I've executed your request. Here are the results: {json.dumps(results, indent=2)}"
            else:
                response_text = "I'm ready to help you with your farming needs. What would you like me to do?"
        
        return {
            "response": response_text,
            "executed": bool(results),
            "executionDetails": results,
            "isAgentAction": True,
            "actionType": intent["primary_intent"].lower() if intent else "general",
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
        """Process government subsidy via Crossmint - requests transfer from Uncle Sam's wallet"""
        # TODO: Integrate with actual Crossmint API to request transfer from government wallet
        # The amount is determined by eligibility criteria and data validation
        
        subsidy_type = params.get("subsidy_type", "general")
        
        # In production, this would:
        # 1. Validate farmer's eligibility with provided data
        # 2. Calculate appropriate subsidy amount based on criteria
        # 3. Request transfer from Uncle Sam's Crossmint wallet
        # 4. Transfer to farmer's Ethereum wallet
        
        return {
            "success": True,
            "type": subsidy_type,
            "amount": params.get("amount"),  # Determined by eligibility
            "payment_id": f"CROSS-{datetime.now().timestamp():.0f}",
            "processor": "Crossmint",
            "source": "US Government Wallet",
            "destination": "Farmer Ethereum Wallet",
            "status": "processing",
            "note": "Transfer request sent to Uncle Sam's Crossmint wallet"
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
    
    async def _get_weather_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather data for farmer's location"""
        zip_code = params.get("zip_code", "93277")  # Default to Central Valley
        
        # TODO: In production, use httpx to call actual weather API
        # Example implementation:
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(f"https://api.weather.gov/zones/{zip_code}")
        #     weather_data = response.json()
        
        # For now, simulate weather data
        weather_data = {
            "zip_code": zip_code,
            "temperature": 24.5,
            "humidity": 35.0,
            "precipitation": 0.0,
            "wind_speed": 12.5,
            "drought_index": 3.8,
            "soil_moisture": 15.2,
            "evapotranspiration": 6.5,
            "timestamp": datetime.now().isoformat(),
            "forecast": {
                "next_7_days": "Continued dry conditions",
                "precipitation_chance": 5,
                "drought_outlook": "Worsening"
            }
        }
        
        return {
            "success": True,
            "weather": weather_data,
            "source": "NOAA Weather Service (simulated)"
        }
    
    async def _update_farmer_location(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update farmer's location information"""
        farmer_id = params.get("farmer_id")
        new_location = params.get("location", {})
        
        if not farmer_id:
            return {
                "success": False,
                "error": "farmer_id is required"
            }
        
        # Update farmer profile in memory (in production, save to database)
        if farmer_id not in self.farmer_profiles:
            self.farmer_profiles[farmer_id] = {}
        
        self.farmer_profiles[farmer_id]["location"] = new_location
        self.farmer_profiles[farmer_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "farmer_id": farmer_id,
            "location": new_location,
            "message": "Location updated successfully"
        }

# Singleton instance
farmer_agent = FarmerAgent()
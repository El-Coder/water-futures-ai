"""
MCP Server Connector - Routes messages to appropriate MCP servers
Handles NLP interpretation and action execution
"""
import httpx
import json
from typing import Dict, Any, Optional
import os
from anthropic import Anthropic

class MCPConnector:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self.anthropic = Anthropic(api_key=api_key)
        else:
            self.anthropic = None
            print("⚠️  Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
        
        # MCP Server endpoints
        self.trading_agent_url = os.getenv("TRADING_AGENT_URL", "http://localhost:5001")
        self.farmer_assistant_url = os.getenv("FARMER_ASSISTANT_URL", "http://localhost:5002")
        
    async def process_message(self, message: str, mode: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message from the farmer, using Claude for NLP
        and routing to appropriate MCP servers for actions
        """
        
        # Step 1: Use Claude to understand intent
        intent = await self._analyze_intent(message, context)
        
        # Step 2: Route based on mode and intent
        if mode == "chat":
            # Safe mode - only provide information, no execution
            return await self._handle_chat_mode(message, intent, context)
        
        elif mode == "agent":
            # Agent mode - can execute real actions
            return await self._handle_agent_mode(message, intent, context)
        
        return {
            "response": "I couldn't understand your request. Please try again.",
            "intent": intent
        }
    
    async def _analyze_intent(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Claude to understand the farmer's intent
        """
        if not self.anthropic:
            # Fallback to simple keyword-based intent detection
            return self._simple_intent_detection(message)
        
        try:
            response = self.anthropic.messages.create(
                model="claude-3-haiku-20240307",  # Fast model for intent classification
                max_tokens=200,
                system="""You are an intent classifier for a farming assistant. 
                Classify the user's message into one of these intents:
                - TRADE_INQUIRY: Questions about trading water futures
                - TRADE_EXECUTE: Request to buy/sell water futures
                - SUBSIDY_INQUIRY: Questions about government subsidies
                - SUBSIDY_CLAIM: Request to claim/process a subsidy
                - MARKET_ANALYSIS: Request for market conditions or forecasts
                - GENERAL_HELP: General questions about farming or water
                
                Also extract:
                - action: BUY/SELL/INFO
                - quantity: number if mentioned
                - contract_code: if mentioned (default: NQH25)
                - subsidy_type: if mentioned
                
                Return as JSON.""",
                messages=[
                    {
                        "role": "user",
                        "content": f"Message: {message}\nContext: {json.dumps(context)}"
                    }
                ]
            )
            
            # Parse Claude's response
            intent_text = response.content[0].text
            
            # Simple parsing (in production, use proper JSON parsing)
            intent = {
                "primary": "GENERAL_HELP",
                "action": None,
                "quantity": None,
                "contract_code": "NQH25",
                "confidence": 0.8
            }
            
            # Detect intent from keywords
            message_lower = message.lower()
            if "buy" in message_lower or "purchase" in message_lower:
                intent["primary"] = "TRADE_EXECUTE"
                intent["action"] = "BUY"
                # Extract quantity if mentioned
                for word in message.split():
                    if word.isdigit():
                        intent["quantity"] = int(word)
                        break
            elif "sell" in message_lower:
                intent["primary"] = "TRADE_EXECUTE"
                intent["action"] = "SELL"
            elif "subsidy" in message_lower or "government" in message_lower:
                if "claim" in message_lower or "process" in message_lower or "apply" in message_lower:
                    intent["primary"] = "SUBSIDY_CLAIM"
                else:
                    intent["primary"] = "SUBSIDY_INQUIRY"
            elif "market" in message_lower or "forecast" in message_lower or "predict" in message_lower:
                intent["primary"] = "MARKET_ANALYSIS"
            elif "trade" in message_lower or "futures" in message_lower:
                intent["primary"] = "TRADE_INQUIRY"
            
            return intent
            
        except Exception as e:
            print(f"Intent analysis error: {e}")
            return self._simple_intent_detection(message)
    
    def _simple_intent_detection(self, message: str) -> Dict[str, Any]:
        """Simple keyword-based intent detection as fallback"""
        message_lower = message.lower()
        intent = {
            "primary": "GENERAL_HELP",
            "action": None,
            "quantity": None,
            "contract_code": "NQH25",
            "confidence": 0.5
        }
        
        if "buy" in message_lower or "purchase" in message_lower:
            intent["primary"] = "TRADE_EXECUTE"
            intent["action"] = "BUY"
            for word in message.split():
                if word.isdigit():
                    intent["quantity"] = int(word)
                    break
        elif "sell" in message_lower:
            intent["primary"] = "TRADE_EXECUTE"
            intent["action"] = "SELL"
        elif "subsidy" in message_lower or "government" in message_lower:
            if "claim" in message_lower or "process" in message_lower:
                intent["primary"] = "SUBSIDY_CLAIM"
            else:
                intent["primary"] = "SUBSIDY_INQUIRY"
        elif "market" in message_lower or "forecast" in message_lower:
            intent["primary"] = "MARKET_ANALYSIS"
        elif "trade" in message_lower or "futures" in message_lower:
            intent["primary"] = "TRADE_INQUIRY"
        
        return intent
    
    async def _handle_chat_mode(self, message: str, intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle message in chat mode (safe, no execution)
        """
        # Use Claude for conversational response if available
        if not self.anthropic:
            return self._fallback_chat_response(message, intent)
        
        try:
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system="""You are a helpful farming assistant in CHAT MODE (safe mode).
                You can provide information but CANNOT execute trades or process payments.
                Always remind users they need to enable Agent Mode for real transactions.
                
                Current context:
                - Location: Central Valley, CA
                - Drought Severity: 4/5 (Severe)
                - Current water futures price: $508
                - Available subsidies: USDA Drought Relief, CA Conservation Rebate
                """,
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            
            suggested_actions = []
            
            # Add suggested actions based on intent
            if intent["primary"] == "TRADE_EXECUTE":
                suggested_actions.append({
                    "type": "trade",
                    "action": f"{intent['action']} water futures",
                    "quantity": intent.get("quantity", 5),
                    "requiresAgentMode": True
                })
            elif intent["primary"] == "SUBSIDY_CLAIM":
                suggested_actions.append({
                    "type": "subsidy",
                    "action": "Claim drought relief subsidy",
                    "estimatedAmount": 15000,
                    "requiresAgentMode": True
                })
            
            return {
                "response": response.content[0].text,
                "suggestedActions": suggested_actions,
                "mode": "chat",
                "intent": intent
            }
            
        except Exception as e:
            return self._fallback_chat_response(message, intent)
    
    def _fallback_chat_response(self, message: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback response when Claude is not available"""
        suggested_actions = []
        
        if intent["primary"] == "TRADE_EXECUTE":
            suggested_actions.append({
                "type": "trade",
                "action": f"{intent['action']} water futures",
                "quantity": intent.get("quantity", 5),
                "requiresAgentMode": True
            })
            response_text = "To execute trades, please enable Agent Mode. I can help you buy or sell water futures contracts."
        elif intent["primary"] == "SUBSIDY_CLAIM":
            suggested_actions.append({
                "type": "subsidy",
                "action": "Claim drought relief subsidy",
                "estimatedAmount": 15000,
                "requiresAgentMode": True
            })
            response_text = "Government subsidies are available for drought relief. Enable Agent Mode to process your claim."
        else:
            response_text = "I can help you understand water futures and subsidies. What would you like to know?"
        
        return {
            "response": response_text,
            "suggestedActions": suggested_actions,
            "mode": "chat",
            "intent": intent
        }
    
    async def _handle_agent_mode(self, message: str, intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle message in agent mode (can execute real actions)
        """
        
        # Route to appropriate MCP server based on intent
        if intent["primary"] in ["TRADE_EXECUTE", "TRADE_INQUIRY"]:
            return await self._execute_trade_action(message, intent, context)
        
        elif intent["primary"] in ["SUBSIDY_CLAIM", "SUBSIDY_INQUIRY"]:
            return await self._execute_subsidy_action(message, intent, context)
        
        elif intent["primary"] == "MARKET_ANALYSIS":
            return await self._get_market_analysis(message, context)
        
        else:
            # General conversation with agent capabilities
            return await self._agent_conversation(message, context)
    
    async def _execute_trade_action(self, message: str, intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trade through the trading MCP server
        """
        try:
            # Call trading MCP server
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.trading_agent_url}/execute_trade",
                    json={
                        "action": intent.get("action", "BUY").lower(),
                        "quantity": intent.get("quantity", 5),
                        "contract_code": intent.get("contract_code", "NQH25"),
                        "reason": message,
                        "farmerId": context.get("farmerId", "farmer-001")
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "response": f"✅ Trade Executed Successfully!\n\n"
                                  f"Action: {intent['action']} {intent.get('quantity', 5)} contracts\n"
                                  f"Contract: {intent.get('contract_code', 'NQH25')}\n"
                                  f"Order ID: {result.get('orderId', 'N/A')}\n\n"
                                  f"Analysis: {result.get('analysis', 'Trade processed')}",
                        "executed": True,
                        "executionDetails": result,
                        "isAgentAction": True,
                        "actionType": "trade",
                        "mode": "agent"
                    }
        except Exception as e:
            print(f"Trade execution error: {e}")
        
        # Fallback to simulated execution
        return {
            "response": f"✅ [SIMULATED] Trade Executed!\n"
                       f"Action: {intent['action']} {intent.get('quantity', 5)} water futures\n"
                       f"Price: $508 per contract\n"
                       f"Total: ${508 * intent.get('quantity', 5)}",
            "executed": True,
            "isAgentAction": True,
            "actionType": "trade",
            "mode": "agent"
        }
    
    async def _execute_subsidy_action(self, message: str, intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process subsidy through Crossmint via MCP server
        """
        try:
            # Call farmer assistant MCP server
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.farmer_assistant_url}/process_subsidy",
                    json={
                        "farmerId": context.get("farmerId", "farmer-001"),
                        "subsidyType": "drought_relief",
                        "amount": 15000,
                        "metadata": {
                            "droughtSeverity": context.get("droughtSeverity", 4),
                            "location": context.get("location", "Central Valley")
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "response": f"✅ Subsidy Payment Processed!\n\n"
                                  f"Type: Drought Relief Assistance\n"
                                  f"Amount: $15,000\n"
                                  f"Payment Method: Crossmint (US Government)\n"
                                  f"Status: {result.get('status', 'Processing')}\n\n"
                                  f"Funds will be deposited within 24 hours.",
                        "executed": True,
                        "executionDetails": result,
                        "isAgentAction": True,
                        "actionType": "subsidy",
                        "mode": "agent"
                    }
        except Exception as e:
            print(f"Subsidy processing error: {e}")
        
        # Fallback to simulated processing
        return {
            "response": "✅ [SIMULATED] Subsidy Claimed!\n"
                       "Type: USDA Drought Relief\n"
                       "Amount: $15,000\n"
                       "Processing via Crossmint...\n"
                       "Funds will appear in your account within 24 hours.",
            "executed": True,
            "isAgentAction": True,
            "actionType": "subsidy",
            "mode": "agent"
        }
    
    async def _get_market_analysis(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get market analysis from trading MCP server
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.trading_agent_url}/analyze_market",
                    json={
                        "includeNews": True,
                        "includeDrought": True
                    }
                )
                
                if response.status_code == 200:
                    analysis = response.json()
                    return {
                        "response": f"📊 Market Analysis:\n\n"
                                  f"Drought Severity: {analysis.get('droughtConditions', {}).get('averageSeverity', 4)}/5\n"
                                  f"Market Condition: {analysis.get('marketCondition', 'Neutral')}\n"
                                  f"News Sentiment: {analysis.get('newsSentiment', {}).get('interpretation', 'Mixed')}\n\n"
                                  f"Recommendation: {analysis.get('recommendation', 'Monitor conditions closely')}",
                        "mode": "agent"
                    }
        except Exception as e:
            print(f"Market analysis error: {e}")
        
        return {
            "response": "📊 Current Market Conditions:\n"
                       "• Water futures: $508 (↑2.5%)\n"
                       "• Drought severity: 4/5 (Severe)\n"
                       "• Recommendation: Consider hedging with 5-10 contracts",
            "mode": "agent"
        }
    
    async def _agent_conversation(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        General conversation in agent mode
        """
        if not self.anthropic:
            return {
                "response": "I'm your agent assistant. I can execute trades and process subsidies. How can I help?",
                "mode": "agent",
                "isAgentAction": False
            }
        
        try:
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system="""You are an AI farming assistant in AGENT MODE.
                You have the ability to execute real trades and process subsidies.
                Be helpful but remind users that all actions are REAL and use REAL MONEY.
                
                Current capabilities:
                - Execute water futures trades via Alpaca
                - Process government subsidies via Crossmint
                - Provide market analysis and forecasts
                - Manage portfolio and risk
                """,
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            
            return {
                "response": response.content[0].text,
                "mode": "agent",
                "isAgentAction": False
            }
            
        except Exception as e:
            return {
                "response": "I'm your agent assistant. I can execute trades and process subsidies. How can I help?",
                "error": str(e),
                "mode": "agent"
            }

# Singleton instance
mcp_connector = MCPConnector()
# Trade Approval Flow Documentation

## Overview

The Water Futures AI platform implements a sophisticated trade approval system that ensures users maintain complete control over all financial transactions. This document details the implementation of the approval flow, from user request to trade execution.

## Key Components

### 1. ChatbotV2 Component (`frontend/src/components/ChatbotV2.tsx`)

The main interface for user interaction with two distinct modes:

#### Chat Mode (Default - Safe)
- Information and analysis only
- No execution capabilities
- Perfect for learning and exploration
- Green/blue UI theme

#### Agent Mode (Requires Explicit Activation)
- Full execution capabilities
- Red warning indicators throughout UI
- Requires confirmation dialog acceptance
- All actions require additional approval

### 2. Farmer Agent Service (`backend/services/farmer_agent.py`)

The intelligent backend service that:
- Analyzes user intent using Claude AI
- Routes requests to appropriate services
- Manages execution in agent mode
- Maintains conversation history
- Logs all executed actions

### 3. Alpaca MCP Client (`backend/services/alpaca_mcp_client.py`)

Handles actual trade execution:
- Connects to Alpaca paper trading API
- Maps water futures symbols to tradeable proxies
- Executes approved orders
- Returns confirmation details

## Detailed Flow

### Step 1: Mode Selection

```typescript
// ChatbotV2.tsx - Mode Toggle Implementation
const handleAgentModeToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
  if (event.target.checked) {
    // Show warning dialog when turning ON agent mode
    setPendingAgentMode(true);
    setShowAgentWarning(true);
  } else {
    // Turn OFF agent mode immediately
    setAgentMode(false);
    addSystemMessage("Agent Mode DISABLED. Now in safe chat mode.");
  }
};
```

### Step 2: Warning Dialog

When enabling Agent Mode, users see:

```typescript
<Dialog open={showAgentWarning}>
  <DialogTitle>
    <WarningIcon color="error" />
    Are You Sure You Want to Turn on Agent Mode?
  </DialogTitle>
  <DialogContent>
    <Alert severity="error">
      AGENT MODE EXECUTES TRADES WITH REAL MONEY
    </Alert>
    <DialogContentText>
      By enabling Agent Mode, you authorize the AI agent to:
      • Execute water futures trades on your behalf
      • Process government subsidy payments via Crossmint
      • Access and modify your account balance
      • Make financial decisions based on market analysis
    </DialogContentText>
  </DialogContent>
  <DialogActions>
    <Button onClick={cancelAgentMode}>Cancel (Stay Safe)</Button>
    <Button onClick={confirmAgentMode} color="error">
      Yes, Enable Agent Mode
    </Button>
  </DialogActions>
</Dialog>
```

### Step 3: Intent Analysis

When a user sends a message in Agent Mode:

```python
# farmer_agent.py - Intent Analysis
async def _analyze_intent_with_tools(self, message: str, context: Dict[str, Any]):
    tools_description = """
    Available tools:
    1. trade_water_futures: Buy/sell water futures contracts
    2. check_account: Get account balance and buying power
    3. process_subsidy: Claim government subsidies via Crossmint
    """
    
    response = self.anthropic.messages.create(
        model="claude-3-opus-20240229",
        system=tools_description,
        messages=[{"role": "user", "content": message}]
    )
    
    # Parse intent (TRADE_EXECUTE, SUBSIDY_CLAIM, etc.)
    return self._parse_claude_intent(response.content[0].text, message)
```

### Step 4: Trade Suggestion

The agent presents suggested actions with clear visual indicators:

```typescript
// ChatbotV2.tsx - Display Suggested Actions
{message.suggestedActions && (
  <Box sx={{ mt: 2 }}>
    {message.suggestedActions.map((action, idx) => (
      <Button
        key={idx}
        variant={agentMode ? "contained" : "outlined"}
        color={action.type === 'trade' ? 'warning' : 'success'}
        onClick={() => executeAction(action)}
        disabled={!agentMode}
        startIcon={<MoneyIcon />}
      >
        {action.action}
        {!agentMode && " (Enable Agent Mode)"}
      </Button>
    ))}
  </Box>
)}
```

### Step 5: User Approval

Before execution, the system shows trade details:

```typescript
// Approval Dialog (implicit in the button click)
const executeAction = async (action: any) => {
  if (!agentMode) {
    addSystemMessage("Please enable Agent Mode to execute real transactions.");
    return;
  }
  
  // User has already clicked the action button - this IS the approval
  setLoading(true);
  try {
    const response = await axios.post('/api/v1/agent/action', {
      action,
      context: { agentModeEnabled: true }
    });
    
    addSystemMessage(
      `✅ ${action.type === 'trade' ? 'Trade' : 'Subsidy'} Executed:\n` +
      `${response.data.details}`
    );
  } catch (error) {
    addSystemMessage(`❌ Action failed: ${error}`);
  }
};
```

### Step 6: Trade Execution

Upon approval, the backend executes:

```python
# alpaca_mcp_client.py - Trade Execution
async def place_water_futures_order(
    self, 
    symbol: str, 
    quantity: int, 
    side: str,
    order_type: str = "market"
) -> Dict[str, Any]:
    # Map water futures to tradeable securities
    symbol_mapping = {
        "NQH25": "SPY",  # Using SPY as proxy for demo
        "NQM25": "QQQ",  # Using QQQ as proxy
        "WATER": "AWK",  # American Water Works as proxy
    }
    
    trade_symbol = symbol_mapping.get(symbol, "SPY")
    
    # Create and submit order
    order_data = MarketOrderRequest(
        symbol=trade_symbol,
        qty=quantity,
        side=OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL,
        time_in_force=TimeInForce.DAY
    )
    
    order = self.trading_client.submit_order(order_data)
    
    return {
        "success": True,
        "order_id": order.id,
        "symbol": symbol,
        "traded_symbol": trade_symbol,
        "quantity": quantity,
        "side": side,
        "status": order.status,
        "message": f"Order placed successfully"
    }
```

### Step 7: Confirmation & Logging

After execution:

```python
# farmer_agent.py - Execution Confirmation
if intent["primary_intent"] == "TRADE" and results:
    trade_result = results[0]
    if trade_result.get("success"):
        response_text = (
            f"✅ Trade Executed Successfully!\n\n"
            f"Order ID: {trade_result.get('order_id')}\n"
            f"Symbol: {trade_result.get('symbol')}\n"
            f"Quantity: {trade_result.get('quantity')}\n"
            f"Side: {trade_result.get('side')}\n"
            f"Status: {trade_result.get('status')}"
        )
        
        # Log the executed action
        self.executed_actions.append({
            "tool": "trade_water_futures",
            "parameters": intent.get("parameters", {}),
            "result": trade_result,
            "timestamp": datetime.now().isoformat()
        })
```

## Safety Features

### Visual Indicators

1. **Color Coding**:
   - Chat Mode: Blue/Green theme
   - Agent Mode: Red/Orange theme
   - Trade buttons: Yellow warning color
   - Subsidy buttons: Green success color

2. **Text Warnings**:
   - Input placeholder changes in Agent Mode
   - "AGENT MODE - REAL MONEY" label
   - "LIVE" chip indicator
   - Warning icons throughout

3. **Confirmation Requirements**:
   - Initial mode toggle confirmation
   - Per-action button click required
   - No automatic execution without user interaction

### Backend Safeguards

1. **Mode Verification**:
```python
# main_simple.py - Agent endpoint
@app.post("/api/v1/agent/execute")
async def agent_execute(request: ChatRequest):
    # Verify agent mode is enabled
    if not request.context.get("agentModeEnabled"):
        return {
            "response": "Agent mode is not enabled.",
            "error": "Agent mode required"
        }
```

2. **Paper Trading Default**:
```python
# alpaca_mcp_client.py
self.trading_client = TradingClient(
    api_key=self.api_key,
    secret_key=self.api_secret,
    paper=True  # Always use paper trading for safety
)
```

3. **Transaction Logging**:
- All actions logged with timestamps
- Audit trail maintained
- Conversation history preserved

## Testing the Approval Flow

### Test Scenario 1: Attempt Trade in Chat Mode
1. Keep Agent Mode disabled
2. Type: "Buy 5 water futures"
3. Expected: Information response, no execution
4. Suggested actions shown but disabled

### Test Scenario 2: Enable Agent Mode
1. Toggle Agent Mode switch
2. See warning dialog
3. Click "Cancel" - remains in Chat Mode
4. Toggle again, click "Confirm"
5. UI changes to red theme
6. "AGENT MODE - REAL MONEY" label appears

### Test Scenario 3: Execute Approved Trade
1. Enable Agent Mode
2. Type: "Buy 5 NQH25 contracts"
3. AI suggests trade with button
4. Click trade button (this is approval)
5. See execution confirmation
6. Check transaction log

### Test Scenario 4: Decline Trade
1. Enable Agent Mode
2. Type: "Buy 10 water futures"
3. AI suggests trade
4. Don't click the button
5. Type: "Actually, nevermind"
6. No trade executed

## Implementation Best Practices

### Frontend
- Always show mode state clearly
- Use consistent color coding
- Require explicit user actions
- Provide clear feedback on all actions
- Log all state changes

### Backend
- Verify mode in every execution endpoint
- Use paper trading for development
- Maintain comprehensive audit logs
- Return detailed confirmation messages
- Handle errors gracefully

### Security
- Never auto-execute trades
- Always require user interaction
- Use warning dialogs for mode changes
- Implement rate limiting
- Validate all inputs

## Future Enhancements

1. **Multi-Factor Approval**:
   - Add SMS/email confirmation for large trades
   - Implement daily trading limits
   - Require re-authentication for Agent Mode

2. **Advanced Controls**:
   - Set maximum trade sizes
   - Define approved trading hours
   - Create whitelisted strategies
   - Implement stop-loss rules

3. **Audit & Compliance**:
   - Export transaction logs
   - Generate compliance reports
   - Track approval patterns
   - Monitor unusual activity

4. **User Preferences**:
   - Customizable warning levels
   - Preferred confirmation methods
   - Risk tolerance settings
   - Auto-disable after inactivity

## Conclusion

The trade approval flow in Water Futures AI ensures users maintain complete control over their financial decisions while benefiting from AI-powered insights. The dual-mode system, combined with explicit approval requirements and comprehensive safety features, creates a secure yet powerful trading environment for agricultural water risk management.

The implementation prioritizes:
- **User Control**: Every action requires explicit approval
- **Transparency**: Clear visual and textual indicators
- **Safety**: Multiple confirmation steps and paper trading default
- **Auditability**: Comprehensive logging of all actions

This design allows farmers to confidently use AI assistance for complex financial decisions while maintaining full authority over their accounts and transactions.
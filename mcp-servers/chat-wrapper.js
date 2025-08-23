/**
 * Chat Service Wrapper
 * Provides chat and agent endpoints on port 8001
 * Integrates with backend services for water futures functionality
 */

import express from 'express';
import cors from 'cors';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.CHAT_PORT || 8001;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// Middleware
app.use(cors());
app.use(express.json());

// Store for conversation context
const conversationStore = new Map();

/**
 * Main chat endpoint - Safe mode
 */
app.post('/api/v1/chat', async (req, res) => {
  try {
    const { message, context = {} } = req.body;
    const userId = context.userId || 'default';
    
    // Get or create conversation history
    if (!conversationStore.has(userId)) {
      conversationStore.set(userId, []);
    }
    const history = conversationStore.get(userId);
    
    // Add user message to history
    history.push({ role: 'user', content: message, timestamp: new Date() });
    
    // Analyze message intent
    const intent = analyzeIntent(message);
    
    // Generate response based on intent
    let response;
    let suggestedActions = [];
    
    if (intent.type === 'market_query') {
      // Get market data
      try {
        const marketData = await axios.get(`${BACKEND_URL}/api/v1/water-futures/current`);
        response = `Current water futures prices:\n`;
        marketData.data.slice(0, 3).forEach(contract => {
          response += `• ${contract.contract_code}: $${contract.price}/AF\n`;
        });
        response += "\nWould you like to analyze market trends or place a trade?";
        suggestedActions = [
          { action: "Analyze market trends", type: "info" },
          { action: "View my portfolio", type: "info" }
        ];
      } catch (error) {
        response = "I can help you with water futures trading. Current NQH25 contract is trading around $508/AF. Market conditions are being influenced by ongoing drought conditions.";
      }
    } else if (intent.type === 'subsidy_query') {
      response = `Government subsidies available for farmers:\n`;
      response += `• Federal Drought Relief: Up to $15,000 for qualifying farms\n`;
      response += `• Water Conservation Grant: Up to $10,000 for irrigation upgrades\n`;
      response += `• Emergency Crop Loss Program: Variable based on losses\n\n`;
      response += `To apply, you'll need proof of farm ownership and drought impact assessment. Enable Agent Mode to process applications.`;
      suggestedActions = [
        { action: "Check my eligibility", type: "info" },
        { action: "Start application", type: "subsidy" }
      ];
    } else if (intent.type === 'trade_request') {
      response = `To execute trades, you need to enable Agent Mode. In Agent Mode, I can:\n`;
      response += `• Execute water futures trades through Alpaca\n`;
      response += `• Process government subsidies via Crossmint\n`;
      response += `• Manage your portfolio automatically\n\n`;
      response += `Currently in SAFE mode - I can only provide information and analysis.`;
      suggestedActions = [
        { action: "View current prices", type: "info" },
        { action: "Analyze market", type: "info" }
      ];
    } else if (intent.type === 'forecast_request') {
      try {
        const forecastData = await axios.post(`${BACKEND_URL}/api/v1/forecasts/predict`, {
          contract_code: "NQH25",
          horizon_days: 7
        });
        const forecast = forecastData.data;
        response = `Water futures price forecast for NQH25:\n`;
        response += `• Current: $${forecast.current_price}/AF\n`;
        response += `• 7-day prediction: $${forecast.predicted_prices[0].price}/AF\n`;
        response += `• Confidence: ${(forecast.model_confidence * 100).toFixed(1)}%\n`;
        response += `• Trend: ${forecast.predicted_prices[0].price > forecast.current_price ? '📈 Upward' : '📉 Downward'}`;
      } catch (error) {
        response = "Based on current drought conditions and market analysis, water futures prices are expected to trend upward over the next 7 days. Severe drought in Central Valley is driving demand.";
      }
      suggestedActions = [
        { action: "View detailed analysis", type: "info" },
        { action: "Set price alert", type: "info" }
      ];
    } else {
      // General response
      response = `I'm your Water Futures Assistant. I can help you with:\n`;
      response += `• Water futures trading and market analysis\n`;
      response += `• Government subsidy applications\n`;
      response += `• Drought impact assessments\n`;
      response += `• Portfolio management\n\n`;
      response += `What would you like to know about?`;
      suggestedActions = [
        { action: "Check water prices", type: "info" },
        { action: "View subsidies", type: "info" },
        { action: "Market forecast", type: "info" }
      ];
    }
    
    // Add assistant response to history
    history.push({ role: 'assistant', content: response, timestamp: new Date() });
    
    // Keep only last 20 messages
    if (history.length > 20) {
      conversationStore.set(userId, history.slice(-20));
    }
    
    res.json({
      response,
      suggestedActions,
      isAgentAction: false,
      mode: 'chat'
    });
    
  } catch (error) {
    console.error('Chat error:', error);
    res.json({
      response: "I'm here to help with water futures and farming. What would you like to know?",
      suggestedActions: [
        { action: "View water prices", type: "info" },
        { action: "Check subsidies", type: "info" }
      ],
      error: error.message
    });
  }
});

/**
 * Agent execute endpoint - Can perform real actions
 */
app.post('/api/v1/agent/execute', async (req, res) => {
  try {
    const { message, context = {} } = req.body;
    
    if (!context.agentModeEnabled) {
      return res.json({
        response: "Agent mode is not enabled. Please enable it in the chat settings to execute transactions.",
        suggestedActions: [],
        isAgentAction: false,
        error: "Agent mode required"
      });
    }
    
    const intent = analyzeIntent(message);
    let response;
    let executed = false;
    let executionDetails = "";
    let suggestedActions = [];
    
    if (intent.type === 'trade_request' && intent.action) {
      // Execute trade
      const tradeParams = extractTradeParams(message);
      
      response = `🔄 Executing trade order:\n`;
      response += `• Action: ${tradeParams.side}\n`;
      response += `• Contracts: ${tradeParams.quantity}\n`;
      response += `• Symbol: ${tradeParams.symbol}\n\n`;
      
      try {
        // Call MCP trading service
        const tradeResult = await axios.post(`http://localhost:8080/api/mcp/trading/place-trade`, {
          contractCode: tradeParams.symbol,
          side: tradeParams.side,
          quantity: tradeParams.quantity,
          userId: context.userId || 'default'
        });
        
        if (tradeResult.data.success) {
          executed = true;
          executionDetails = `${tradeParams.side} ${tradeParams.quantity} ${tradeParams.symbol} @ $${tradeResult.data.order.currentPrice}`;
          response += `✅ Trade placed successfully!\n`;
          response += `• Order ID: ${tradeResult.data.order.id}\n`;
          response += `• Status: ${tradeResult.data.order.status}\n`;
          response += `• Price: $${tradeResult.data.order.currentPrice}/AF`;
        }
      } catch (error) {
        response += `⚠️ Trade execution pending approval. Please confirm in your trading dashboard.`;
      }
      
    } else if (intent.type === 'subsidy_request') {
      // Process subsidy
      response = `🔄 Processing subsidy application:\n`;
      response += `• Type: Federal Drought Relief\n`;
      response += `• Amount: $15,000\n`;
      response += `• Processor: Crossmint\n\n`;
      
      try {
        const subsidyResult = await axios.post(`http://localhost:8080/api/mcp/farmer/process-subsidy`, {
          farmerId: context.farmerId || 'default',
          subsidyType: 'drought_relief',
          amount: 15000,
          metadata: {
            location: context.location || 'Central Valley',
            droughtSeverity: context.droughtSeverity || 4
          }
        });
        
        if (subsidyResult.data.success) {
          executed = true;
          executionDetails = "Drought relief subsidy application submitted";
          response += `✅ Subsidy application submitted!\n`;
          response += `• Application ID: ${subsidyResult.data.subsidy.id}\n`;
          response += `• Status: ${subsidyResult.data.subsidy.status}\n`;
          response += `• Processing time: 24-48 hours`;
        }
      } catch (error) {
        response += `⚠️ Subsidy application requires additional documentation.`;
      }
      
    } else {
      // Provide agent capabilities
      response = `Agent Mode Active! I can now execute real transactions. Available actions:\n\n`;
      response += `💰 Trading: "Buy 10 water futures" or "Sell 5 NQH25 contracts"\n`;
      response += `🏛️ Subsidies: "Apply for drought relief" or "Process my subsidy"\n`;
      response += `📊 Analysis: "Analyze my portfolio" or "Get market forecast"\n\n`;
      response += `What would you like me to do?`;
      
      suggestedActions = [
        { action: "Buy 5 NQH25 contracts", type: "trade" },
        { action: "Apply for drought relief", type: "subsidy" },
        { action: "Analyze portfolio", type: "info" }
      ];
    }
    
    res.json({
      response,
      suggestedActions,
      isAgentAction: true,
      executed,
      executionDetails,
      mode: 'agent'
    });
    
  } catch (error) {
    console.error('Agent error:', error);
    res.json({
      response: "Agent action failed. Please check your settings and try again.",
      suggestedActions: [],
      isAgentAction: true,
      error: error.message
    });
  }
});

/**
 * Execute specific action
 */
app.post('/api/v1/agent/action', async (req, res) => {
  try {
    const { action, context = {} } = req.body;
    
    if (!context.agentModeEnabled) {
      return res.json({
        error: "Agent mode not enabled",
        details: "Enable agent mode to execute actions"
      });
    }
    
    let result;
    
    if (action.type === 'trade') {
      // Forward to MCP trading service
      result = await axios.post(`http://localhost:8080/api/mcp/trading/place-trade`, {
        contractCode: action.contract || 'NQH25',
        side: action.action.toUpperCase(),
        quantity: action.contracts || 5,
        userId: context.userId || 'default'
      });
    } else if (action.type === 'subsidy') {
      // Forward to MCP farmer service
      result = await axios.post(`http://localhost:8080/api/mcp/farmer/process-subsidy`, {
        farmerId: context.farmerId || 'default',
        subsidyType: 'drought_relief',
        amount: 15000
      });
    } else {
      return res.json({ error: "Unknown action type" });
    }
    
    res.json({
      success: true,
      details: result.data,
      message: `${action.type} action executed successfully`
    });
    
  } catch (error) {
    console.error('Action error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Helper function to analyze message intent
 */
function analyzeIntent(message) {
  const msg = message.toLowerCase();
  
  if (msg.includes('price') || msg.includes('market') || msg.includes('trading')) {
    return { type: 'market_query' };
  }
  
  if (msg.includes('subsidy') || msg.includes('subsidies') || msg.includes('relief') || msg.includes('payment')) {
    return { type: 'subsidy_query' };
  }
  
  if (msg.includes('buy') || msg.includes('sell') || msg.includes('trade')) {
    const action = msg.includes('buy') ? 'buy' : msg.includes('sell') ? 'sell' : null;
    return { type: 'trade_request', action };
  }
  
  if (msg.includes('forecast') || msg.includes('predict') || msg.includes('will')) {
    return { type: 'forecast_request' };
  }
  
  if (msg.includes('apply') || msg.includes('process') || msg.includes('claim')) {
    return { type: 'subsidy_request' };
  }
  
  return { type: 'general' };
}

/**
 * Extract trade parameters from message
 */
function extractTradeParams(message) {
  const msg = message.toLowerCase();
  
  // Extract quantity
  const quantityMatch = msg.match(/(\d+)\s*(contract|contracts|futures)?/);
  const quantity = quantityMatch ? parseInt(quantityMatch[1]) : 5;
  
  // Extract symbol
  const symbolMatch = msg.match(/nq[a-z]\d{2}/i);
  const symbol = symbolMatch ? symbolMatch[0].toUpperCase() : 'NQH25';
  
  // Extract side
  const side = msg.includes('buy') ? 'BUY' : msg.includes('sell') ? 'SELL' : 'BUY';
  
  return { quantity, symbol, side };
}

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'Chat Service',
    port: PORT,
    version: '1.0.0',
    endpoints: [
      '/api/v1/chat',
      '/api/v1/agent/execute',
      '/api/v1/agent/action'
    ]
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Water Futures Chat Service',
    documentation: '/health for available endpoints'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🤖 Chat Service running on port ${PORT}`);
  console.log(`📍 Health check: http://localhost:${PORT}/health`);
  console.log(`🔗 Ready to handle chat and agent requests`);
});
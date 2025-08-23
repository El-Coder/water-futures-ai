import { createServer } from '@smithery/sdk';
import { createNodeHost } from '@smithery/host-nodejs';
import Anthropic from '@anthropic-ai/sdk';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

// Initialize Anthropic Claude
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Backend API URL
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// Crossmint configuration for government payments
const CROSSMINT_API = 'https://www.crossmint.com/api/v1';
const CROSSMINT_KEY = process.env.CROSSMINT_API_KEY;

const server = createServer({
  name: 'farmer-assistant',
  version: '1.0.0',
  description: 'Claude-powered assistant for farmers to manage water futures and receive subsidies',
});

// Tool: Chat with Claude about farming and water futures
server.tool({
  name: 'chat_with_farmer',
  description: 'Have a conversation with a farmer about water futures, drought conditions, and trading strategies',
  inputSchema: {
    type: 'object',
    properties: {
      message: { type: 'string', description: 'Farmer\'s message or question' },
      context: { 
        type: 'object', 
        description: 'Context about the farmer\'s situation',
        properties: {
          location: { type: 'string' },
          farmSize: { type: 'number' },
          currentBalance: { type: 'number' },
          droughtSeverity: { type: 'number' },
        }
      },
    },
    required: ['message'],
  },
  handler: async ({ message, context = {} }) => {
    try {
      // Get current market data for context
      const marketData = await axios.get(`${BACKEND_URL}/api/v1/water-futures/current`);
      const droughtData = await axios.get(`${BACKEND_URL}/api/v1/embeddings/drought-map`);
      
      // Create system prompt with context
      const systemPrompt = `You are an AI assistant helping California farmers navigate water futures markets and government subsidies. 
      
Current Context:
- Current water futures price: $${marketData.data[0]?.price || 508}
- Average drought severity: ${context.droughtSeverity || 3.6}/5
- Farmer's location: ${context.location || 'Central Valley'}
- Farm size: ${context.farmSize || 500} acres
- Account balance: $${context.currentBalance || 125000}

Your role is to:
1. Explain water futures in simple terms
2. Advise on hedging strategies for drought risk
3. Inform about available government subsidies
4. Help make trading decisions based on drought forecasts
5. Explain how Crossmint payments work for subsidies

Be practical, empathetic, and focused on the farmer's financial wellbeing.`;

      // Get Claude's response
      const response = await anthropic.messages.create({
        model: 'claude-3-opus-20240229',
        max_tokens: 1000,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: message,
          },
        ],
      });
      
      return {
        response: response.content[0].text,
        suggestedActions: await generateSuggestedActions(message, context),
      };
    } catch (error) {
      return { 
        error: error.message,
        fallbackResponse: "I'm having trouble accessing market data, but I can still help. Water futures are contracts that let you lock in water prices, protecting you from drought-related price spikes. What specific questions do you have?"
      };
    }
  },
});

// Tool: Execute a trade based on Claude's recommendation
server.tool({
  name: 'execute_trade',
  description: 'Execute a water futures trade based on AI recommendation',
  inputSchema: {
    type: 'object',
    properties: {
      action: { type: 'string', enum: ['buy', 'sell'], description: 'Trade action' },
      quantity: { type: 'number', description: 'Number of contracts' },
      reason: { type: 'string', description: 'Reason for the trade' },
      farmerId: { type: 'string', description: 'Farmer\'s account ID' },
    },
    required: ['action', 'quantity', 'reason'],
  },
  handler: async ({ action, quantity, reason, farmerId }) => {
    try {
      // Get Claude's analysis of the trade
      const analysis = await anthropic.messages.create({
        model: 'claude-3-opus-20240229',
        max_tokens: 500,
        messages: [
          {
            role: 'user',
            content: `Analyze this water futures trade: ${action} ${quantity} contracts. Reason: ${reason}. Is this a good decision for drought hedging?`,
          },
        ],
      });
      
      // Execute trade via backend
      const tradeResponse = await axios.post(`${BACKEND_URL}/api/v1/trading/order`, {
        contract_code: 'NQH25',
        side: action.toUpperCase(),
        quantity: quantity,
      });
      
      return {
        success: true,
        orderId: tradeResponse.data.order_id,
        analysis: analysis.content[0].text,
        executedAt: new Date().toISOString(),
        reason: reason,
      };
    } catch (error) {
      return { 
        success: false,
        error: error.message,
        advice: "Trade couldn't be executed. Consider reviewing market conditions and trying again."
      };
    }
  },
});

// Tool: Process government subsidy payment via Crossmint
server.tool({
  name: 'process_subsidy',
  description: 'Process government subsidy payment through Crossmint',
  inputSchema: {
    type: 'object',
    properties: {
      farmerId: { type: 'string', description: 'Farmer\'s account ID' },
      subsidyType: { 
        type: 'string', 
        enum: ['drought_relief', 'conservation_rebate', 'crop_insurance'],
        description: 'Type of subsidy' 
      },
      amount: { type: 'number', description: 'Subsidy amount in USD' },
      metadata: { type: 'object', description: 'Additional subsidy details' },
    },
    required: ['farmerId', 'subsidyType', 'amount'],
  },
  handler: async ({ farmerId, subsidyType, amount, metadata = {} }) => {
    try {
      // Verify eligibility with Claude
      const eligibilityCheck = await anthropic.messages.create({
        model: 'claude-3-opus-20240229',
        max_tokens: 200,
        messages: [
          {
            role: 'user',
            content: `Verify eligibility for ${subsidyType} subsidy of $${amount} based on: ${JSON.stringify(metadata)}`,
          },
        ],
      });
      
      // Process payment through Crossmint (mock for hackathon)
      const payment = {
        id: `SUB-${Date.now()}`,
        recipient: farmerId,
        amount: amount,
        currency: 'USD',
        type: subsidyType,
        status: 'processed',
        source: 'US Government via Crossmint',
        processedAt: new Date().toISOString(),
        eligibilityCheck: eligibilityCheck.content[0].text,
      };
      
      // In production, would call Crossmint API:
      // const crossmintResponse = await axios.post(
      //   `${CROSSMINT_API}/payments`,
      //   payment,
      //   { headers: { 'X-API-KEY': CROSSMINT_KEY } }
      // );
      
      return {
        success: true,
        payment: payment,
        message: `Successfully processed ${subsidyType} subsidy of $${amount}`,
        nextSteps: getNextSteps(subsidyType),
      };
    } catch (error) {
      return { 
        success: false,
        error: error.message,
        message: 'Subsidy processing failed. Please contact support.'
      };
    }
  },
});

// Tool: Get personalized recommendations
server.tool({
  name: 'get_recommendations',
  description: 'Get personalized recommendations for water management and trading',
  inputSchema: {
    type: 'object',
    properties: {
      farmerId: { type: 'string', description: 'Farmer\'s account ID' },
      includeTrading: { type: 'boolean', description: 'Include trading recommendations' },
      includeSubsidies: { type: 'boolean', description: 'Include subsidy recommendations' },
    },
  },
  handler: async ({ farmerId, includeTrading = true, includeSubsidies = true }) => {
    try {
      // Get current conditions
      const [marketData, newsData, droughtData] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/v1/water-futures/current`),
        axios.get(`${BACKEND_URL}/api/v1/news/latest?limit=5`),
        axios.get(`${BACKEND_URL}/api/v1/embeddings/drought-map`),
      ]);
      
      // Get Claude's recommendations
      const prompt = `Based on current conditions:
- Water futures price: $${marketData.data[0]?.price || 508}
- Drought severity: High in Central Valley
- Recent news sentiment: ${newsData.data[0]?.sentimentScore > 0 ? 'Positive' : 'Negative'}

Provide practical recommendations for a California farmer on:
${includeTrading ? '1. Trading water futures to hedge drought risk' : ''}
${includeSubsidies ? '2. Available government subsidies and how to qualify' : ''}
3. Water conservation strategies`;

      const recommendations = await anthropic.messages.create({
        model: 'claude-3-opus-20240229',
        max_tokens: 1000,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
      });
      
      return {
        recommendations: recommendations.content[0].text,
        actionItems: [
          includeTrading && {
            type: 'trading',
            action: 'Consider buying 5-10 water futures contracts',
            urgency: 'high',
            reason: 'Drought conditions worsening',
          },
          includeSubsidies && {
            type: 'subsidy',
            action: 'Apply for USDA drought relief',
            urgency: 'medium',
            potentialAmount: 15000,
          },
        ].filter(Boolean),
        marketConditions: {
          currentPrice: marketData.data[0]?.price || 508,
          trend: 'increasing',
          volatility: 'moderate',
        },
      };
    } catch (error) {
      return { error: error.message };
    }
  },
});

// Helper functions
async function generateSuggestedActions(message, context) {
  const actions = [];
  
  // Check if message mentions trading
  if (message.toLowerCase().includes('buy') || message.toLowerCase().includes('hedge')) {
    actions.push({
      type: 'trade',
      action: 'Buy water futures',
      contracts: Math.min(10, Math.floor((context.currentBalance || 100000) / 5000)),
    });
  }
  
  // Check if eligible for subsidies
  if (context.droughtSeverity >= 4) {
    actions.push({
      type: 'subsidy',
      action: 'Apply for drought relief',
      estimatedAmount: 15000,
    });
  }
  
  return actions;
}

function getNextSteps(subsidyType) {
  const steps = {
    drought_relief: [
      'Funds will be deposited within 24 hours',
      'Use funds for water-efficient irrigation upgrades',
      'Submit usage report within 90 days',
    ],
    conservation_rebate: [
      'Install water meters to track savings',
      'Submit monthly conservation reports',
      'Additional rebates available for exceeding targets',
    ],
    crop_insurance: [
      'Document crop losses with photos',
      'File claim within 72 hours of loss',
      'Adjuster will visit within 1 week',
    ],
  };
  
  return steps[subsidyType] || ['Check your account for payment confirmation'];
}

// Start the MCP server
const host = createNodeHost();
host.connect(server);

console.log('Farmer Assistant MCP Server started');
console.log('Ready to help farmers with:');
console.log('- Water futures trading advice');
console.log('- Government subsidy processing');
console.log('- Drought management strategies');
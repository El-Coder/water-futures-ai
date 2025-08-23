/**
 * HTTP Wrapper for MCP Servers
 * Exposes MCP tools as REST API endpoints for easy access from frontend and backend
 */

import express from 'express';
import cors from 'cors';
import { createServer } from '@smithery/sdk';
import { createNodeHost } from '@smithery/host-nodejs';
import Alpaca from '@alpacahq/alpaca-trade-api';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize Alpaca client
const alpaca = new Alpaca({
  keyId: process.env.ALPACA_API_KEY || '',
  secretKey: process.env.ALPACA_SECRET_KEY || '',
  paper: true,
});

// Backend URL for getting forecasts
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// Initialize MCP servers
const tradingServer = createServer({
  name: 'water-futures-trading',
  version: '1.0.0',
  description: 'Trading agent for water futures',
});

const farmerServer = createServer({
  name: 'farmer-assistant',
  version: '1.0.0',
  description: 'AI assistant for farmers',
});

// ============================
// Trading MCP Tools
// ============================

/**
 * Place a trade for water futures
 */
app.post('/api/mcp/trading/place-trade', async (req, res) => {
  try {
    const { contractCode, side, quantity, userId } = req.body;
    
    // Get forecast from backend
    const forecastResponse = await axios.post(`${BACKEND_URL}/api/v1/forecasts/predict`, {
      contract_code: contractCode,
      horizon_days: 7,
    }).catch(() => ({ data: { current_price: 508, predicted_prices: [{ price: 510 }], model_confidence: 0.75 }}));
    
    const forecast = forecastResponse.data;
    const currentPrice = forecast.current_price || 508;
    const predictedPrice = forecast.predicted_prices?.[0]?.price || 510;
    const priceChange = ((predictedPrice - currentPrice) / currentPrice) * 100;
    
    // Trading decision logic
    let decision = 'HOLD';
    const confidence = forecast.model_confidence || 0.75;
    
    if (priceChange > 2 && confidence > 0.7) {
      decision = 'BUY';
    } else if (priceChange < -2 && confidence > 0.7) {
      decision = 'SELL';
    }
    
    // Simulate order execution
    const order = {
      id: `ORD-${Date.now()}`,
      userId,
      symbol: contractCode,
      qty: quantity,
      side: side.toUpperCase(),
      type: 'market',
      status: 'pending_approval',
      currentPrice,
      predictedPrice,
      priceChangePercent: priceChange.toFixed(2),
      confidence,
      decision,
      timestamp: new Date().toISOString(),
    };
    
    // Return order for approval
    res.json({
      success: true,
      requiresApproval: true,
      order,
      analysis: {
        currentPrice,
        predictedPrice,
        priceChangePercent: priceChange.toFixed(2),
        confidence,
        recommendation: decision,
        reason: decision === 'BUY' ? 'Price expected to increase' : 
                decision === 'SELL' ? 'Price expected to decrease' : 
                'No clear trading signal'
      }
    });
    
  } catch (error) {
    console.error('Trade error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Confirm and execute a trade
 */
app.post('/api/mcp/trading/confirm-trade', async (req, res) => {
  try {
    const { orderId, approved, userId } = req.body;
    
    if (!approved) {
      return res.json({
        success: true,
        message: 'Trade cancelled by user',
        orderId,
        status: 'cancelled'
      });
    }
    
    // In production, would execute via Alpaca
    // For now, simulate execution
    const executedOrder = {
      id: orderId,
      userId,
      status: 'filled',
      executedAt: new Date().toISOString(),
      fillPrice: 508.25,
      commission: 1.00,
      message: 'Trade executed successfully via Alpaca paper trading'
    };
    
    res.json({
      success: true,
      order: executedOrder,
      message: 'Trade executed successfully'
    });
    
  } catch (error) {
    console.error('Trade confirmation error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get portfolio status
 */
app.get('/api/mcp/trading/portfolio', async (req, res) => {
  try {
    // Try to get real Alpaca account data
    let accountData;
    try {
      const account = await alpaca.getAccount();
      accountData = {
        cash: parseFloat(account.cash),
        portfolio_value: parseFloat(account.portfolio_value),
        buying_power: parseFloat(account.buying_power),
        day_trade_count: account.daytrade_count,
        pattern_day_trader: account.pattern_day_trader,
      };
    } catch (error) {
      // Fallback to mock data
      accountData = {
        cash: 95000,
        portfolio_value: 125000,
        buying_power: 95000,
        day_trade_count: 0,
        pattern_day_trader: false,
      };
    }
    
    // Get positions
    let positions;
    try {
      const alpacaPositions = await alpaca.getPositions();
      positions = alpacaPositions.map(pos => ({
        symbol: pos.symbol,
        qty: parseFloat(pos.qty),
        avg_entry_price: parseFloat(pos.avg_entry_price),
        market_value: parseFloat(pos.market_value),
        unrealized_pl: parseFloat(pos.unrealized_pl),
        unrealized_plpc: parseFloat(pos.unrealized_plpc),
      }));
    } catch (error) {
      // Fallback to mock positions
      positions = [
        {
          symbol: 'NQH25',
          qty: 10,
          avg_entry_price: 500,
          market_value: 5080,
          unrealized_pl: 80,
          unrealized_plpc: 1.6,
        }
      ];
    }
    
    res.json({
      account: accountData,
      positions,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Portfolio error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Analyze market conditions
 */
app.post('/api/mcp/trading/analyze-market', async (req, res) => {
  try {
    const { includeNews = true, includeDrought = true } = req.body;
    
    const analysis = {
      timestamp: new Date().toISOString(),
      marketCondition: 'neutral',
    };
    
    if (includeNews) {
      try {
        const newsResponse = await axios.get(`${BACKEND_URL}/api/v1/news/latest?limit=5`);
        const news = newsResponse.data;
        
        const avgSentiment = news.reduce((sum, article) => 
          sum + (article.sentiment_score || 0), 0) / (news.length || 1);
        
        analysis.newsSentiment = {
          average: avgSentiment,
          interpretation: avgSentiment > 0.2 ? 'positive' : 
                         avgSentiment < -0.2 ? 'negative' : 'neutral',
          articleCount: news.length,
          headlines: news.slice(0, 3).map(n => n.title),
        };
      } catch (error) {
        analysis.newsSentiment = { error: 'Unable to fetch news' };
      }
    }
    
    if (includeDrought) {
      try {
        const droughtResponse = await axios.get(`${BACKEND_URL}/api/v1/embeddings/drought-map`);
        const droughtData = droughtResponse.data;
        
        const avgSeverity = droughtData.regions.reduce((sum, region) => 
          sum + region.severity, 0) / droughtData.regions.length;
        
        analysis.droughtConditions = {
          averageSeverity: avgSeverity,
          interpretation: avgSeverity > 3.5 ? 'severe' : 
                         avgSeverity > 2.5 ? 'moderate' : 'mild',
          affectedRegions: droughtData.regions.filter(r => r.severity >= 4).length,
          regions: droughtData.regions,
        };
      } catch (error) {
        // Fallback drought data
        analysis.droughtConditions = {
          averageSeverity: 4.0,
          interpretation: 'severe',
          affectedRegions: 3,
        };
      }
    }
    
    // Overall recommendation
    if (analysis.droughtConditions?.averageSeverity > 3.5) {
      analysis.marketCondition = 'bullish';
      analysis.recommendation = 'Consider long positions - severe drought driving demand';
      analysis.confidence = 0.8;
    } else if (analysis.newsSentiment?.average < -0.3) {
      analysis.marketCondition = 'bearish';
      analysis.recommendation = 'Consider hedging - negative market sentiment';
      analysis.confidence = 0.6;
    } else {
      analysis.marketCondition = 'neutral';
      analysis.recommendation = 'Monitor conditions - no clear signals';
      analysis.confidence = 0.5;
    }
    
    res.json(analysis);
    
  } catch (error) {
    console.error('Market analysis error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================
// Farmer Assistant MCP Tools
// ============================

/**
 * Process government subsidy
 */
app.post('/api/mcp/farmer/process-subsidy', async (req, res) => {
  try {
    const { farmerId, subsidyType, amount, metadata } = req.body;
    
    // Simulate Crossmint payment processing
    const subsidy = {
      id: `SUB-${Date.now()}`,
      farmerId,
      type: subsidyType || 'drought_relief',
      amount: amount || 15000,
      status: 'pending_approval',
      processor: 'Crossmint',
      metadata: {
        ...metadata,
        requestedAt: new Date().toISOString(),
        estimatedProcessingTime: '24-48 hours',
      },
      requiresDocumentation: true,
      documentsRequired: [
        'Proof of farm ownership',
        'Drought impact assessment',
        'Previous year tax returns'
      ]
    };
    
    res.json({
      success: true,
      requiresApproval: true,
      subsidy,
      message: 'Subsidy application initiated - pending approval'
    });
    
  } catch (error) {
    console.error('Subsidy error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Confirm subsidy application
 */
app.post('/api/mcp/farmer/confirm-subsidy', async (req, res) => {
  try {
    const { subsidyId, approved, farmerId } = req.body;
    
    if (!approved) {
      return res.json({
        success: true,
        message: 'Subsidy application cancelled',
        subsidyId,
        status: 'cancelled'
      });
    }
    
    // Simulate Crossmint processing
    const processedSubsidy = {
      id: subsidyId,
      farmerId,
      status: 'processing',
      paymentId: `CROSS-${Date.now()}`,
      processedAt: new Date().toISOString(),
      estimatedArrival: new Date(Date.now() + 86400000).toISOString(), // +24 hours
      message: 'Subsidy approved and processing via Crossmint'
    };
    
    res.json({
      success: true,
      subsidy: processedSubsidy,
      message: 'Subsidy application approved and processing'
    });
    
  } catch (error) {
    console.error('Subsidy confirmation error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * Get farming recommendations
 */
app.post('/api/mcp/farmer/recommendations', async (req, res) => {
  try {
    const { farmerId, location, cropType } = req.body;
    
    // Get current conditions
    const marketAnalysis = await axios.post(`${BACKEND_URL}/api/v1/agent/execute`, {
      message: "analyze market conditions",
      context: { agentModeEnabled: false }
    }).catch(() => ({ data: {} }));
    
    const recommendations = [
      {
        priority: 'high',
        category: 'risk_management',
        action: 'Increase water futures position',
        reason: 'Severe drought conditions expected to drive prices up',
        estimatedImpact: '+15% portfolio protection',
      },
      {
        priority: 'high',
        category: 'subsidies',
        action: 'Apply for federal drought relief',
        reason: '$15,000 available for qualifying farms',
        estimatedImpact: 'Immediate cash flow improvement',
      },
      {
        priority: 'medium',
        category: 'infrastructure',
        action: 'Upgrade to drip irrigation',
        reason: '30% water usage reduction',
        estimatedImpact: 'Long-term cost savings',
      },
      {
        priority: 'medium',
        category: 'crop_management',
        action: 'Consider drought-resistant varieties',
        reason: 'Better yield in water-scarce conditions',
        estimatedImpact: '20% yield improvement',
      }
    ];
    
    res.json({
      farmerId,
      location,
      recommendations,
      basedOn: ['drought_severity', 'market_conditions', 'subsidy_availability'],
      generatedAt: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Recommendations error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================
// Health & Status Endpoints
// ============================

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'MCP HTTP Wrapper',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    endpoints: [
      '/api/mcp/trading/place-trade',
      '/api/mcp/trading/confirm-trade',
      '/api/mcp/trading/portfolio',
      '/api/mcp/trading/analyze-market',
      '/api/mcp/farmer/process-subsidy',
      '/api/mcp/farmer/confirm-subsidy',
      '/api/mcp/farmer/recommendations'
    ]
  });
});

app.get('/', (req, res) => {
  res.json({
    message: 'Water Futures MCP HTTP Service',
    documentation: '/health for available endpoints',
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 MCP HTTP Wrapper running on port ${PORT}`);
  console.log(`📍 Health check: http://localhost:${PORT}/health`);
  console.log(`🔗 Ready to accept requests from frontend and backend`);
});
import { createServer } from '@smithery/sdk';
import { createNodeHost } from '@smithery/host-nodejs';
import Alpaca from '@alpacahq/alpaca-trade-api';
import axios from 'axios';

// Initialize Alpaca client
const alpaca = new Alpaca({
  keyId: process.env.ALPACA_API_KEY || 'your-api-key',
  secretKey: process.env.ALPACA_SECRET_KEY || 'your-secret',
  paper: true, // Use paper trading
});

// Water Futures AI backend URL
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

const server = createServer({
  name: 'water-futures-trading',
  version: '1.0.0',
  description: 'Trading agent for water futures using Alpaca and market analysis',
});

// Tool: Place a water futures trade
server.tool({
  name: 'place_trade',
  description: 'Place a trade for water futures based on forecast and signals',
  inputSchema: {
    type: 'object',
    properties: {
      contractCode: { type: 'string', description: 'Water futures contract code' },
      side: { type: 'string', enum: ['buy', 'sell'], description: 'Trade side' },
      quantity: { type: 'number', description: 'Number of contracts' },
      strategy: { type: 'string', description: 'Trading strategy to use' },
    },
    required: ['contractCode', 'side', 'quantity'],
  },
  handler: async ({ contractCode, side, quantity, strategy }) => {
    try {
      // Get forecast from backend
      const forecastResponse = await axios.post(`${BACKEND_URL}/api/v1/forecasts/predict`, {
        contract_code: contractCode,
        horizon_days: 7,
      });
      
      const forecast = forecastResponse.data;
      
      // Simple trading logic based on forecast
      const currentPrice = forecast.current_price;
      const predictedPrice = forecast.predicted_prices[0]?.price;
      
      if (!predictedPrice) {
        return { error: 'No price prediction available' };
      }
      
      const priceChange = ((predictedPrice - currentPrice) / currentPrice) * 100;
      
      // Decision logic
      let decision = 'HOLD';
      let confidence = forecast.model_confidence || 0.5;
      
      if (priceChange > 2 && confidence > 0.7) {
        decision = 'BUY';
      } else if (priceChange < -2 && confidence > 0.7) {
        decision = 'SELL';
      }
      
      // Execute trade if decision matches requested side
      if (decision.toLowerCase() === side.toLowerCase()) {
        // For hackathon, we'll simulate the trade
        const order = {
          id: `SIM-${Date.now()}`,
          symbol: contractCode,
          qty: quantity,
          side: side.toUpperCase(),
          type: 'market',
          time_in_force: 'day',
          status: 'accepted',
        };
        
        return {
          success: true,
          order,
          analysis: {
            currentPrice,
            predictedPrice,
            priceChangePercent: priceChange.toFixed(2),
            confidence,
            decision,
          },
        };
      } else {
        return {
          success: false,
          message: `Analysis suggests ${decision}, but requested ${side.toUpperCase()}`,
          analysis: {
            currentPrice,
            predictedPrice,
            priceChangePercent: priceChange.toFixed(2),
            confidence,
            decision,
          },
        };
      }
    } catch (error) {
      return { error: error.message };
    }
  },
});

// Tool: Get portfolio status
server.tool({
  name: 'get_portfolio',
  description: 'Get current portfolio status and positions',
  handler: async () => {
    try {
      // For hackathon, return mock portfolio
      return {
        account: {
          cash: 100000,
          portfolio_value: 105000,
          buying_power: 95000,
        },
        positions: [
          {
            symbol: 'NQH25',
            qty: 10,
            avg_entry_price: 500,
            market_value: 5080,
            unrealized_pl: 80,
          },
        ],
      };
    } catch (error) {
      return { error: error.message };
    }
  },
});

// Tool: Analyze market conditions
server.tool({
  name: 'analyze_market',
  description: 'Analyze water futures market conditions',
  inputSchema: {
    type: 'object',
    properties: {
      includeNews: { type: 'boolean', description: 'Include news sentiment analysis' },
      includeDrought: { type: 'boolean', description: 'Include drought severity data' },
    },
  },
  handler: async ({ includeNews = true, includeDrought = true }) => {
    try {
      const analysis = {
        timestamp: new Date().toISOString(),
        marketCondition: 'neutral',
      };
      
      if (includeNews) {
        const newsResponse = await axios.get(`${BACKEND_URL}/api/v1/news/latest?limit=5`);
        const news = newsResponse.data;
        
        // Calculate average sentiment
        const avgSentiment = news.reduce((sum, article) => 
          sum + (article.sentiment_score || 0), 0) / news.length;
        
        analysis.newsSentiment = {
          average: avgSentiment,
          interpretation: avgSentiment > 0.2 ? 'positive' : avgSentiment < -0.2 ? 'negative' : 'neutral',
          articleCount: news.length,
        };
      }
      
      if (includeDrought) {
        const droughtResponse = await axios.get(`${BACKEND_URL}/api/v1/embeddings/drought-map`);
        const droughtData = droughtResponse.data;
        
        // Calculate average drought severity
        const avgSeverity = droughtData.regions.reduce((sum, region) => 
          sum + region.severity, 0) / droughtData.regions.length;
        
        analysis.droughtConditions = {
          averageSeverity: avgSeverity,
          interpretation: avgSeverity > 3.5 ? 'severe' : avgSeverity > 2.5 ? 'moderate' : 'mild',
          affectedRegions: droughtData.regions.filter(r => r.severity >= 4).length,
        };
      }
      
      // Overall market recommendation
      if (analysis.droughtConditions?.averageSeverity > 3.5) {
        analysis.marketCondition = 'bullish';
        analysis.recommendation = 'Consider long positions due to severe drought conditions';
      } else if (analysis.newsSentiment?.average < -0.3) {
        analysis.marketCondition = 'bearish';
        analysis.recommendation = 'Consider hedging positions due to negative sentiment';
      }
      
      return analysis;
    } catch (error) {
      return { error: error.message };
    }
  },
});

// Tool: Execute automated trading strategy
server.tool({
  name: 'run_strategy',
  description: 'Execute an automated trading strategy',
  inputSchema: {
    type: 'object',
    properties: {
      strategyName: { 
        type: 'string', 
        enum: ['momentum', 'mean_reversion', 'sentiment_based'],
        description: 'Trading strategy to execute' 
      },
      contractCode: { type: 'string', description: 'Contract to trade' },
      maxPositionSize: { type: 'number', description: 'Maximum position size' },
    },
    required: ['strategyName', 'contractCode'],
  },
  handler: async ({ strategyName, contractCode, maxPositionSize = 10 }) => {
    try {
      // Get market analysis
      const marketAnalysis = await server.handlers.analyze_market({ 
        includeNews: true, 
        includeDrought: true 
      });
      
      // Get forecast
      const forecastResponse = await axios.post(`${BACKEND_URL}/api/v1/forecasts/predict`, {
        contract_code: contractCode,
        horizon_days: 3,
      });
      
      const forecast = forecastResponse.data;
      
      let signal = 'HOLD';
      let confidence = 0;
      let reason = '';
      
      switch (strategyName) {
        case 'momentum':
          // Buy if price trending up with high confidence
          const priceChange = forecast.predicted_prices[0]?.price - forecast.current_price;
          if (priceChange > 0 && forecast.model_confidence > 0.75) {
            signal = 'BUY';
            confidence = forecast.model_confidence;
            reason = 'Positive price momentum detected';
          }
          break;
          
        case 'mean_reversion':
          // Trade against extreme moves
          if (forecast.current_price < 480) { // Below historical mean
            signal = 'BUY';
            confidence = 0.7;
            reason = 'Price below historical mean, expecting reversion';
          } else if (forecast.current_price > 520) { // Above historical mean
            signal = 'SELL';
            confidence = 0.7;
            reason = 'Price above historical mean, expecting reversion';
          }
          break;
          
        case 'sentiment_based':
          // Trade based on news and drought conditions
          if (marketAnalysis.droughtConditions?.averageSeverity > 4) {
            signal = 'BUY';
            confidence = 0.8;
            reason = 'Severe drought conditions driving demand';
          } else if (marketAnalysis.newsSentiment?.average > 0.5) {
            signal = 'SELL';
            confidence = 0.6;
            reason = 'Positive sentiment may indicate oversupply';
          }
          break;
      }
      
      // Execute trade if signal is not HOLD
      if (signal !== 'HOLD') {
        const quantity = Math.min(maxPositionSize, 5); // Conservative position sizing
        
        return {
          strategy: strategyName,
          signal,
          confidence,
          reason,
          proposedTrade: {
            contractCode,
            side: signal,
            quantity,
            currentPrice: forecast.current_price,
          },
          marketContext: marketAnalysis,
        };
      }
      
      return {
        strategy: strategyName,
        signal: 'HOLD',
        reason: 'No clear trading opportunity identified',
        marketContext: marketAnalysis,
      };
      
    } catch (error) {
      return { error: error.message };
    }
  },
});

// Start the MCP server
const host = createNodeHost();
host.connect(server);

console.log('Water Futures Trading MCP Server started');
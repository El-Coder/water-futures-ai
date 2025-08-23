/**
 * MCP Client Service
 * Handles communication with MCP HTTP wrapper for trading and farmer assistance
 */

import axios from 'axios';

// MCP server URL - in production, this will be the Cloud Run URL
const MCP_URL = import.meta.env.VITE_MCP_URL || 'http://localhost:8080';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface TradeOrder {
  contractCode: string;
  side: 'buy' | 'sell';
  quantity: number;
  userId?: string;
}

export interface TradeAnalysis {
  currentPrice: number;
  predictedPrice: number;
  priceChangePercent: string;
  confidence: number;
  recommendation: string;
  reason: string;
}

export interface TradeResponse {
  success: boolean;
  requiresApproval: boolean;
  order: {
    id: string;
    symbol: string;
    qty: number;
    side: string;
    status: string;
    currentPrice: number;
    predictedPrice: number;
    confidence: number;
  };
  analysis: TradeAnalysis;
}

export interface SubsidyRequest {
  farmerId: string;
  subsidyType?: string;
  amount?: number;
  metadata?: any;
}

export interface SubsidyResponse {
  success: boolean;
  requiresApproval: boolean;
  subsidy: {
    id: string;
    farmerId: string;
    type: string;
    amount: number;
    status: string;
    processor: string;
    documentsRequired?: string[];
  };
  message: string;
}

export interface Portfolio {
  account: {
    cash: number;
    portfolio_value: number;
    buying_power: number;
    day_trade_count: number;
    pattern_day_trader: boolean;
  };
  positions: Array<{
    symbol: string;
    qty: number;
    avg_entry_price: number;
    market_value: number;
    unrealized_pl: number;
    unrealized_plpc: number;
  }>;
}

export interface MarketAnalysis {
  marketCondition: 'bullish' | 'bearish' | 'neutral';
  recommendation: string;
  confidence: number;
  droughtConditions?: {
    averageSeverity: number;
    interpretation: string;
    affectedRegions: number;
  };
  newsSentiment?: {
    average: number;
    interpretation: string;
    articleCount: number;
    headlines?: string[];
  };
}

class MCPClient {
  /**
   * Request a trade (requires approval)
   */
  async requestTrade(order: TradeOrder): Promise<TradeResponse> {
    try {
      const response = await axios.post(`${MCP_URL}/api/mcp/trading/place-trade`, {
        ...order,
        userId: this.getUserId(),
      });
      return response.data;
    } catch (error) {
      console.error('Trade request error:', error);
      throw error;
    }
  }

  /**
   * Confirm or reject a trade
   */
  async confirmTrade(orderId: string, approved: boolean): Promise<any> {
    try {
      const response = await axios.post(`${MCP_URL}/api/mcp/trading/confirm-trade`, {
        orderId,
        approved,
        userId: this.getUserId(),
      });
      return response.data;
    } catch (error) {
      console.error('Trade confirmation error:', error);
      throw error;
    }
  }

  /**
   * Get portfolio status
   */
  async getPortfolio(): Promise<Portfolio> {
    try {
      const response = await axios.get(`${MCP_URL}/api/mcp/trading/portfolio`);
      return response.data;
    } catch (error) {
      console.error('Portfolio fetch error:', error);
      // Return mock data on error
      return {
        account: {
          cash: 95000,
          portfolio_value: 125000,
          buying_power: 95000,
          day_trade_count: 0,
          pattern_day_trader: false,
        },
        positions: [
          {
            symbol: 'NQH25',
            qty: 10,
            avg_entry_price: 500,
            market_value: 5080,
            unrealized_pl: 80,
            unrealized_plpc: 1.6,
          },
        ],
      };
    }
  }

  /**
   * Analyze market conditions
   */
  async analyzeMarket(includeNews = true, includeDrought = true): Promise<MarketAnalysis> {
    try {
      const response = await axios.post(`${MCP_URL}/api/mcp/trading/analyze-market`, {
        includeNews,
        includeDrought,
      });
      return response.data;
    } catch (error) {
      console.error('Market analysis error:', error);
      // Return default analysis on error
      return {
        marketCondition: 'neutral',
        recommendation: 'Monitor conditions',
        confidence: 0.5,
      };
    }
  }

  /**
   * Request subsidy processing
   */
  async requestSubsidy(request: SubsidyRequest): Promise<SubsidyResponse> {
    try {
      const response = await axios.post(`${MCP_URL}/api/mcp/farmer/process-subsidy`, request);
      return response.data;
    } catch (error) {
      console.error('Subsidy request error:', error);
      throw error;
    }
  }

  /**
   * Confirm or reject subsidy application
   */
  async confirmSubsidy(subsidyId: string, approved: boolean): Promise<any> {
    try {
      const response = await axios.post(`${MCP_URL}/api/mcp/farmer/confirm-subsidy`, {
        subsidyId,
        approved,
        farmerId: this.getUserId(),
      });
      return response.data;
    } catch (error) {
      console.error('Subsidy confirmation error:', error);
      throw error;
    }
  }

  /**
   * Get farming recommendations
   */
  async getRecommendations(location?: string, cropType?: string): Promise<any> {
    try {
      const response = await axios.post(`${MCP_URL}/api/mcp/farmer/recommendations`, {
        farmerId: this.getUserId(),
        location,
        cropType,
      });
      return response.data;
    } catch (error) {
      console.error('Recommendations error:', error);
      return {
        recommendations: [],
        error: 'Unable to fetch recommendations',
      };
    }
  }

  /**
   * Process agent action with MCP context
   */
  async processAgentAction(action: any, context: any): Promise<any> {
    try {
      // First analyze market conditions for context
      const marketAnalysis = await this.analyzeMarket();
      
      // Then process the action through the backend
      const response = await axios.post(`${API_URL}/api/v1/agent/action`, {
        action: {
          ...action,
          marketContext: marketAnalysis,
        },
        context: {
          ...context,
          mcpAvailable: true,
          marketAnalysis,
        },
      });
      
      return response.data;
    } catch (error) {
      console.error('Agent action error:', error);
      throw error;
    }
  }

  /**
   * Get user ID from localStorage or generate one
   */
  private getUserId(): string {
    let userId = localStorage.getItem('userId');
    if (!userId) {
      userId = `USER-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('userId', userId);
    }
    return userId;
  }

  /**
   * Check MCP server health
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await axios.get(`${MCP_URL}/health`);
      return response.data.status === 'healthy';
    } catch (error) {
      console.error('MCP health check failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const mcpClient = new MCPClient();

// Export types
export type { MCPClient };
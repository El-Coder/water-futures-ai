// Water Futures Types
export interface WaterFuture {
  id: number;
  contractCode: string;
  contractMonth: string;
  price: number;
  volume: number;
  openInterest: number;
  high?: number;
  low?: number;
  open?: number;
  close?: number;
  settlementPrice?: number;
  change?: number;
  changePercent?: number;
  timestamp: string;
  createdAt: string;
  updatedAt: string;
}

export interface WaterIndex {
  id: number;
  indexName: string;
  indexValue: number;
  region: string;
  timestamp: string;
  metadata: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface HistoricalPrice {
  id: number;
  contractCode: string;
  date: string;
  open?: number;
  high?: number;
  low?: number;
  close: number;
  volume?: number;
  settlementPrice?: number;
  openInterest?: number;
}

export interface TradingSignal {
  id: number;
  contractCode: string;
  signalType: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  predictedPrice?: number;
  currentPrice?: number;
  reasoning: Record<string, any>;
  isActive: boolean;
  generatedAt: string;
}

// Embeddings Types
export interface SatelliteEmbedding {
  id: number;
  locationId: string;
  latitude: number;
  longitude: number;
  embedding?: number[];
  resolution: string;
  captureDate: string;
  metadata: Record<string, any>;
}

export interface PDFMEmbedding {
  id: number;
  locationId: string;
  latitude: number;
  longitude: number;
  populationDensity?: number;
  demographicEmbedding?: number[];
  economicIndicators: Record<string, any>;
  waterUsageEstimate?: number;
  timestamp: string;
}

export interface RegionAnalysis {
  id: number;
  regionName: string;
  county?: string;
  state: string;
  totalAreaSqkm?: number;
  agriculturalAreaSqkm?: number;
  urbanAreaSqkm?: number;
  waterSources: string[];
  droughtSeverity?: number;
  precipitationMm?: number;
  temperatureCelsius?: number;
  combinedEmbedding?: number[];
  analysisDate: string;
  predictions: Record<string, any>;
}

// News Types
export interface NewsArticle {
  id: number;
  title: string;
  url: string;
  source: string;
  author?: string;
  content?: string;
  summary?: string;
  publishedAt: string;
  relevanceScore: number;
  sentimentScore?: number;
  categories: string[];
  keywords: string[];
  locationsMentioned: string[];
  isCaliforniaRelated: boolean;
  isWaterRelated: boolean;
}

export interface MarketInsight {
  id: number;
  insightType: 'NEWS' | 'ANALYSIS' | 'ALERT';
  title: string;
  content: string;
  impactLevel?: 'HIGH' | 'MEDIUM' | 'LOW';
  affectedRegions: string[];
  priceImpactEstimate?: number;
  confidenceLevel?: number;
  sourceArticles: string[];
  generatedAt: string;
  expiresAt?: string;
}

export interface WaterEvent {
  id: number;
  eventType: string;
  title: string;
  description?: string;
  severity?: number;
  affectedCounties: string[];
  startDate: string;
  endDate?: string;
  estimatedImpact: Record<string, any>;
  dataSources: string[];
  isActive: boolean;
}

// Trading Types
export type OrderStatus = 'pending' | 'filled' | 'partially_filled' | 'cancelled' | 'rejected';
export type OrderType = 'market' | 'limit' | 'stop' | 'stop_limit';

export interface Trade {
  id: number;
  orderId: string;
  contractCode: string;
  orderType: OrderType;
  side: 'BUY' | 'SELL';
  quantity: number;
  price?: number;
  executedPrice?: number;
  status: OrderStatus;
  filledQuantity: number;
  commission: number;
  executedAt?: string;
  metadata: Record<string, any>;
}

export interface Portfolio {
  id: number;
  portfolioName: string;
  totalValue: number;
  cashBalance: number;
  positions: Record<string, any>;
  performanceMetrics: Record<string, any>;
  lastUpdated: string;
}

export interface Position {
  id: number;
  portfolioId: number;
  contractCode: string;
  quantity: number;
  averageCost: number;
  currentPrice?: number;
  unrealizedPnl?: number;
  realizedPnl: number;
  lastUpdated: string;
}

export interface TradingStrategy {
  id: number;
  strategyName: string;
  strategyType: string;
  parameters: Record<string, any>;
  isActive: boolean;
  performanceStats: Record<string, any>;
  lastSignal?: string;
  totalTrades: number;
  winRate?: number;
  averageReturn?: number;
}

// API Request/Response Types
export interface ForecastRequest {
  contractCode: string;
  horizonDays?: number;
  includeEmbeddings?: boolean;
  includeNewsSentiment?: boolean;
}

export interface ForecastResponse {
  contractCode: string;
  currentPrice: number;
  predictedPrices: Array<{
    date: string;
    price: number;
  }>;
  confidenceIntervals: {
    upper: number[];
    lower: number[];
  };
  modelConfidence: number;
  factors: Record<string, any>;
}

export interface OrderRequest {
  contractCode: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  orderType?: OrderType;
  limitPrice?: number;
  stopPrice?: number;
}

export interface OrderResponse {
  orderId: string;
  status: string;
  message: string;
}

export interface LocationRequest {
  latitude: number;
  longitude: number;
  radiusKm?: number;
}

export interface RegionAnalysisResponse {
  regionName: string;
  droughtSeverity: number;
  waterUsageEstimate: number;
  agriculturalImpact: Record<string, any>;
  recommendations: string[];
}
import axios from 'axios';
import type { 
  WaterFuture, 
  ForecastRequest, 
  ForecastResponse,
  OrderRequest,
  OrderResponse,
  NewsArticle 
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const waterFuturesAPI = {
  // Water Futures
  getCurrentPrices: async (): Promise<WaterFuture[]> => {
    const { data } = await api.get('/api/v1/water-futures/current');
    return data;
  },

  getHistoricalPrices: async (
    contractCode?: string,
    startDate?: string,
    endDate?: string
  ) => {
    const params = new URLSearchParams();
    if (contractCode) params.append('contract_code', contractCode);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const { data } = await api.get(`/api/v1/water-futures/history?${params}`);
    return data;
  },

  uploadCSV: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const { data } = await api.post('/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  },

  // Forecasts
  generateForecast: async (request: ForecastRequest): Promise<ForecastResponse> => {
    const { data } = await api.post('/api/v1/forecasts/predict', request);
    return data;
  },

  // Trading
  placeOrder: async (request: OrderRequest): Promise<OrderResponse> => {
    const { data } = await api.post('/api/v1/trading/order', request);
    return data;
  },

  // News
  getLatestNews: async (limit: number = 20): Promise<NewsArticle[]> => {
    const { data } = await api.get(`/api/v1/news/latest?limit=${limit}`);
    return data;
  },

  // Drought Map
  getDroughtMap: async () => {
    const { data } = await api.get('/api/v1/embeddings/drought-map');
    return data;
  },
};

export default waterFuturesAPI;
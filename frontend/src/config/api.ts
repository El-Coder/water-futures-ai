/**
 * API Configuration for different environments
 */

// Get environment variables with fallbacks
const isDevelopment = import.meta.env.MODE === 'development';
const isProduction = import.meta.env.MODE === 'production';

// API URLs
export const API_CONFIG = {
  // Backend API
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
  // MCP Server
  MCP_URL: import.meta.env.VITE_MCP_URL || 'http://localhost:8080',
  
  // Chat Service
  CHAT_URL: import.meta.env.VITE_CHAT_URL || 'http://localhost:8001',
  
  // Specific endpoints
  CHAT_ENDPOINT: import.meta.env.VITE_CHAT_ENDPOINT || 
    (import.meta.env.VITE_CHAT_URL ? `${import.meta.env.VITE_CHAT_URL}/api/v1/chat` : 'http://localhost:8001/api/v1/chat'),
  
  AGENT_ENDPOINT: import.meta.env.VITE_AGENT_ENDPOINT || 
    (import.meta.env.VITE_CHAT_URL ? `${import.meta.env.VITE_CHAT_URL}/api/v1/agent/execute` : 'http://localhost:8001/api/v1/agent/execute'),
  
  // Drought endpoints
  DROUGHT_CONTEXT_ENDPOINT: import.meta.env.VITE_CHAT_URL 
    ? `${import.meta.env.VITE_CHAT_URL}/api/v1/context/drought`
    : 'http://localhost:8001/api/v1/context/drought',
  
  DROUGHT_NOTIFY_ENDPOINT: import.meta.env.VITE_CHAT_URL
    ? `${import.meta.env.VITE_CHAT_URL}/api/v1/agent/notify-drought`
    : 'http://localhost:8001/api/v1/agent/notify-drought',
  
  DROUGHT_TRANSFER_ENDPOINT: import.meta.env.VITE_CHAT_URL
    ? `${import.meta.env.VITE_CHAT_URL}/api/v1/drought/execute-transfer`
    : 'http://localhost:8001/api/v1/drought/execute-transfer',
};

// Firebase configuration
export const FIREBASE_CONFIG = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyAzAisQlEUKeIHTrpGy64eSm-ZRgduMMLQ",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "water-futures-ai.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "water-futures-ai",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "water-futures-ai.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "640022295144",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:640022295144:web:3b7bb0826efb6ace0981dd",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-1PKETWJCV2"
};

// Helper function to get the correct URL based on environment
export function getApiUrl(service: 'backend' | 'mcp' | 'chat' = 'backend'): string {
  switch (service) {
    case 'backend':
      return API_CONFIG.API_URL;
    case 'mcp':
      return API_CONFIG.MCP_URL;
    case 'chat':
      return API_CONFIG.CHAT_URL;
    default:
      return API_CONFIG.API_URL;
  }
}

// Log configuration in development
if (isDevelopment) {
  console.log('API Configuration:', {
    API_URL: API_CONFIG.API_URL,
    MCP_URL: API_CONFIG.MCP_URL,
    CHAT_URL: API_CONFIG.CHAT_URL,
    MODE: import.meta.env.MODE
  });
}

export default API_CONFIG;
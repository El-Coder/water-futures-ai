/**
 * Component Tests for Water Futures AI Frontend
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';

// Components to test
import Dashboard from '../pages/Dashboard';
import Trading from '../pages/Trading';
import News from '../pages/News';
import Forecast from '../pages/Forecast';
import ChatbotV2 from '../components/ChatbotV2';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock firebase
jest.mock('../config/firebase', () => ({
  auth: {
    currentUser: { uid: 'test-user-id', email: 'test@example.com' }
  },
  db: {},
  storage: {}
}));

// Helper function to wrap component with router
const renderWithRouter = (component: React.ReactNode) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    // Mock API responses
    mockedAxios.get.mockImplementation((url) => {
      if (url.includes('/water-futures/current')) {
        return Promise.resolve({
          data: [
            { contract_code: 'NQH25', price: 508, change_percent: 2.5 },
            { contract_code: 'NQM25', price: 515, change_percent: -1.2 }
          ]
        });
      }
      if (url.includes('/news/latest')) {
        return Promise.resolve({
          data: [
            { title: 'Drought Conditions Worsen', sentiment_score: -0.3 }
          ]
        });
      }
      return Promise.resolve({ data: {} });
    });
  });

  test('renders dashboard with key metrics', async () => {
    renderWithRouter(<Dashboard />);
    
    // Check for dashboard elements
    expect(screen.getByText(/Portfolio Overview/i)).toBeInTheDocument();
    
    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/NQH25/)).toBeInTheDocument();
    });
    
    // Check for price display
    expect(screen.getByText(/508/)).toBeInTheDocument();
  });

  test('displays portfolio value correctly', async () => {
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Portfolio Value/i)).toBeInTheDocument();
    });
    
    // Check for value formatting
    const portfolioValue = screen.getByText(/\$[\d,]+\.\d{2}/);
    expect(portfolioValue).toBeInTheDocument();
  });

  test('shows drought severity indicator', async () => {
    renderWithRouter(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Drought Severity/i)).toBeInTheDocument();
    });
  });
});

describe('Trading Component', () => {
  beforeEach(() => {
    mockedAxios.post.mockResolvedValue({
      data: {
        order_id: 'ORD-123',
        status: 'pending',
        message: 'Order placed successfully'
      }
    });
  });

  test('renders trading form', () => {
    renderWithRouter(<Trading />);
    
    expect(screen.getByText(/Water Futures Trading/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Contract/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Quantity/i)).toBeInTheDocument();
    expect(screen.getByText(/Buy/i)).toBeInTheDocument();
    expect(screen.getByText(/Sell/i)).toBeInTheDocument();
  });

  test('handles buy order submission', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Trading />);
    
    // Fill out form
    const quantityInput = screen.getByLabelText(/Quantity/i);
    await user.clear(quantityInput);
    await user.type(quantityInput, '10');
    
    // Click buy button
    const buyButton = screen.getByRole('button', { name: /Place Buy Order/i });
    await user.click(buyButton);
    
    // Verify API call
    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/trading/order'),
        expect.objectContaining({
          quantity: 10,
          side: 'BUY'
        })
      );
    });
  });

  test('displays order cost calculation', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Trading />);
    
    const quantityInput = screen.getByLabelText(/Quantity/i);
    await user.clear(quantityInput);
    await user.type(quantityInput, '5');
    
    await waitFor(() => {
      expect(screen.getByText(/Estimated Cost/i)).toBeInTheDocument();
      expect(screen.getByText(/\$[\d,]+\.\d{2}/)).toBeInTheDocument();
    });
  });
});

describe('ChatbotV2 Component', () => {
  beforeEach(() => {
    mockedAxios.post.mockImplementation((url) => {
      if (url.includes('/chat')) {
        return Promise.resolve({
          data: {
            response: 'I can help you with water futures trading.',
            suggestedActions: [
              { action: 'View prices', type: 'info' }
            ]
          }
        });
      }
      return Promise.resolve({ data: {} });
    });
  });

  test('renders chat button initially', () => {
    render(<ChatbotV2 />);
    
    const chatButton = screen.getByRole('button', { name: /chat/i });
    expect(chatButton).toBeInTheDocument();
  });

  test('opens chat window when clicked', async () => {
    const user = userEvent.setup();
    render(<ChatbotV2 />);
    
    const chatButton = screen.getByRole('button', { name: /chat/i });
    await user.click(chatButton);
    
    expect(screen.getByText(/Water Futures/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ask about water futures/i)).toBeInTheDocument();
  });

  test('sends message and receives response', async () => {
    const user = userEvent.setup();
    render(<ChatbotV2 />);
    
    // Open chat
    const chatButton = screen.getByRole('button', { name: /chat/i });
    await user.click(chatButton);
    
    // Type message
    const input = screen.getByPlaceholderText(/Ask about water futures/i);
    await user.type(input, 'What are current prices?');
    
    // Send message
    const sendButton = screen.getByRole('button', { name: /send/i });
    await user.click(sendButton);
    
    // Check for response
    await waitFor(() => {
      expect(screen.getByText(/I can help you with water futures trading/i)).toBeInTheDocument();
    });
  });

  test('displays agent mode toggle', async () => {
    const user = userEvent.setup();
    render(<ChatbotV2 />);
    
    const chatButton = screen.getByRole('button', { name: /chat/i });
    await user.click(chatButton);
    
    expect(screen.getByText(/Chat Mode - Safe/i)).toBeInTheDocument();
    expect(screen.getByRole('checkbox')).toBeInTheDocument();
  });

  test('shows warning when enabling agent mode', async () => {
    const user = userEvent.setup();
    render(<ChatbotV2 />);
    
    const chatButton = screen.getByRole('button', { name: /chat/i });
    await user.click(chatButton);
    
    const toggle = screen.getByRole('checkbox');
    await user.click(toggle);
    
    // Check for warning dialog
    await waitFor(() => {
      expect(screen.getByText(/AGENT MODE EXECUTES TRADES WITH REAL MONEY/i)).toBeInTheDocument();
    });
  });
});

describe('News Component', () => {
  beforeEach(() => {
    mockedAxios.get.mockResolvedValue({
      data: [
        {
          title: 'Drought Worsens in Central Valley',
          summary: 'Conditions continue to deteriorate',
          sentiment_score: -0.4,
          source: 'Water News Daily',
          published_at: new Date().toISOString()
        },
        {
          title: 'Federal Relief Announced',
          summary: 'New subsidies for farmers',
          sentiment_score: 0.6,
          source: 'USDA',
          published_at: new Date().toISOString()
        }
      ]
    });
  });

  test('renders news articles', async () => {
    renderWithRouter(<News />);
    
    await waitFor(() => {
      expect(screen.getByText(/Drought Worsens in Central Valley/i)).toBeInTheDocument();
      expect(screen.getByText(/Federal Relief Announced/i)).toBeInTheDocument();
    });
  });

  test('displays sentiment indicators', async () => {
    renderWithRouter(<News />);
    
    await waitFor(() => {
      // Look for sentiment chips or indicators
      const sentimentElements = screen.getAllByText(/negative|positive|neutral/i);
      expect(sentimentElements.length).toBeGreaterThan(0);
    });
  });

  test('shows article sources', async () => {
    renderWithRouter(<News />);
    
    await waitFor(() => {
      expect(screen.getByText(/Water News Daily/i)).toBeInTheDocument();
      expect(screen.getByText(/USDA/i)).toBeInTheDocument();
    });
  });
});

describe('Forecast Component', () => {
  beforeEach(() => {
    mockedAxios.post.mockResolvedValue({
      data: {
        current_price: 508,
        predicted_prices: [
          { date: '2024-01-01', price: 515 },
          { date: '2024-01-02', price: 518 }
        ],
        model_confidence: 0.85,
        factors: {
          drought_impact: 0.7,
          market_sentiment: 0.3
        }
      }
    });
  });

  test('renders forecast form', () => {
    renderWithRouter(<Forecast />);
    
    expect(screen.getByText(/Price Forecast/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Contract/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Forecast Period/i)).toBeInTheDocument();
  });

  test('generates forecast on submit', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Forecast />);
    
    const generateButton = screen.getByRole('button', { name: /Generate Forecast/i });
    await user.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Current Price.*508/i)).toBeInTheDocument();
      expect(screen.getByText(/Confidence.*85%/i)).toBeInTheDocument();
    });
  });

  test('displays price predictions', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Forecast />);
    
    const generateButton = screen.getByRole('button', { name: /Generate Forecast/i });
    await user.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText(/515/)).toBeInTheDocument();
      expect(screen.getByText(/518/)).toBeInTheDocument();
    });
  });

  test('shows impact factors', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Forecast />);
    
    const generateButton = screen.getByRole('button', { name: /Generate Forecast/i });
    await user.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Drought Impact/i)).toBeInTheDocument();
      expect(screen.getByText(/Market Sentiment/i)).toBeInTheDocument();
    });
  });
});
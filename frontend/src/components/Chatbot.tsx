import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  List,
  ListItem,
  Fab,
  Collapse,
  Avatar,
  Chip,
  Button,
  CircularProgress,
} from '@mui/material';
import {
  Send as SendIcon,
  Chat as ChatIcon,
  Close as CloseIcon,
  Agriculture as AgricultureIcon,
  SmartToy as BotIcon,
} from '@mui/icons-material';
import axios from 'axios';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  suggestedActions?: any[];
}

const Chatbot: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi! I'm your Water Futures Assistant. I can help you with trading strategies, government subsidies, and drought management. What would you like to know?",
      sender: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Call MCP server through backend
      const response = await axios.post('http://localhost:8000/api/v1/chat', {
        message: input,
        context: {
          location: 'Central Valley',
          farmSize: 500,
          currentBalance: 125000,
          droughtSeverity: 4,
        },
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.response || "I can help you understand water futures markets. They're financial contracts that help you hedge against water price increases during droughts.",
        sender: 'assistant',
        timestamp: new Date(),
        suggestedActions: response.data.suggestedActions,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      // Fallback response if MCP server is not available
      const fallbackMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: getSmartResponse(input),
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, fallbackMessage]);
    } finally {
      setLoading(false);
    }
  };

  const getSmartResponse = (message: string): string => {
    const msg = message.toLowerCase();
    
    if (msg.includes('subsidy') || msg.includes('government')) {
      return "You may be eligible for several government subsidies:\n\n" +
        "1. **USDA Drought Relief**: Up to $15,000 for farms in severe drought areas\n" +
        "2. **Water Conservation Rebate**: $0.16 per gallon saved\n" +
        "3. **Crop Insurance**: Automatic payouts when yields drop below 70%\n\n" +
        "These payments are processed automatically through Crossmint when you qualify.";
    }
    
    if (msg.includes('trade') || msg.includes('buy') || msg.includes('hedge')) {
      return "Based on current drought conditions (severity 4/5), I recommend:\n\n" +
        "• **Buy 5-10 water futures contracts** to hedge against price increases\n" +
        "• Current price: $508 per contract\n" +
        "• Expected price in drought: $520-530\n\n" +
        "This protects you from water cost increases while limiting downside risk.";
    }
    
    if (msg.includes('drought') || msg.includes('water')) {
      return "Current drought conditions in Central Valley:\n\n" +
        "• Severity: 4/5 (Severe)\n" +
        "• Precipitation: 65% below average\n" +
        "• Water allocation: Reduced to 20% of normal\n\n" +
        "Consider both water futures hedging and applying for drought relief subsidies.";
    }
    
    return "I can help you with:\n" +
      "• Trading water futures to protect against price increases\n" +
      "• Understanding government subsidies you qualify for\n" +
      "• Analyzing drought impact on your farm\n" +
      "• Making data-driven water management decisions\n\n" +
      "What would you like to know more about?";
  };

  const handleQuickAction = (action: string) => {
    setInput(action);
  };

  const executeTradeAction = async (action: any) => {
    try {
      const response = await axios.post('http://localhost:8000/api/v1/trading/order', {
        contract_code: 'NQH25',
        side: action.action === 'Buy water futures' ? 'BUY' : 'SELL',
        quantity: action.contracts || 5,
      });
      
      const confirmMessage: Message = {
        id: Date.now().toString(),
        text: `✅ Trade executed: ${action.action} - ${action.contracts} contracts`,
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, confirmMessage]);
    } catch (error) {
      console.error('Trade execution failed:', error);
    }
  };

  return (
    <>
      {/* Chat Button */}
      {!open && (
        <Fab
          color="primary"
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
            zIndex: 1000,
          }}
          onClick={() => setOpen(true)}
        >
          <ChatIcon />
        </Fab>
      )}

      {/* Chat Window */}
      <Collapse in={open}>
        <Paper
          elevation={8}
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
            width: 380,
            height: 600,
            display: 'flex',
            flexDirection: 'column',
            zIndex: 1000,
          }}
        >
          {/* Header */}
          <Box
            sx={{
              p: 2,
              bgcolor: 'primary.main',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box display="flex" alignItems="center">
              <AgricultureIcon sx={{ mr: 1 }} />
              <Typography variant="h6">Water Futures Assistant</Typography>
            </Box>
            <IconButton size="small" onClick={() => setOpen(false)} sx={{ color: 'white' }}>
              <CloseIcon />
            </IconButton>
          </Box>

          {/* Messages */}
          <List
            sx={{
              flex: 1,
              overflow: 'auto',
              p: 2,
              bgcolor: 'grey.50',
            }}
          >
            {messages.map((message) => (
              <ListItem
                key={message.id}
                sx={{
                  flexDirection: 'column',
                  alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2,
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor: message.sender === 'user' ? 'secondary.main' : 'primary.main',
                      mx: 1,
                    }}
                  >
                    {message.sender === 'user' ? 'F' : <BotIcon />}
                  </Avatar>
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      bgcolor: message.sender === 'user' ? 'primary.light' : 'white',
                      color: message.sender === 'user' ? 'white' : 'text.primary',
                    }}
                  >
                    <Typography variant="body2" style={{ whiteSpace: 'pre-line' }}>
                      {message.text}
                    </Typography>
                    {message.suggestedActions && (
                      <Box sx={{ mt: 2 }}>
                        {message.suggestedActions.map((action, idx) => (
                          <Button
                            key={idx}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 1, mt: 1 }}
                            onClick={() => executeTradeAction(action)}
                          >
                            {action.action}
                          </Button>
                        ))}
                      </Box>
                    )}
                  </Paper>
                </Box>
              </ListItem>
            ))}
            {loading && (
              <ListItem sx={{ justifyContent: 'center' }}>
                <CircularProgress size={24} />
              </ListItem>
            )}
            <div ref={messagesEndRef} />
          </List>

          {/* Quick Actions */}
          <Box sx={{ px: 2, py: 1, bgcolor: 'grey.100' }}>
            <Chip
              label="Check subsidies"
              size="small"
              onClick={() => handleQuickAction("What government subsidies am I eligible for?")}
              sx={{ mr: 1 }}
            />
            <Chip
              label="Trading advice"
              size="small"
              onClick={() => handleQuickAction("Should I buy water futures now?")}
              sx={{ mr: 1 }}
            />
            <Chip
              label="Drought status"
              size="small"
              onClick={() => handleQuickAction("What's the current drought situation?")}
            />
          </Box>

          {/* Input */}
          <Box sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask about water futures, subsidies..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !loading) {
                  sendMessage();
                }
              }}
              size="small"
              disabled={loading}
            />
            <IconButton
              color="primary"
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              sx={{ ml: 1 }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Collapse>
    </>
  );
};

export default Chatbot;
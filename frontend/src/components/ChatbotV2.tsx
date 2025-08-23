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
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Alert,
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  Chat as ChatIcon,
  Close as CloseIcon,
  Agriculture as AgricultureIcon,
  SmartToy as BotIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  MonetizationOn as MoneyIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { mcpClient } from '../services/mcp-client';
import { API_CONFIG } from '../config/api';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
  suggestedActions?: any[];
  isAgentAction?: boolean;
  actionType?: 'trade' | 'subsidy' | 'info';
}

const ChatbotV2: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi! I'm your Water Futures Assistant. I'm currently in CHAT MODE (safe). Switch to AGENT MODE to enable real trading and subsidy processing.",
      sender: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [agentMode, setAgentMode] = useState(false);
  const [showAgentWarning, setShowAgentWarning] = useState(false);
  const [pendingAgentMode, setPendingAgentMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleAgentModeToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      // Show warning dialog when turning ON agent mode
      setPendingAgentMode(true);
      setShowAgentWarning(true);
    } else {
      // Turn OFF agent mode immediately
      setAgentMode(false);
      addSystemMessage("Agent Mode DISABLED. Now in safe chat mode - no real transactions will be executed.");
    }
  };

  const confirmAgentMode = () => {
    setAgentMode(true);
    setPendingAgentMode(false);
    setShowAgentWarning(false);
    addSystemMessage(
      "⚠️ AGENT MODE ACTIVE ⚠️\n\n" +
      "The AI agent can now:\n" +
      "• Execute REAL water futures trades\n" +
      "• Process government subsidy payments via Crossmint\n" +
      "• Access your account balance\n\n" +
      "All actions will be logged. Trade carefully!"
    );
  };

  const cancelAgentMode = () => {
    setPendingAgentMode(false);
    setShowAgentWarning(false);
  };

  const addSystemMessage = (text: string) => {
    const systemMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'assistant',
      timestamp: new Date(),
      isAgentAction: true,
    };
    setMessages((prev) => [...prev, systemMessage]);
  };

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
      // Determine which endpoint to use based on mode
      const endpoint = agentMode 
        ? API_CONFIG.AGENT_ENDPOINT
        : API_CONFIG.CHAT_ENDPOINT;

      const response = await axios.post(endpoint, {
        message: input,
        mode: agentMode ? 'agent' : 'chat',
        context: {
          location: 'Central Valley',
          farmSize: 500,
          currentBalance: 125000,
          droughtSeverity: 4,
          agentModeEnabled: agentMode,
        },
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        sender: 'assistant',
        timestamp: new Date(),
        suggestedActions: response.data.suggestedActions,
        isAgentAction: response.data.isAgentAction,
        actionType: response.data.actionType,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // If agent executed an action, show confirmation
      if (response.data.executed && agentMode) {
        const confirmationMessage: Message = {
          id: (Date.now() + 2).toString(),
          text: `✅ Action Executed: ${response.data.executionDetails}`,
          sender: 'assistant',
          timestamp: new Date(),
          isAgentAction: true,
        };
        setMessages((prev) => [...prev, confirmationMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: agentMode 
          ? "Agent action failed. Please check your connection to MCP servers."
          : "I'm having trouble connecting. Let me provide you with general information instead.",
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const executeAction = async (action: any) => {
    if (!agentMode) {
      addSystemMessage("Please enable Agent Mode to execute real transactions.");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_CONFIG.CHAT_URL}/api/v1/agent/action`, {
        action,
        context: {
          agentModeEnabled: true,
        },
      });

      addSystemMessage(
        `✅ ${action.type === 'trade' ? 'Trade' : 'Subsidy'} Executed:\n` +
        `${response.data.details}`
      );
    } catch (error) {
      addSystemMessage(`❌ Action failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = (action: string) => {
    setInput(action);
  };

  return (
    <>
      {/* Chat Button */}
      {!open && (
        <Fab
          color="secondary"
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 9999,
            bgcolor: '#1976D2',
            color: 'white',
            '&:hover': {
              bgcolor: '#1565C0',
            },
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
            width: 420,
            height: 650,
            display: 'flex',
            flexDirection: 'column',
            zIndex: 1000,
          }}
        >
          {/* Header */}
          <Box
            sx={{
              p: 2,
              bgcolor: agentMode ? 'error.dark' : 'primary.main',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box display="flex" alignItems="center">
              <AgricultureIcon sx={{ mr: 1 }} />
              <Typography variant="h6">
                Water Futures {agentMode ? 'AGENT' : 'Assistant'}
              </Typography>
            </Box>
            <IconButton size="small" onClick={() => setOpen(false)} sx={{ color: 'white' }}>
              <CloseIcon />
            </IconButton>
          </Box>

          {/* Mode Toggle */}
          <Box
            sx={{
              px: 2,
              py: 1,
              bgcolor: agentMode ? 'error.light' : 'grey.100',
              color: agentMode ? 'white' : 'text.primary',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <FormControlLabel
              control={
                <Switch
                  checked={agentMode}
                  onChange={handleAgentModeToggle}
                  color={agentMode ? 'warning' : 'primary'}
                />
              }
              label={
                <Box display="flex" alignItems="center">
                  {agentMode ? (
                    <>
                      <WarningIcon sx={{ mr: 0.5, fontSize: 18 }} />
                      AGENT MODE - REAL MONEY
                    </>
                  ) : (
                    <>
                      <ChatIcon sx={{ mr: 0.5, fontSize: 18 }} />
                      Chat Mode - Safe
                    </>
                  )}
                </Box>
              }
            />
            {agentMode && (
              <Chip
                label="LIVE"
                color="error"
                size="small"
                icon={<MoneyIcon />}
              />
            )}
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
                      bgcolor: message.sender === 'user' 
                        ? 'secondary.main' 
                        : message.isAgentAction 
                          ? 'error.main' 
                          : 'primary.main',
                      mx: 1,
                    }}
                  >
                    {message.sender === 'user' ? 'F' : <BotIcon />}
                  </Avatar>
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '75%',
                      bgcolor: message.sender === 'user' 
                        ? 'primary.light' 
                        : message.isAgentAction
                          ? 'error.light'
                          : 'white',
                      color: message.sender === 'user' || message.isAgentAction
                        ? 'white' 
                        : 'text.primary',
                      border: message.isAgentAction ? '2px solid' : 'none',
                      borderColor: 'error.main',
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
                            variant={agentMode ? "contained" : "outlined"}
                            color={action.type === 'trade' ? 'warning' : 'success'}
                            sx={{ mr: 1, mt: 1 }}
                            onClick={() => executeAction(action)}
                            disabled={!agentMode}
                            startIcon={action.type === 'trade' ? <MoneyIcon /> : <CheckCircleIcon />}
                          >
                            {action.action}
                            {!agentMode && " (Enable Agent Mode)"}
                          </Button>
                        ))}
                      </Box>
                    )}
                  </Paper>
                </Box>
                {message.isAgentAction && (
                  <Typography variant="caption" sx={{ mt: 0.5, color: 'error.main' }}>
                    Agent Action Executed
                  </Typography>
                )}
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
            <Typography variant="caption" sx={{ mb: 1, display: 'block' }}>
              Quick Actions:
            </Typography>
            <Box>
              <Chip
                label="Check subsidies"
                size="small"
                onClick={() => handleQuickAction("What government subsidies am I eligible for?")}
                sx={{ mr: 1, mb: 1 }}
              />
              <Chip
                label="Market analysis"
                size="small"
                onClick={() => handleQuickAction("Analyze current water futures market conditions")}
                sx={{ mr: 1, mb: 1 }}
              />
              {agentMode && (
                <>
                  <Chip
                    label="Buy 5 contracts"
                    size="small"
                    color="warning"
                    onClick={() => handleQuickAction("Buy 5 NQH25 water futures contracts")}
                    sx={{ mr: 1, mb: 1 }}
                  />
                  <Chip
                    label="Claim subsidy"
                    size="small"
                    color="success"
                    onClick={() => handleQuickAction("Process my drought relief subsidy payment")}
                    sx={{ mr: 1, mb: 1 }}
                  />
                </>
              )}
            </Box>
          </Box>

          {/* Input */}
          <Box sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder={agentMode 
                ? "⚠️ AGENT MODE: Commands will execute real trades..." 
                : "Ask about water futures, subsidies..."}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !loading) {
                  sendMessage();
                }
              }}
              size="small"
              disabled={loading}
              error={agentMode}
            />
            <IconButton
              color={agentMode ? "error" : "primary"}
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              sx={{ ml: 1 }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Collapse>

      {/* Agent Mode Warning Dialog */}
      <Dialog
        open={showAgentWarning}
        onClose={cancelAgentMode}
        aria-labelledby="agent-warning-dialog"
      >
        <DialogTitle id="agent-warning-dialog">
          <Box display="flex" alignItems="center">
            <WarningIcon color="error" sx={{ mr: 1 }} />
            Are You Sure You Want to Turn on Agent Mode?
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            AGENT MODE EXECUTES TRADES WITH REAL MONEY
          </Alert>
          <DialogContentText>
            By enabling Agent Mode, you authorize the AI agent to:
          </DialogContentText>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" gutterBottom>
              • Execute water futures trades on your behalf
            </Typography>
            <Typography variant="body2" gutterBottom>
              • Process government subsidy payments via Crossmint
            </Typography>
            <Typography variant="body2" gutterBottom>
              • Access and modify your account balance
            </Typography>
            <Typography variant="body2" gutterBottom>
              • Make financial decisions based on market analysis
            </Typography>
          </Box>
          <Alert severity="warning" sx={{ mt: 2 }}>
            All transactions are FINAL and use REAL MONEY from your connected accounts.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={cancelAgentMode} color="primary" variant="contained">
            Cancel (Stay Safe)
          </Button>
          <Button onClick={confirmAgentMode} color="error" variant="outlined">
            Yes, Enable Agent Mode
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ChatbotV2;
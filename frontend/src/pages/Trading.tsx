import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  Alert,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Divider,
  Tab,
  Tabs,
} from '@mui/material';
import {
  AccountBalance,
  CheckCircle,
  Lock,
} from '@mui/icons-material';
import waterFuturesAPI from '../services/api';
import ChatbotV2 from '../components/ChatbotV2';
import axios from 'axios';
import { API_CONFIG } from '../config/api';

interface Balance {
  tradingAccount: {
    cash: number;
    portfolio_value: number;
    buying_power: number;
    unrealized_pnl: number;
    realized_pnl: number;
    canUseForTrading: boolean;
    message: string;
  };
  subsidyAccounts: {
    totalSubsidies: number;
    totalAvailable: number;
    accounts: Record<string, {
      amount: number;
      available: number;
      used: number;
      restrictions: string;
    }>;
    canUseForTrading: boolean;
    message: string;
  };
  ethBalance?: {
    sepolia: number;
    address: string;
    network: string;
  };
  totalBalance: {
    allFunds: number;
    availableForTrading: number;
    earmarkedForSpecificUse: number;
    message?: string;
  };
  complianceStatus?: {
    isCompliant: boolean;
    nextReportingDate: string;
    warnings?: string[];
  };
}

interface Transaction {
  id: string;
  date: string;
  type: string;
  amount: number;
  status: string;
  description: string;
  fundSource: string;
}

const Trading: React.FC = () => {
  const [contractCode, setContractCode] = useState('NQH25');
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [quantity, setQuantity] = useState(1);
  const [orderStatus, setOrderStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [balance, setBalance] = useState<Balance | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [tabValue, setTabValue] = useState(0);
  const [balanceLoading, setBalanceLoading] = useState(true);

  useEffect(() => {
    // Fetch all data on component mount and when page becomes visible
    fetchBalance();
    fetchTransactions();

    // Add visibility change listener to refresh when tab becomes active
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        fetchBalance();
        fetchTransactions();
      }
    };

    // Add focus listener to refresh when window gains focus
    const handleFocus = () => {
      fetchBalance();
      fetchTransactions();
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  const fetchBalance = async () => {
    try {
      const response = await axios.get(`${API_CONFIG.MCP_URL}/api/mcp/farmer/balance/farmer-ted`);
      setBalance(response.data);
    } catch (error) {
      console.error('Error fetching balance:', error);
    } finally {
      setBalanceLoading(false);
    }
  };

  const fetchTransactions = async () => {
    // Mock transactions - in production would fetch from API
    setTransactions([
      {
        id: 'TXN-001',
        date: '2025-08-23',
        type: 'SUBSIDY',
        amount: 15000,
        status: 'completed',
        description: 'Drought Relief Payment',
        fundSource: 'Crossmint - US Government'
      },
      {
        id: 'TXN-002',
        date: '2025-08-22',
        type: 'TRADE',
        amount: -5000,
        status: 'completed',
        description: 'Buy 10 NQH25 @ $500',
        fundSource: 'Alpaca Trading Account'
      },
      {
        id: 'TXN-003',
        date: '2025-08-21',
        type: 'SUBSIDY_USAGE',
        amount: -2500,
        status: 'completed',
        description: 'Water Rights Purchase',
        fundSource: 'Drought Relief Fund'
      },
    ]);
  };

  const handlePlaceOrder = async () => {
    setLoading(true);
    try {
      // Check if using trading funds
      if (balance && quantity * 500 > balance.tradingAccount.buying_power) {
        setOrderStatus({
          type: 'error',
          message: 'Insufficient trading funds. Subsidy funds cannot be used for trading.',
        });
        setLoading(false);
        return;
      }

      const response = await waterFuturesAPI.placeOrder({
        contractCode,
        side,
        quantity,
      });
      setOrderStatus({
        type: 'success',
        message: `${response.message} - Using Alpaca trading account funds only.`,
      });
      fetchBalance();
      fetchTransactions();
    } catch (err) {
      console.error('Order placement failed:', err);
      setOrderStatus({
        type: 'error',
        message: 'Failed to place order. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Water Futures Trading Dashboard
      </Typography>
      
      {/* Fund Balance Overview */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ bgcolor: '#e8f5e9' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="textSecondary" gutterBottom>
                  Trading Account (Alpaca)
                </Typography>
                <CheckCircle color="success" />
              </Box>
              <Typography variant="h5">
                ${balance?.tradingAccount.portfolio_value.toLocaleString() || '0'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Portfolio Value
              </Typography>
              <Divider sx={{ my: 1 }} />
              <Typography variant="body2">
                Cash: ${balance?.tradingAccount.cash.toLocaleString() || '0'}
              </Typography>
              <Typography variant="body2" color="success.main">
                Buying Power: ${balance?.tradingAccount.buying_power.toLocaleString() || '0'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ bgcolor: '#fff3e0' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="textSecondary" gutterBottom>
                  Subsidy Funds (Crossmint)
                </Typography>
                <Lock color="warning" />
              </Box>
              <Typography variant="h5">
                ${balance?.subsidyAccounts.totalAvailable.toLocaleString() || '0'}
              </Typography>
              <Typography variant="body2" color="warning.main">
                🔒 Restricted - Cannot trade
              </Typography>
              <Divider sx={{ my: 1 }} />
              <Typography variant="caption">
                Earmarked for approved uses only
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
      </Grid>

      {/* Compliance Status Alert */}
      {balance?.complianceStatus && (
        <Alert severity={balance.complianceStatus.isCompliant ? "success" : "warning"} sx={{ mb: 3 }}>
          <Typography variant="body2">
            {balance.complianceStatus.isCompliant 
              ? "✅ All funds are compliant and properly separated" 
              : "⚠️ Compliance review required"}
          </Typography>
          <Typography variant="caption">
            Next reporting date: {balance.complianceStatus.nextReportingDate}
          </Typography>
        </Alert>
      )}

      {/* Tabs for Trading and Transactions */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Trading" />
          <Tab label="Transaction History" />
          <Tab label="Subsidy Details" />
        </Tabs>
      </Paper>

      {/* Trading Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Place Order (Trading Funds Only)
                </Typography>
                
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="caption">
                    Only Alpaca trading account funds can be used. Subsidy funds are restricted.
                  </Typography>
                </Alert>

              <TextField
                fullWidth
                label="Contract Code"
                value={contractCode}
                onChange={(e) => setContractCode(e.target.value)}
                margin="normal"
              />

              <Box sx={{ mt: 2, mb: 2 }}>
                <Typography gutterBottom>Order Side</Typography>
                <ToggleButtonGroup
                  value={side}
                  exclusive
                  onChange={(_, newSide) => newSide && setSide(newSide)}
                  fullWidth
                >
                  <ToggleButton value="BUY" color="success">
                    BUY
                  </ToggleButton>
                  <ToggleButton value="SELL" color="error">
                    SELL
                  </ToggleButton>
                </ToggleButtonGroup>
              </Box>

              <TextField
                fullWidth
                label="Quantity"
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value))}
                margin="normal"
                inputProps={{ min: 1 }}
              />

              <Button
                fullWidth
                variant="contained"
                color={side === 'BUY' ? 'success' : 'error'}
                onClick={handlePlaceOrder}
                disabled={loading || balanceLoading}
                sx={{ mt: 2 }}
              >
                {loading ? 'Processing...' : `Place ${side} Order (Using Trading Funds)`}
              </Button>
              
              <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                Available Trading Funds: ${balance?.tradingAccount.buying_power.toLocaleString() || '0'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Alpaca Portfolio Summary
              </Typography>
              
              <Grid container spacing={2}>
                <Grid size={6}>
                  <Typography color="textSecondary" variant="subtitle2">
                    Portfolio Value
                  </Typography>
                  <Typography variant="h6">
                    ${balance?.tradingAccount.portfolio_value.toLocaleString() || '0'}
                  </Typography>
                </Grid>
                <Grid size={6}>
                  <Typography color="textSecondary" variant="subtitle2">
                    Cash Balance
                  </Typography>
                  <Typography variant="h6">
                    ${balance?.tradingAccount.cash.toLocaleString() || '0'}
                  </Typography>
                </Grid>
                <Grid size={6}>
                  <Typography color="textSecondary" variant="subtitle2">
                    Unrealized P&L
                  </Typography>
                  <Typography variant="h6" color={(balance?.tradingAccount.unrealized_pnl ?? 0) >= 0 ? "success.main" : "error.main"}>
                    {(balance?.tradingAccount.unrealized_pnl ?? 0) >= 0 ? '+' : ''}
                    ${balance?.tradingAccount.unrealized_pnl?.toLocaleString() || '0'}
                  </Typography>
                </Grid>
                <Grid size={6}>
                  <Typography color="textSecondary" variant="subtitle2">
                    Realized P&L
                  </Typography>
                  <Typography variant="h6" color={(balance?.tradingAccount.realized_pnl ?? 0) >= 0 ? "success.main" : "error.main"}>
                    {(balance?.tradingAccount.realized_pnl ?? 0) >= 0 ? '+' : ''}
                    ${balance?.tradingAccount.realized_pnl?.toLocaleString() || '0'}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Positions
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2">NQH25 - 10 Contracts</Typography>
                <Typography color="success.main">+$80 (1.6%)</Typography>
              </Box>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2">NQM25 - 5 Contracts</Typography>
                <Typography color="error.main">-$30 (-1.2%)</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      )}

      {/* Transaction History Tab */}
      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Transaction History
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Fund Source</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {transactions.map((tx) => (
                    <TableRow key={tx.id}>
                      <TableCell>{tx.date}</TableCell>
                      <TableCell>
                        <Chip 
                          label={tx.type} 
                          size="small" 
                          color={tx.type === 'SUBSIDY' ? 'warning' : tx.type === 'TRADE' ? 'primary' : 'default'}
                        />
                      </TableCell>
                      <TableCell>{tx.description}</TableCell>
                      <TableCell>
                        <Typography variant="caption">
                          {tx.fundSource}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography color={tx.amount >= 0 ? 'success.main' : 'error.main'}>
                          {tx.amount >= 0 ? '+' : ''}
                          ${Math.abs(tx.amount).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={tx.status} 
                          size="small" 
                          color={tx.status === 'completed' ? 'success' : 'default'}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Subsidy Details Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid size={12}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="body2">
                ⚠️ Government subsidies via Crossmint are EARMARKED and cannot be used for futures trading
              </Typography>
            </Alert>
          </Grid>
          {Object.entries(balance?.subsidyAccounts.accounts || {}).map(([type, details]) => (
            <Grid size={{ xs: 12, md: 6 }} key={type}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {type.replace('_', ' ').toUpperCase()}
                  </Typography>
                  <Box display="flex" justifyContent="space-between" mb={2}>
                    <Typography color="textSecondary">
                      Total Amount
                    </Typography>
                    <Typography>
                      ${details.amount.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between" mb={2}>
                    <Typography color="textSecondary">
                      Available
                    </Typography>
                    <Typography color="success.main">
                      ${details.available.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between" mb={2}>
                    <Typography color="textSecondary">
                      Used
                    </Typography>
                    <Typography color="error.main">
                      ${details.used.toLocaleString()}
                    </Typography>
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Alert severity="info">
                    <Typography variant="caption">
                      {details.restrictions}
                    </Typography>
                  </Alert>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Integrated Chatbot */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            AI Trading Assistant
          </Typography>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="caption">
              Ask about trading strategies, check subsidies, or get help with fund management.
              The assistant knows about your fund restrictions.
            </Typography>
          </Alert>
          <ChatbotV2 />
        </CardContent>
      </Card>

      <Snackbar
        open={orderStatus !== null}
        autoHideDuration={6000}
        onClose={() => setOrderStatus(null)}
      >
        <Alert severity={orderStatus?.type || 'info'} onClose={() => setOrderStatus(null)}>
          {orderStatus?.message || ''}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Trading;
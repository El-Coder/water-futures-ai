import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Divider,
  Paper,
} from '@mui/material';
import {
  AccountBalance as AccountBalanceIcon,
  TrendingUp,
  AttachMoney,
  Agriculture,
} from '@mui/icons-material';

interface Transaction {
  id: string;
  type: 'subsidy' | 'trade' | 'deposit' | 'withdrawal';
  description: string;
  amount: number;
  timestamp: string;
  source?: string;
  metadata?: {
    program?: string;
    region?: string;
    severity?: number;
    contractCode?: string;
    quantity?: number;
    price?: number;
    confidence?: number;
    status?: string;
  };
}

const Account: React.FC = () => {
  const [balance] = useState(125000);
  const [transactions] = useState<Transaction[]>([
    {
      id: '1',
      type: 'deposit',
      description: 'Initial deposit',
      amount: 100000,
      timestamp: '2024-12-01T09:00:00',
      source: 'Bank Transfer',
    },
    {
      id: '2',
      type: 'subsidy',
      description: 'USDA Drought Relief Payment',
      amount: 15000,
      timestamp: '2024-12-05T14:30:00',
      source: 'Crossmint Agent - US Government',
      metadata: {
        program: 'Emergency Drought Assistance',
        region: 'Central Valley',
        severity: 4,
      },
    },
    {
      id: '3',
      type: 'trade',
      description: 'Bought 10 NQH25 Water Futures @ $502',
      amount: -5020,
      timestamp: '2024-12-06T10:15:00',
      source: 'Automated Trading System',
      metadata: {
        contractCode: 'NQH25',
        quantity: 10,
        price: 502,
        strategy: 'drought_hedge',
      },
    },
    {
      id: '4',
      type: 'subsidy',
      description: 'California Water Conservation Incentive',
      amount: 8000,
      timestamp: '2024-12-08T11:00:00',
      source: 'Crossmint Agent - CA State',
      metadata: {
        program: 'Water Efficiency Rebate',
        savedGallons: 50000,
      },
    },
    {
      id: '5',
      type: 'trade',
      description: 'Sold 5 NQH25 Water Futures @ $508',
      amount: 2540,
      timestamp: '2024-12-10T15:45:00',
      source: 'Automated Trading System',
      metadata: {
        contractCode: 'NQH25',
        quantity: 5,
        price: 508,
        profit: 30,
      },
    },
    {
      id: '6',
      type: 'subsidy',
      description: 'Federal Crop Insurance Payout',
      amount: 12000,
      timestamp: '2024-12-12T09:30:00',
      source: 'Crossmint Agent - USDA',
      metadata: {
        reason: 'Yield loss due to water shortage',
        coverage: '70% of expected yield',
      },
    },
    {
      id: '7',
      type: 'trade',
      description: 'Bought 15 NQM25 Water Futures @ $515',
      amount: -7725,
      timestamp: '2024-12-13T14:20:00',
      source: 'AI Trading Strategy',
      metadata: {
        contractCode: 'NQM25',
        quantity: 15,
        price: 515,
        signal: 'Severe drought forecast',
        confidence: 0.85,
      },
    },
  ]);

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'subsidy':
        return <Agriculture color="success" />;
      case 'trade':
        return <TrendingUp color="primary" />;
      case 'deposit':
        return <AttachMoney color="info" />;
      default:
        return <AccountBalanceIcon />;
    }
  };

  const getTransactionColor = (type: string) => {
    switch (type) {
      case 'subsidy':
        return 'success';
      case 'trade':
        return 'primary';
      case 'deposit':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(Math.abs(amount));
  };

  const totalSubsidies = transactions
    .filter(t => t.type === 'subsidy')
    .reduce((sum, t) => sum + t.amount, 0);

  const totalTrades = transactions
    .filter(t => t.type === 'trade')
    .reduce((sum, t) => sum + t.amount, 0);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Account Balance & Transactions
      </Typography>

      <Grid container spacing={3}>
        {/* Balance Overview */}
        <Grid size={12}>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Current Balance
                  </Typography>
                  <Typography variant="h4">
                    {formatCurrency(balance)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Government Subsidies
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    +{formatCurrency(totalSubsidies)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Trading P&L
                  </Typography>
                  <Typography variant="h5" color={totalTrades >= 0 ? 'success.main' : 'error.main'}>
                    {totalTrades >= 0 ? '+' : ''}{formatCurrency(totalTrades)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Active Positions
                  </Typography>
                  <Typography variant="h5">
                    20 Contracts
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Transaction History */}
        <Grid size={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Transaction History
            </Typography>
            <List>
              {transactions.reverse().map((transaction, index) => (
                <React.Fragment key={transaction.id}>
                  <ListItem>
                    <ListItemIcon>
                      {getTransactionIcon(transaction.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Box>
                            <Typography variant="subtitle1">
                              {transaction.description}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              {new Date(transaction.timestamp).toLocaleString()}
                            </Typography>
                            {transaction.source && (
                              <Chip 
                                label={transaction.source} 
                                size="small" 
                                color={getTransactionColor(transaction.type) as 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'}
                                sx={{ mt: 0.5 }}
                              />
                            )}
                          </Box>
                          <Typography 
                            variant="h6" 
                            color={transaction.amount >= 0 ? 'success.main' : 'error.main'}
                          >
                            {transaction.amount >= 0 ? '+' : ''}{formatCurrency(transaction.amount)}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        transaction.metadata && (
                          <span style={{ marginTop: '8px', display: 'block' }}>
                            {transaction.type === 'subsidy' && (
                              <span style={{ fontSize: '0.75rem', color: 'rgba(0, 0, 0, 0.6)' }}>
                                Program: {transaction.metadata.program}
                                {transaction.metadata.region && ` | Region: ${transaction.metadata.region}`}
                                {transaction.metadata.severity && ` | Drought Severity: ${transaction.metadata.severity}/5`}
                              </span>
                            )}
                            {transaction.type === 'trade' && (
                              <span style={{ fontSize: '0.75rem', color: 'rgba(0, 0, 0, 0.6)' }}>
                                Contract: {transaction.metadata.contractCode} | 
                                Qty: {transaction.metadata.quantity} | 
                                Price: ${transaction.metadata.price}
                                {transaction.metadata.confidence && ` | AI Confidence: ${(transaction.metadata.confidence * 100).toFixed(0)}%`}
                              </span>
                            )}
                          </span>
                        )
                      }
                    />
                  </ListItem>
                  {index < transactions.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Subsidy Programs Info */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Subsidy Programs
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText 
                    primary="USDA Emergency Drought Assistance"
                    secondary="Eligible for payments based on drought severity in your region"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="California Water Conservation Rebate"
                    secondary="$0.16 per gallon saved through efficiency improvements"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Federal Crop Insurance"
                    secondary="Automatic payouts when yield falls below 70% due to water shortage"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Automated Trading Status */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Automated Trading Status
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Active Strategy
                </Typography>
                <Typography variant="body1">
                  Drought Severity Hedging
                </Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Next Trade Signal
                </Typography>
                <Typography variant="body1">
                  BUY 5 NQH26 if drought severity exceeds 4.2
                </Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" color="textSecondary">
                  Risk Limit
                </Typography>
                <Typography variant="body1">
                  $50,000 max position size
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Account;
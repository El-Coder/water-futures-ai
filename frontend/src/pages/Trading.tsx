import React, { useState } from 'react';
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
} from '@mui/material';
import waterFuturesAPI from '../services/api';

const Trading: React.FC = () => {
  const [contractCode, setContractCode] = useState('NQH25');
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [quantity, setQuantity] = useState(1);
  const [orderStatus, setOrderStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const handlePlaceOrder = async () => {
    setLoading(true);
    try {
      const response = await waterFuturesAPI.placeOrder({
        contractCode,
        side,
        quantity,
      });
      setOrderStatus({
        type: 'success',
        message: response.message,
      });
    } catch (error) {
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
        Trading Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Place Order
              </Typography>

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
                disabled={loading}
                sx={{ mt: 2 }}
              >
                {loading ? 'Processing...' : `Place ${side} Order`}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Portfolio Summary
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography color="textSecondary" variant="subtitle2">
                    Total Value
                  </Typography>
                  <Typography variant="h6">
                    $105,000
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography color="textSecondary" variant="subtitle2">
                    Cash Balance
                  </Typography>
                  <Typography variant="h6">
                    $95,000
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography color="textSecondary" variant="subtitle2">
                    Open Positions
                  </Typography>
                  <Typography variant="h6">
                    3
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography color="textSecondary" variant="subtitle2">
                    Daily P&L
                  </Typography>
                  <Typography variant="h6" color="success.main">
                    +$250
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

      <Snackbar
        open={orderStatus !== null}
        autoHideDuration={6000}
        onClose={() => setOrderStatus(null)}
      >
        {orderStatus && (
          <Alert severity={orderStatus.type} onClose={() => setOrderStatus(null)}>
            {orderStatus.message}
          </Alert>
        )}
      </Snackbar>
    </Box>
  );
};

export default Trading;
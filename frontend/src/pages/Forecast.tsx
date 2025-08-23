import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import waterFuturesAPI from '../services/api';

interface ForecastResponse {
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

const Forecast: React.FC = () => {
  const [contractCode, setContractCode] = useState('NQH25');
  const [horizonDays, setHorizonDays] = useState(7);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await waterFuturesAPI.generateForecast({
        contractCode,
        horizonDays,
      });
      setForecast(response);
    } catch (err) {
      setError('Failed to generate forecast. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const chartData = forecast?.predictedPrices.map((p, i) => ({
    day: `Day ${i + 1}`,
    price: p.price,
    current: i === 0 ? forecast.currentPrice : undefined,
  }));

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Water Futures Forecast
      </Typography>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Forecast Parameters
              </Typography>
              
              <TextField
                fullWidth
                label="Contract Code"
                value={contractCode}
                onChange={(e) => setContractCode(e.target.value)}
                margin="normal"
              />
              
              <TextField
                fullWidth
                label="Forecast Horizon (days)"
                type="number"
                value={horizonDays}
                onChange={(e) => setHorizonDays(parseInt(e.target.value))}
                margin="normal"
                inputProps={{ min: 1, max: 30 }}
              />
              
              <Button
                fullWidth
                variant="contained"
                onClick={generateForecast}
                disabled={loading}
                sx={{ mt: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Generate Forecast'}
              </Button>
            </CardContent>
          </Card>

          {forecast && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Model Confidence
                </Typography>
                <Typography variant="h4" color="primary">
                  {(forecast.modelConfidence * 100).toFixed(1)}%
                </Typography>
                
                <Typography variant="subtitle2" sx={{ mt: 2 }}>
                  Current Price
                </Typography>
                <Typography variant="h5">
                  ${forecast.currentPrice.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>

        <Grid size={{ xs: 12, md: 8 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {forecast && chartData && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Price Forecast
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="price"
                      stroke="#1976d2"
                      strokeWidth={2}
                      dot={{ fill: '#1976d2' }}
                    />
                    <Line
                      type="monotone"
                      dataKey="current"
                      stroke="#dc004e"
                      strokeDasharray="5 5"
                      name="Current Price"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {forecast?.factors && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Contributing Factors
                </Typography>
                <Grid container spacing={2}>
                  {Object.entries(forecast.factors).map(([key, value]) => (
                    <Grid item xs={6} key={key}>
                      <Typography variant="subtitle2" color="textSecondary">
                        {key.replace(/_/g, ' ').toUpperCase()}
                      </Typography>
                      <Typography variant="body1">
                        {String(value)}
                      </Typography>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default Forecast;
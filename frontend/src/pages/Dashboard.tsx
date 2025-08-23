import React, { useEffect, useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import waterFuturesAPI from '../services/api';

const Dashboard: React.FC = () => {
  const [currentPrices, setCurrentPrices] = useState<any[]>([]);
  const [droughtData, setDroughtData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [prices, drought] = await Promise.all([
        waterFuturesAPI.getCurrentPrices(),
        waterFuturesAPI.getDroughtMap(),
      ]);
      setCurrentPrices(prices);
      setDroughtData(drought);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mock data for chart
  const chartData = [
    { date: 'Jan', price: 480, volume: 1200 },
    { date: 'Feb', price: 485, volume: 1100 },
    { date: 'Mar', price: 490, volume: 1300 },
    { date: 'Apr', price: 495, volume: 1250 },
    { date: 'May', price: 502, volume: 1400 },
    { date: 'Jun', price: 508, volume: 1350 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Water Futures Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Key Metrics */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Current Index
              </Typography>
              <Typography variant="h5">
                $508.23
              </Typography>
              <Typography color="success.main" variant="body2">
                +2.5% (24h)
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Trading Volume
              </Typography>
              <Typography variant="h5">
                1,350
              </Typography>
              <Typography variant="body2">
                Contracts
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Drought Severity
              </Typography>
              <Typography variant="h5">
                3.6 / 5
              </Typography>
              <Typography color="warning.main" variant="body2">
                Moderate-Severe
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                News Sentiment
              </Typography>
              <Typography variant="h5">
                -0.15
              </Typography>
              <Typography color="error.main" variant="body2">
                Slightly Negative
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Price Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Price History
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#1976d2"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Volume Chart */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Trading Volume
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="volume"
                  stroke="#dc004e"
                  fill="#dc004e"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Drought Map Placeholder */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              California Drought Severity Map
            </Typography>
            <Box sx={{ height: 400, bgcolor: 'grey.100', p: 2 }}>
              {droughtData && (
                <Grid container spacing={2}>
                  {droughtData.regions?.map((region: any) => (
                    <Grid item xs={12} md={4} key={region.name}>
                      <Card>
                        <CardContent>
                          <Typography variant="subtitle1">
                            {region.name}
                          </Typography>
                          <Typography
                            color={region.severity >= 4 ? 'error.main' : 'warning.main'}
                          >
                            Severity: {region.severity}/5
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
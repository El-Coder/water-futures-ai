import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Paper,
  Chip,
  Button,
  CircularProgress,
} from '@mui/material';
import {
  WaterDrop,
  CloudOff,
  Warning,
  CheckCircle,
} from '@mui/icons-material';

const Demo: React.FC = () => {
  const [droughtLevel, setDroughtLevel] = useState<'low' | 'medium' | 'high'>('low');
  const [transferStatus, setTransferStatus] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [subsidyAmount, setSubsidyAmount] = useState<string>('0');

  // Get subsidy amount based on drought level
  const getSubsidyAmount = (level: 'low' | 'medium' | 'high') => {
    switch (level) {
      case 'low':
        return '0';
      case 'medium':
        return '0.25';
      case 'high':
        return '0.5';
      default:
        return '0';
    }
  };

  // Handle drought level change
  const handleDroughtLevelChange = async (newLevel: 'low' | 'medium' | 'high') => {
    setDroughtLevel(newLevel);
    const amount = getSubsidyAmount(newLevel);
    setSubsidyAmount(amount);
    
    // Update the global context for the chatbot
    try {
      await fetch('http://localhost:8001/api/v1/context/drought', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          droughtLevel: newLevel,
          subsidyAmount: amount,
          farmerId: 'farmer-ted',
        }),
      });
      
      if (newLevel === 'low') {
        setTransferStatus('ℹ️ No subsidies available - drought level is low');
      } else if (newLevel === 'medium') {
        setTransferStatus(`⚠️ Eligible for ${amount} USDC subsidy - moderate drought detected`);
      } else {
        setTransferStatus(`🚨 Eligible for ${amount} USDC emergency relief - severe drought!`);
      }
    } catch (error) {
      console.error('Error updating drought context:', error);
    }
  };

  // Manually trigger a transfer (for demo purposes)
  const executeTransfer = async () => {
    if (subsidyAmount === '0') {
      setTransferStatus('❌ No subsidy available at low drought level');
      return;
    }
    
    setIsProcessing(true);
    setTransferStatus('Processing transfer...');
    
    try {
      const response = await fetch('http://localhost:8001/api/v1/drought/execute-transfer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          droughtLevel,
          amount: subsidyAmount,
          farmerId: 'farmer-ted',
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setTransferStatus(`✅ Transfer complete! ${subsidyAmount} USDC sent from Uncle Sam to Farmer Ted`);
      } else {
        setTransferStatus(`❌ Transfer failed: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Transfer error:', error);
      setTransferStatus('❌ Transfer failed. Please check the connection.');
    } finally {
      setIsProcessing(false);
    }
  };

  const getDroughtIcon = (level: 'low' | 'medium' | 'high') => {
    switch (level) {
      case 'low':
        return <WaterDrop sx={{ color: 'green', fontSize: 40 }} />;
      case 'medium':
        return <Warning sx={{ color: 'orange', fontSize: 40 }} />;
      case 'high':
        return <CloudOff sx={{ color: 'red', fontSize: 40 }} />;
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Drought Index Demo & Subsidy System
      </Typography>
      
      <Grid container spacing={3}>
        {/* Drought Control Panel */}
        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                🌾 Farmer Ted's Farm - Drought Monitor
              </Typography>
              
              <Grid container spacing={3} sx={{ mt: 2 }}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Paper sx={{ p: 3, bgcolor: 'background.default' }}>
                    <Box display="flex" alignItems="center" gap={2} mb={3}>
                      {getDroughtIcon(droughtLevel)}
                      <Box>
                        <Typography variant="h6">Current Drought Status</Typography>
                        <Chip 
                          label={droughtLevel.toUpperCase()} 
                          color={droughtLevel === 'low' ? 'success' : droughtLevel === 'medium' ? 'warning' : 'error'}
                          size="small"
                        />
                      </Box>
                    </Box>
                    
                    <FormControl fullWidth>
                      <InputLabel>Set Drought Level (Demo Control)</InputLabel>
                      <Select
                        value={droughtLevel}
                        label="Set Drought Level (Demo Control)"
                        onChange={(e) => handleDroughtLevelChange(e.target.value as 'low' | 'medium' | 'high')}
                        disabled={isProcessing}
                      >
                        <MenuItem value="low">
                          <Box display="flex" alignItems="center" gap={1}>
                            <CheckCircle sx={{ color: 'green' }} />
                            <Box>
                              <Typography>Low - Normal Conditions</Typography>
                              <Typography variant="caption">No subsidy (0 USDC)</Typography>
                            </Box>
                          </Box>
                        </MenuItem>
                        <MenuItem value="medium">
                          <Box display="flex" alignItems="center" gap={1}>
                            <Warning sx={{ color: 'orange' }} />
                            <Box>
                              <Typography>Medium - Moderate Drought</Typography>
                              <Typography variant="caption">0.25 USDC subsidy available</Typography>
                            </Box>
                          </Box>
                        </MenuItem>
                        <MenuItem value="high">
                          <Box display="flex" alignItems="center" gap={1}>
                            <CloudOff sx={{ color: 'red' }} />
                            <Box>
                              <Typography>High - Severe Drought</Typography>
                              <Typography variant="caption">0.5 USDC emergency relief</Typography>
                            </Box>
                          </Box>
                        </MenuItem>
                      </Select>
                    </FormControl>
                  </Paper>
                </Grid>
                
                <Grid size={{ xs: 12, md: 6 }}>
                  <Paper sx={{ p: 3, bgcolor: 'background.default' }}>
                    <Typography variant="h6" gutterBottom>
                      Subsidy Eligibility
                    </Typography>
                    
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="body2" color="textSecondary">
                        Current Subsidy Amount:
                      </Typography>
                      <Typography variant="h3" color={subsidyAmount === '0' ? 'text.disabled' : 'primary'}>
                        {subsidyAmount} USDC
                      </Typography>
                    </Box>
                    
                    <Button
                      variant="contained"
                      onClick={executeTransfer}
                      disabled={isProcessing || subsidyAmount === '0'}
                      fullWidth
                      startIcon={isProcessing ? <CircularProgress size={20} /> : null}
                    >
                      {isProcessing ? 'Processing...' : `Execute Transfer (${subsidyAmount} USDC)`}
                    </Button>
                    
                    {transferStatus && (
                      <Alert 
                        severity={
                          transferStatus.includes('✅') ? 'success' : 
                          transferStatus.includes('⚠️') ? 'warning' : 
                          transferStatus.includes('🚨') ? 'error' :
                          transferStatus.includes('❌') ? 'error' : 'info'
                        }
                        sx={{ mt: 2 }}
                        onClose={() => setTransferStatus('')}
                      >
                        {transferStatus}
                      </Alert>
                    )}
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Instructions */}
        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📋 How This Works
              </Typography>
              <Box sx={{ pl: 2 }}>
                <Typography variant="body1" paragraph>
                  <strong>1. Set Drought Level:</strong> Use the dropdown to simulate different drought conditions.
                </Typography>
                <Typography variant="body1" paragraph>
                  <strong>2. Automatic Context Update:</strong> The drought level is shared with the AI chatbot.
                </Typography>
                <Typography variant="body1" paragraph>
                  <strong>3. Ask the Chatbot:</strong> Go to the chat and ask "Am I eligible for any government subsidies today?"
                </Typography>
                <Typography variant="body1" paragraph>
                  <strong>4. Subsidy Amounts:</strong>
                </Typography>
                <Box sx={{ pl: 3, mb: 2 }}>
                  <Typography variant="body2">• Low drought: No subsidy (0 USDC)</Typography>
                  <Typography variant="body2">• Medium drought: 0.25 USDC</Typography>
                  <Typography variant="body2">• High drought: 0.5 USDC emergency relief</Typography>
                </Box>
                <Typography variant="body1" paragraph>
                  <strong>5. Execute Transfer:</strong> The chatbot can ask if you want to execute the transfer. Say "yes" to proceed.
                </Typography>
                <Typography variant="body1" paragraph>
                  <strong>6. Crossmint Integration:</strong> Transfers are processed via Crossmint from Uncle Sam's wallet to Farmer Ted.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Technical Details */}
        <Grid size={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🔧 Technical Implementation
              </Typography>
              <Grid container spacing={2}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    MCP Server Endpoints:
                  </Typography>
                  <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', bgcolor: 'grey.100', p: 1, borderRadius: 1 }}>
{`POST /api/v1/context/drought
POST /api/v1/drought/execute-transfer
POST /api/v1/agent/subsidy-check`}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Transfer Flow:
                  </Typography>
                  <Typography variant="body2">
                    1. Frontend sets drought level<br/>
                    2. MCP server updates context<br/>
                    3. Chatbot checks eligibility<br/>
                    4. User confirms in chat<br/>
                    5. Crossmint executes transfer<br/>
                    6. Confirmation sent to user
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Demo;
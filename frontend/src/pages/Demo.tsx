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
  const [isSubmitted, setIsSubmitted] = useState(false);

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

  // Handle drought level change (just updates UI, doesn't submit)
  const handleDroughtLevelChange = (newLevel: 'low' | 'medium' | 'high') => {
    if (!isSubmitted) {
      setDroughtLevel(newLevel);
      const amount = getSubsidyAmount(newLevel);
      setSubsidyAmount(amount);
    }
  };
  
  // Submit drought level to the system
  const submitDroughtLevel = async () => {
    setIsProcessing(true);
    setIsSubmitted(true);
    const amount = getSubsidyAmount(droughtLevel);
    
    try {
      // Update the global context for the chatbot
      const contextResponse = await fetch('http://localhost:8001/api/v1/context/drought', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          droughtLevel,
          subsidyAmount: amount,
          farmerId: 'farmer-ted',
        }),
      });
      
      if (contextResponse.ok) {
        // Trigger the agent to send a proactive message
        await fetch('http://localhost:8001/api/v1/agent/notify-drought', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            droughtLevel,
            subsidyAmount: amount,
            farmerId: 'farmer-ted',
          }),
        });
        
        if (droughtLevel === 'low') {
          setTransferStatus('✅ Drought level submitted. Check the chat for agent response.');
        } else if (droughtLevel === 'medium') {
          setTransferStatus(`✅ Drought level submitted. You're eligible for ${amount} USDC. Check the chat!`);
        } else {
          setTransferStatus(`✅ Emergency drought level submitted. ${amount} USDC relief available. Check the chat!`);
        }
      }
    } catch (error) {
      console.error('Error updating drought context:', error);
      setTransferStatus('❌ Failed to submit drought level');
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Reset the form
  const resetForm = () => {
    setIsSubmitted(false);
    setDroughtLevel('low');
    setSubsidyAmount('0');
    setTransferStatus('');
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
                    
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Set Drought Level (Demo Control)</InputLabel>
                      <Select
                        value={droughtLevel}
                        label="Set Drought Level (Demo Control)"
                        onChange={(e) => handleDroughtLevelChange(e.target.value as 'low' | 'medium' | 'high')}
                        disabled={isProcessing || isSubmitted}
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
                    
                    {isSubmitted && (
                      <Alert severity="info" sx={{ mb: 2 }}>
                        Drought level has been submitted. The agent will contact you in the chat.
                      </Alert>
                    )}
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
                    
                    {!isSubmitted ? (
                      <Button
                        variant="contained"
                        onClick={submitDroughtLevel}
                        disabled={isProcessing}
                        fullWidth
                        color="primary"
                        size="large"
                        startIcon={isProcessing ? <CircularProgress size={20} color="inherit" /> : null}
                      >
                        {isProcessing ? 'Submitting...' : 'Submit Drought Level'}
                      </Button>
                    ) : (
                      <Button
                        variant="outlined"
                        onClick={resetForm}
                        fullWidth
                        size="large"
                      >
                        Reset Demo
                      </Button>
                    )}
                    
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
                  <strong>2. Submit to System:</strong> Click "Submit Drought Level" to send the information to the AI agent.
                </Typography>
                <Typography variant="body1" paragraph>
                  <strong>3. Agent Contact:</strong> The agent will proactively message you in the chat about available subsidies.
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
                  <strong>5. Respond to Agent:</strong> The agent will ask if you want to execute the transfer. Reply "yes" or "no" in the chat.
                </Typography>
                <Typography variant="body1" paragraph>
                  <strong>6. Crossmint Integration:</strong> If you confirm, transfers are processed via Crossmint from Uncle Sam's wallet to Farmer Ted.
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
POST /api/v1/agent/notify-drought
POST /api/v1/drought/execute-transfer`}
                  </Typography>
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Transfer Flow:
                  </Typography>
                  <Typography variant="body2">
                    1. User sets drought level<br/>
                    2. Submits to MCP server<br/>
                    3. Agent proactively messages user<br/>
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
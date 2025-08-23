import React, { useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import waterFuturesAPI from '../services/api';

const DataUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setMessage(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage({ type: 'error', text: 'Please select a file first' });
      return;
    }

    setUploading(true);
    try {
      const response = await waterFuturesAPI.uploadCSV(file);
      setMessage({ type: 'success', text: response.message || 'File uploaded successfully!' });
      setFile(null);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to upload file. Please try again.' });
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload Historical Data
      </Typography>

      <Paper sx={{ p: 4, mt: 3 }}>
        <Typography variant="body1" gutterBottom>
          Upload CSV files containing historical water futures data for analysis and forecasting.
        </Typography>

        <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <input
            accept=".csv"
            style={{ display: 'none' }}
            id="file-upload"
            type="file"
            onChange={handleFileChange}
          />
          <label htmlFor="file-upload">
            <Button
              variant="outlined"
              component="span"
              startIcon={<CloudUploadIcon />}
              fullWidth
            >
              Select CSV File
            </Button>
          </label>

          {file && (
            <Typography variant="body2">
              Selected file: {file.name}
            </Typography>
          )}

          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!file || uploading}
            fullWidth
          >
            {uploading ? <CircularProgress size={24} /> : 'Upload File'}
          </Button>

          {message && (
            <Alert severity={message.type}>
              {message.text}
            </Alert>
          )}
        </Box>

        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Expected CSV Format:
          </Typography>
          <Typography variant="body2" component="pre" sx={{ bgcolor: 'grey.100', p: 2 }}>
            {`date,contract_code,open,high,low,close,volume,settlement_price
2024-01-01,NQH20,495.50,498.00,494.00,497.25,1234,497.00
2024-01-02,NQH20,497.25,499.50,496.00,498.75,1189,498.50
...`}
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default DataUpload;
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/Layout';
import Account from './pages/Account';
import Forecast from './pages/Forecast';
import News from './pages/News';
import Demo from './pages/Demo';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2E7D32', // Deep green for grass/farming
      light: '#66BB6A',
      dark: '#1B5E20',
    },
    secondary: {
      main: '#1976D2', // Sky blue for water
      light: '#42A5F5',
      dark: '#0D47A1',
    },
    background: {
      default: '#F1F8E9', // Light green tint
      paper: '#FFFFFF',
    },
    info: {
      main: '#29B6F6', // Light blue for water elements
    },
    success: {
      main: '#4CAF50', // Green for growth
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Account />} />
            <Route path="/forecast" element={<Forecast />} />
            <Route path="/news" element={<News />} />
            <Route path="/demo" element={<Demo />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App

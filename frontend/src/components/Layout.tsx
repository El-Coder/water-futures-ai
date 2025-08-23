import React, { useState } from 'react';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Container,
} from '@mui/material';
import {
  Menu as MenuIcon,
  AccountBalance as AccountBalanceIcon,
  WaterDrop as WaterDropIcon,
  ShowChart as ShowChartIcon,
  Article as ArticleIcon,
  Grass as GrassIcon,
  Agriculture as AgricultureIcon,
  Opacity as OpacityIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import ChatbotV2 from './ChatbotV2';

interface LayoutProps {
  children: React.ReactNode;
}

const menuItems = [
  { text: 'Account & Transactions', icon: <AccountBalanceIcon />, path: '/' },
  { text: 'Water Market Forecast', icon: <WaterDropIcon />, path: '/forecast' },
  { text: 'Agricultural News', icon: <AgricultureIcon />, path: '/news' },
];

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ 
        background: 'linear-gradient(135deg, #2E7D32 0%, #1976D2 100%)',
        boxShadow: '0 4px 20px rgba(0,0,0,0.15)'
      }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={toggleDrawer}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <WaterDropIcon sx={{ mr: 1, fontSize: 28 }} />
          <Typography variant="h6" noWrap component="div" sx={{ 
            fontWeight: 600,
            letterSpacing: '0.5px'
          }}>
            AquaFarm Futures 🌾
          </Typography>
        </Toolbar>
      </AppBar>

      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={toggleDrawer}
      >
        <Box
          sx={{ 
            width: 250,
            background: 'linear-gradient(180deg, #F1F8E9 0%, #E8F5E9 100%)',
            height: '100%'
          }}
          role="presentation"
          onClick={toggleDrawer}
        >
          <Box sx={{ 
            p: 2, 
            background: 'linear-gradient(135deg, #2E7D32 0%, #1976D2 100%)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}>
            <WaterDropIcon />
            <Typography variant="h6" fontWeight={600}>
              AquaFarm 🌾
            </Typography>
          </Box>
          <List>
            {menuItems.map((item) => (
              <ListItem
                button
                key={item.text}
                onClick={() => navigate(item.path)}
                selected={location.pathname === item.path}
                sx={{
                  m: 1,
                  borderRadius: 2,
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(46, 125, 50, 0.1)',
                    '&:hover': {
                      backgroundColor: 'rgba(46, 125, 50, 0.2)',
                    }
                  },
                  '&:hover': {
                    backgroundColor: 'rgba(46, 125, 50, 0.05)',
                  }
                }}
              >
                <ListItemIcon sx={{ color: location.pathname === item.path ? '#2E7D32' : '#66BB6A' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text} 
                  sx={{ 
                    '& .MuiTypography-root': { 
                      fontWeight: location.pathname === item.path ? 600 : 400,
                      color: location.pathname === item.path ? '#1B5E20' : '#2E7D32'
                    }
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ 
        flexGrow: 1, 
        p: 3, 
        mt: 8,
        minHeight: '100vh',
        background: 'linear-gradient(180deg, rgba(227, 242, 253, 0.4) 0%, rgba(241, 248, 233, 0.6) 100%)',
        position: 'relative',
        '&::after': {
          content: '""',
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          height: '120px',
          background: 'linear-gradient(to top, rgba(102, 187, 106, 0.1) 0%, transparent 100%)',
          pointerEvents: 'none',
          zIndex: 0
        }
      }}>
        <Container maxWidth="xl" sx={{ position: 'relative', zIndex: 1 }}>
          {children}
        </Container>
      </Box>
      
      <ChatbotV2 />
    </Box>
  );
};

export default Layout;
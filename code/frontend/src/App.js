// src/App.js
import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import MainLayout from './components/layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Recommendations from './pages/Recommendations';
import Transactions from './pages/Transactions';
import Assistant from './pages/Assistant';

// Create a theme.
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <MainLayout>
        {{
          dashboard: <Dashboard onNavigate={setActiveTab} />,
          recommendations: <Recommendations />,
          transactions: <Transactions />,
          assistant: <Assistant />
        }}
      </MainLayout>
    </ThemeProvider>
  );
}

export default App;
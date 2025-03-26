import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider } from './context/AuthContext';
import MainLayout from './components/layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Recommendations from './pages/Recommendations';
import Transactions from './pages/Transactions';
import Assistant from './pages/Assistant';
import { Snackbar, Alert } from '@mui/material';

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

// Add global error handling for API calls
const originalFetch = window.fetch;
window.fetch = function(url, options) {
  return originalFetch(url, options)
    .then(response => {
      if (!response.ok) {
        console.error(`API error: ${url} returned ${response.status}`);
      }
      return response;
    })
    .catch(error => {
      console.error('Fetch error:', error);
      throw error;
    });
};

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [errorMessage, setErrorMessage] = useState('');
  const [showError, setShowError] = useState(false);

  // Global error handler for unhandled promise rejections
  useEffect(() => {
    const handleUnhandledRejection = (event) => {
      console.error('Unhandled rejection:', event.reason);
      setErrorMessage('An error occurred while communicating with the server. Please try again.');
      setShowError(true);
    };

    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    
    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  const handleCloseError = () => {
    setShowError(false);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard onNavigate={setActiveTab} />;
      case 'recommendations':
        return <Recommendations />;
      case 'transactions':
        return <Transactions />;
      case 'assistant':
        return <Assistant />;
      default:
        return <Dashboard onNavigate={setActiveTab} />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <MainLayout activeTab={activeTab} onTabChange={setActiveTab}>
          {renderContent()}
        </MainLayout>
        <Snackbar 
          open={showError} 
          autoHideDuration={6000} 
          onClose={handleCloseError}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
            {errorMessage}
          </Alert>
        </Snackbar>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
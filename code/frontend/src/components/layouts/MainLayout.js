// src/components/layout/MainLayout.js  
import React, { useState, useEffect } from 'react';
import { Box, Toolbar, CssBaseline } from '@mui/material';
import { useAuth } from '../../context/AuthContext';
import Sidebar from './Sidebar';
import Header from './Header';
import enhancedApiService from '../../services/enhanced-api.js';

const MainLayout = ({ children, activeTab, onTabChange }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userData, setUserData] = useState({
    name: 'User',
    accountNumber: '*****',
    balance: 0,
    riskProfile: 'Moderate',
    financialHealth: 'Good',
    sentiment: 'Neutral'
  });

  const { getUserId } = useAuth();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const userId = getUserId();
        console.log(`Fetching user profile for ${userId}`);
        const data = await enhancedApiService.getUserProfile(userId);
        console.log('Received user data:', data);
        
        // Safely extract and transform user data
        setUserData({
          name: data?.name || 'User',
          accountNumber: data?.financial_profile?.account_number || '*****',
          balance: data?.financial_profile?.balance || 0,
          riskProfile: data?.financial_profile?.risk_profile || 'Moderate',
          financialHealth: data?.financial_profile?.financial_health || 'Good',
          sentiment: data?.sentiment?.overall_sentiment || 'Neutral'
        });
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };

    fetchUserData();
  }, [getUserId]);

  // Commented out renderContent function is preserved as in your original code
  // const renderContent = () => {
  //   switch (activeTab) {
  //     case 'dashboard':
  //       return children.dashboard;
  //     case 'recommendations':
  //       return children.recommendations;
  //     case 'transactions':
  //       return children.transactions;
  //     case 'assistant':
  //       return children.assistant;
  //     default:
  //       return children.dashboard;
  //   }
  // };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <CssBaseline />
      <Header activeTab={activeTab} userData={userData} />
      <Sidebar 
        activeTab={activeTab}
        setActiveTab={onTabChange}
        open={sidebarOpen}
        setOpen={setSidebarOpen}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          backgroundColor: (theme) => theme.palette.grey[100],
          overflow: 'auto'  // Added overflow auto for better scrolling
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default MainLayout;
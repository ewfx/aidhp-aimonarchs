// src/components/layout/MainLayout.js
import React, { useState, useEffect } from 'react';
import { Box, Toolbar, CssBaseline } from '@mui/material';
import Sidebar from './Sidebar';
import Header from './Header';
import apiService from '../../services/api';

const MainLayout = ({ children }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userData, setUserData] = useState({
    name: '',
    accountNumber: '',
    balance: 0,
    riskProfile: '',
    financialHealth: '',
    sentiment: ''
  });

  // Fetch user data on component mount
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const data = await apiService.getUserProfile("user123");
        setUserData(data);
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };

    fetchUserData();
  }, []);

  // Determine which content to render based on activeTab
  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return children.dashboard;
      case 'recommendations':
        return children.recommendations;
      case 'transactions':
        return children.transactions;
      case 'assistant':
        return children.assistant;
      default:
        return children.dashboard;
    }
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <CssBaseline />
      <Header activeTab={activeTab} userData={userData} />
      <Sidebar 
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        open={sidebarOpen}
        setOpen={setSidebarOpen}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          backgroundColor: (theme) => theme.palette.grey[100]
        }}
      >
        <Toolbar />
        {renderContent()}
      </Box>
    </Box>
  );
};

export default MainLayout;
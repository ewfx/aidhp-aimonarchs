// src/pages/Dashboard.js
import React, { useState, useEffect } from 'react';
import { Grid, Box, CircularProgress } from '@mui/material';
import FinancialOverview from '../components/dashboard/FinancialOverview';
import AIInsights from '../components/dashboard/AIInsights';
import SpendingBreakdown from '../components/dashboard/SpendingBreakdown';
import IncomeExpensesChart from '../components/dashboard/IncomeExpensesChart';
import TopRecommendation from '../components/dashboard/TopRecommendation';
import apiService from '../services/api';
import { spendingData, transactionData } from '../services/mockData';

const Dashboard = ({ onNavigate }) => {
  const [userData, setUserData] = useState({
    name: '',
    accountNumber: '',
    income_bracket: '',
    riskProfile: '',
    financial_goals: '',
    risk_profile: '', 
    age:''
  });
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const userProfileData = await apiService.getUserProfile("user123");
        const recommendationsData = await apiService.getRecommendations("user123");
        
        setUserData(userProfileData);
        setRecommendations(recommendationsData);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleViewAllRecommendations = () => {
    onNavigate('recommendations');
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <FinancialOverview userData={userData} />
        </Grid>
        <Grid item xs={12} md={4}>
          <AIInsights />
        </Grid>
        <Grid item xs={12} md={4}>
          <SpendingBreakdown spendingData={spendingData} />
        </Grid>
      </Grid>
      
      <IncomeExpensesChart transactionData={transactionData} />
      
      {recommendations.length > 0 && (
        <TopRecommendation 
          recommendation={recommendations[0]} 
          onViewAll={handleViewAllRecommendations}
        />
      )}
    </Box>
  );
};

export default Dashboard;
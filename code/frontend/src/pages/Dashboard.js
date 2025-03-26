import React, { useState, useEffect } from 'react';
import { Grid, Box, CircularProgress } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import FinancialOverview from '../components/dashboard/FinancialOverview';
import AIInsights from '../components/dashboard/AIInsights';
import SpendingBreakdown from '../components/dashboard/SpendingBreakdown';
import IncomeExpensesChart from '../components/dashboard/IncomeExpensesChart';
import TopRecommendation from '../components/dashboard/TopRecommendation';
import AIGeneratedInsights from '../components/dashboard/AIGeneratedInsights';
// Import the enhanced API service instead of the regular one
import enhancedApiService from '../services/enhanced-api';
import { spendingData, transactionData } from '../services/mockData';

const Dashboard = ({ onNavigate }) => {
  const { getUserId } = useAuth();
  const [userData, setUserData] = useState({
    name: '',
    accountNumber: '',
    balance: 0,
    income_bracket: '',
    financial_goals: '',
    risk_profile: '', 
    age:''
  });
  const [recommendations, setRecommendations] = useState([]);
  const [insights, setInsights] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const userId = getUserId();
        
        // Try to fetch data from API
        try {
          const data = await enhancedApiService.getDashboardData(userId);
          setDashboardData(data);
        } catch (error) {
          console.error('Error fetching dashboard data:', error);
          // Fall back to mock data
        }
        
        try {
          const userProfileData = await enhancedApiService.getUserProfile(userId);
          setUserData(userProfileData);
        } catch (error) {
          console.error('Error fetching user profile:', error);
        }
        
        try {
          // Use enhanced recommendations instead of regular ones
          const recommendationsData = await enhancedApiService.getEnhancedRecommendations(userId);
          if (recommendationsData && recommendationsData.length > 0) {
            setRecommendations(recommendationsData);
          }
        } catch (error) {
          console.error('Error fetching recommendations:', error);
        }

        try {
          // Fetch user insights
          const insightsData = await enhancedApiService.getUserInsights(userId);
          if (insightsData && insightsData.length > 0) {
            setInsights(insightsData);
          }
        } catch (error) {
          console.error('Error fetching insights:', error);
        }
      } catch (error) {
        console.error('Error in fetchData:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [getUserId]);

  const handleViewAllRecommendations = () => {
    onNavigate('recommendations');
  };

  const handleRefreshInsights = async () => {
    try {
      const userId = getUserId();
      await enhancedApiService.refreshInsights(userId);
      // Fetch updated insights
      const insightsData = await enhancedApiService.getUserInsights(userId);
      if (insightsData && insightsData.length > 0) {
        setInsights(insightsData);
      }
    } catch (error) {
      console.error('Error refreshing insights:', error);
    }
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
          {insights.length > 0 ? (
            <AIGeneratedInsights insights={insights} onRefresh={handleRefreshInsights} />
          ) : (
            <AIInsights />
          )}
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
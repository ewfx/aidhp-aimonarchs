import React, { useState, useEffect } from 'react';
import { Grid, Box, Typography, CircularProgress, Button } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import SentimentCard from '../components/transactions/SentimentCard';
import TransactionList from '../components/transactions/TransactionList';
import PredictiveInsights from '../components/transactions/PredictiveInsights';
import EnhancedAnomalyCard from '../components/transactions/EnhancedAnomalyCard';
// Import enhanced API service
import enhancedApiService from '../services/enhanced-api';
import { recentTransactions } from '../services/mockData';

const Transactions = () => {
  const { getUserId } = useAuth();
  const [transactions, setTransactions] = useState(recentTransactions); // Default to mock data
  const [analytics, setAnalytics] = useState(null);
  const [sentiment, setSentiment] = useState('neutral'); // Default value
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshingAnomalies, setRefreshingAnomalies] = useState(false);
  
  useEffect(() => {
    const fetchTransactionData = async () => {
      try {
        setLoading(true);
        const userId = getUserId();
        
        // Fetch transaction history
        try {
          const transactionData = await enhancedApiService.getTransactionHistory(userId);
          if (transactionData && transactionData.length > 0) {
            setTransactions(transactionData);
          }
        } catch (error) {
          console.error('Error fetching transaction history:', error);
          // Already using mock data as default
        }
        
        // Fetch analytics
        try {
          const analyticsData = await enhancedApiService.getTransactionAnalytics(userId);
          setAnalytics(analyticsData);
        } catch (error) {
          console.error('Error fetching transaction analytics:', error);
        }
        
        // Fetch sentiment
        try {
          const sentimentData = await enhancedApiService.getSentimentAnalysis(userId);
          if (sentimentData && sentimentData.sentiment_analysis) {
            // Safely extract sentiment value with fallback
            setSentiment(sentimentData.sentiment_analysis.overall_sentiment || 'neutral');
          }
        } catch (error) {
          console.error('Error fetching sentiment analysis:', error);
          // Using default 'neutral' sentiment
        }

        // Fetch anomalies
        try {
          const anomaliesData = await enhancedApiService.getAnomalies(userId);
          if (anomaliesData && anomaliesData.length > 0) {
            setAnomalies(anomaliesData);
          }
        } catch (error) {
          console.error('Error fetching anomalies:', error);
        }
      } catch (error) {
        console.error('Error in fetchTransactionData:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchTransactionData();
  }, [getUserId]);

  const handleRefreshAnomalies = async () => {
    try {
      setRefreshingAnomalies(true);
      const userId = getUserId();
      
      // Use refresh=true parameter to force new anomaly detection
      const anomaliesData = await enhancedApiService.getAnomalies(userId, true);
      if (anomaliesData && anomaliesData.length > 0) {
        setAnomalies(anomaliesData);
      }
    } catch (error) {
      console.error('Error refreshing anomalies:', error);
    } finally {
      setRefreshingAnomalies(false);
    }
  };

  const handleAcknowledgeAnomaly = async (anomalyId) => {
    try {
      await enhancedApiService.acknowledgeAnomaly(anomalyId);
      // Update local state
      setAnomalies(prevAnomalies => 
        prevAnomalies.map(anomaly => 
          anomaly.anomaly_id === anomalyId 
            ? {...anomaly, is_acknowledged: true} 
            : anomaly
        )
      );
    } catch (error) {
      console.error('Error acknowledging anomaly:', error);
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
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom>Transaction Analysis</Typography>
        <Typography variant="body2" color="text.secondary">
          AI-powered insights from your spending patterns
        </Typography>
      </Box>
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <SentimentCard sentiment={sentiment} />
        </Grid>
        <Grid item xs={12} md={6}>
          <EnhancedAnomalyCard 
            anomalies={anomalies} 
            onRefresh={handleRefreshAnomalies}
            onAcknowledge={handleAcknowledgeAnomaly}
          />
        </Grid>
      </Grid>
      
      <TransactionList transactions={transactions} />
      
      <PredictiveInsights />
    </Box>
  );
};

export default Transactions;
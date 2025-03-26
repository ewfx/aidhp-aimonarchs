import React, { useState, useEffect } from 'react';
import { Box, Typography, CircularProgress, Button } from '@mui/material';
import { useAuth } from '../context/AuthContext';
import RecommendationCard from '../components/recommendations/RecommendationCard';
// Import enhanced API service and utils
import enhancedApiService from '../services/enhanced-api';
import { adaptRecommendationData } from '../utils';

const Recommendations = () => {
  const { getUserId } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        const userId = getUserId();
        console.log(`Fetching recommendations for user: ${userId}`);
        
        // Use enhanced recommendations instead of regular ones
        const data = await enhancedApiService.getEnhancedRecommendations(userId);
        console.log('Received recommendations data:', data);
        
        // Adapt the data to match the expected format
        const adaptedData = Array.isArray(data) 
          ? data.map(adaptRecommendationData)
          : [];
          
        console.log('Adapted recommendations data:', adaptedData);
        setRecommendations(adaptedData);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
      } finally {
        setLoading(false);
      }
    };
  
    fetchRecommendations();
  }, [getUserId]);

  const handleRefreshRecommendations = async () => {
    try {
      setRefreshing(true);
      const userId = getUserId();
      
      // Use refresh=true parameter to force new recommendations
      const data = await enhancedApiService.getEnhancedRecommendations(userId, true);
      
      // Adapt the data to match the expected format
      const adaptedData = Array.isArray(data) 
        ? data.map(adaptRecommendationData)
        : [];
      
      setRecommendations(adaptedData);
    } catch (error) {
      console.error('Error refreshing recommendations:', error);
    } finally {
      setRefreshing(false);
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
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Typography variant="h5" gutterBottom>Your Personalized Recommendations</Typography>
          <Typography variant="body2" color="text.secondary">
            Based on your financial profile, spending patterns, and goals
          </Typography>
        </div>
        <Button 
          variant="contained" 
          onClick={handleRefreshRecommendations}
          disabled={refreshing}
        >
          {refreshing ? 'Refreshing...' : 'Refresh Recommendations'}
        </Button>
      </Box>
      
      {recommendations.length > 0 ? (
        recommendations.map((recommendation, index) => (
          <RecommendationCard 
            key={recommendation.id || recommendation.recommendation_id || index} 
            recommendation={recommendation} 
          />
        ))
      ) : (
        <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', mt: 4 }}>
          No recommendations available at this time. Click "Refresh Recommendations" to generate new ones.
        </Typography>
      )}
    </Box>
  );
};

export default Recommendations;
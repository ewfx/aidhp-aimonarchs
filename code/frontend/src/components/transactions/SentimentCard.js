import React from 'react';
import { Card, CardContent, Typography, Box, Avatar } from '@mui/material';

const SentimentCard = ({ sentiment }) => {
  // Provide default value if sentiment is null or undefined
  const sentimentValue = sentiment || 'neutral';
  
  // Determine emoji based on sentiment - with null check
  const getEmoji = (sentimentStr) => {
    // Convert to lowercase safely and provide a default
    const sentimentLower = (sentimentStr || '').toLowerCase();
    
    switch(sentimentLower) {
      case 'positive':
        return '😊';
      case 'negative':
        return '😟';
      case 'neutral':
      default:
        return '😐';
    }
  };

  // Determine color based on sentiment - with null check
  const getColor = (sentimentStr) => {
    // Convert to lowercase safely and provide a default
    const sentimentLower = (sentimentStr || '').toLowerCase();
    
    switch(sentimentLower) {
      case 'positive':
        return 'success.light';
      case 'negative':
        return 'error.light';
      case 'neutral':
      default:
        return 'info.light';
    }
  };

  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Spending Sentiment</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Avatar 
            sx={{ 
              width: 56, 
              height: 56, 
              bgcolor: getColor(sentimentValue),
              fontSize: '1.5rem'
            }}
          >
            {getEmoji(sentimentValue)}
          </Avatar>
          <Box sx={{ ml: 2 }}>
            <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>
              {sentimentValue}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {sentimentValue === 'positive' 
                ? 'Your spending is balanced and sustainable' 
                : sentimentValue === 'negative'
                  ? 'You may want to review your spending habits'
                  : 'Your financial patterns are steady'}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default SentimentCard;
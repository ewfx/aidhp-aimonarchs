// src/components/transactions/SentimentCard.js
import React from 'react';
import { Card, CardContent, Typography, Box, Avatar } from '@mui/material';

const SentimentCard = ({ sentiment }) => {
  // Determine emoji based on sentiment
  const getEmoji = (sentiment) => {
    switch(sentiment.toLowerCase()) {
      case 'positive':
        return '😊';
      case 'negative':
        return '😟';
      case 'neutral':
        return '😐';
      default:
        return '😊';
    }
  };

  // Determine color based on sentiment
  const getColor = (sentiment) => {
    switch(sentiment.toLowerCase()) {
      case 'positive':
        return 'success.light';
      case 'negative':
        return 'error.light';
      case 'neutral':
        return 'info.light';
      default:
        return 'success.light';
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
              bgcolor: getColor(sentiment),
              fontSize: '1.5rem'
            }}
          >
            {getEmoji(sentiment)}
          </Avatar>
          <Box sx={{ ml: 2 }}>
            <Typography variant="h6" sx={{ textTransform: 'capitalize' }}>{sentiment}</Typography>
            <Typography variant="body2" color="text.secondary">
              Your spending is balanced and sustainable
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default SentimentCard;
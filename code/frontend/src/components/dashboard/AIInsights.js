// src/components/dashboard/AIInsights.js
import React from 'react';
import { Card, CardContent, Typography, Divider, Box, Button } from '@mui/material';
import { ArrowForward as ArrowForwardIcon } from '@mui/icons-material';

const AIInsights = () => {
  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" gutterBottom>AI Insights</Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2">
            Based on your spending patterns, you could save $320 monthly by reducing restaurant expenses.
          </Typography>
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2">
            You're on track to reach your emergency fund goal by September 2024.
          </Typography>
        </Box>
        
        <Button 
          endIcon={<ArrowForwardIcon />} 
          color="primary" 
          sx={{ mt: 1 }}
        >
          View all insights
        </Button>
      </CardContent>
    </Card>
  );
};

export default AIInsights;
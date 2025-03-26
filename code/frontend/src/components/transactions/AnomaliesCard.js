// src/components/transactions/AnomaliesCard.js
import React from 'react';
import { Card, CardContent, Typography, Box, Button } from '@mui/material';
import { ArrowForward as ArrowForwardIcon } from '@mui/icons-material';

const AnomaliesCard = () => {
  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Spending Anomalies</Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          We detected an unusual increase in Entertainment spending this month (+42% from average).
        </Typography>
        <Button 
          size="small" 
          endIcon={<ArrowForwardIcon />}
          color="primary"
        >
          View details
        </Button>
      </CardContent>
    </Card>
  );
};

export default AnomaliesCard;
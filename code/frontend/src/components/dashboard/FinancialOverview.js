// src/components/dashboard/FinancialOverview.js
import React from 'react';
import { Card, CardContent, Typography, Divider, Chip, Box } from '@mui/material';

const FinancialOverview = ({ userData }) => {
  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Financial Overview</Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">Current Balance</Typography>
          <Typography variant="h5" fontWeight="bold">${userData.balance}</Typography>
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">Risk Profile</Typography>
          <Typography variant="body1" color="primary.main" fontWeight="medium">{userData.riskProfile}</Typography>
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">Financial Health</Typography>
          <Chip 
            label={userData.financialHealth} 
            color="success" 
            size="small" 
            variant="outlined"
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default FinancialOverview;
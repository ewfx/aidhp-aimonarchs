// src/components/transactions/PredictiveInsights.js
import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Paper,
  List,
  ListItem,
  ListItemText,
  Button,
  Divider
} from '@mui/material';
import { upcomingExpenses } from '../../services/mockData';

const PredictiveInsights = () => {
  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Predictive Insights</Typography>
        
        <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Based on your pattern, we predict these upcoming expenses:
          </Typography>
          
          <List dense>
            {upcomingExpenses.map((expense) => (
              <ListItem key={expense.id} sx={{ py: 0 }}>
                <ListItemText primary={expense.description} />
                <Typography variant="body2" fontWeight="medium">
                  ${expense.amount.toFixed(2)} on {expense.date}
                </Typography>
              </ListItem>
            ))}
          </List>
        </Paper>
        
        <Paper 
          variant="outlined" 
          sx={{ p: 2, bgcolor: 'primary.light', color: 'primary.contrastText' }}
        >
          <Typography variant="subtitle2" gutterBottom>
            Opportunity: We notice you spend $245/month on subscriptions that you rarely use. Would you like to review them?
          </Typography>
          <Button 
            variant="contained" 
            size="small" 
            color="primary"
            sx={{ mt: 1 }}
          >
            Review now
          </Button>
        </Paper>
      </CardContent>
    </Card>
  );
};

export default PredictiveInsights;
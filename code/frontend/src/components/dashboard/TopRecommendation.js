// src/components/dashboard/TopRecommendation.js
import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Button, 
  Chip, 
  Divider,
  Paper
} from '@mui/material';
import { ArrowForward as ArrowForwardIcon } from '@mui/icons-material';

const TopRecommendation = ({ recommendation, onViewAll }) => {
  return (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Top Recommendation</Typography>
          <Button 
            endIcon={<ArrowForwardIcon />} 
            onClick={onViewAll}
            color="primary"
            size="small"
          >
            View all
          </Button>
        </Box>
        
        <Paper elevation={1} sx={{ p: 2, border: '1px solid #eee' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h6">{recommendation.title}</Typography>
              <Typography variant="caption" color="text.secondary">{recommendation.category}</Typography>
            </Box>
            <Chip 
              label={`${recommendation.score}% Match`} 
              color="primary" 
              size="small"
              sx={{ fontWeight: 'medium' }}
            />
          </Box>
          
          <Typography variant="body2" sx={{ my: 2 }}>{recommendation.reason}</Typography>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
            {recommendation.features.map((feature, index) => (
              <Chip 
                key={index} 
                label={feature} 
                size="small" 
                variant="outlined"
              />
            ))}
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button variant="contained" color="primary" fullWidth>
              Learn More
            </Button>
            <Button variant="outlined" color="primary">
              Not Interested
            </Button>
          </Box>
        </Paper>
      </CardContent>
    </Card>
  );
};

export default TopRecommendation;
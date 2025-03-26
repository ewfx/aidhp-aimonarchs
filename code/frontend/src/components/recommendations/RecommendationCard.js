// src/components/recommendations/RecommendationCard.js
import React, { useState } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Button, 
  Chip, 
  Divider,
  IconButton
} from '@mui/material';
import { 
  ThumbUp as ThumbUpIcon, 
  ThumbDown as ThumbDownIcon 
} from '@mui/icons-material';
import apiService from '../../services/api';

const RecommendationCard = ({ recommendation }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const handleFeedback = async (isHelpful) => {
    try {
      setIsSubmitting(true);
      await apiService.submitFeedback(recommendation.id, isHelpful);
      setFeedbackSubmitted(true);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card elevation={2} sx={{ mb: 3 }}>
      <CardContent>
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
        
        <Box sx={{ my: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Why we recommend this</Typography>
          <Typography variant="body2">{recommendation.reason}</Typography>
        </Box>
                
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="contained" color="primary" fullWidth>
            Learn More
          </Button>
          <Button variant="outlined" color="primary">
            Not Interested
          </Button>
        </Box>
        
        <Divider sx={{ my: 2 }} />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            {feedbackSubmitted 
              ? "Thanks for your feedback!" 
              : "Was this recommendation helpful?"}
          </Typography>
          {!feedbackSubmitted && (
            <Box>
              <IconButton 
                color="primary"
                onClick={() => handleFeedback(true)}
                disabled={isSubmitting}
              >
                <ThumbUpIcon />
              </IconButton>
              <IconButton 
                color="default"
                onClick={() => handleFeedback(false)}
                disabled={isSubmitting}
              >
                <ThumbDownIcon />
              </IconButton>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default RecommendationCard;
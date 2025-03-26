import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Button, 
  Chip, 
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions
} from '@mui/material';
import { 
  ThumbUp as ThumbUpIcon, 
  ThumbDown as ThumbDownIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import enhancedApiService from '../../services/enhanced-api.js';
import ReactMarkdown from 'react-markdown';

const RecommendationCard = ({ recommendation }) => {
  const { getUserId } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);

  const id = recommendation?.id || recommendation?.recommendation_id || 'rec-id';
  const title = recommendation?.title || recommendation?.product_name || 'Recommendation';
  const category = recommendation?.category || recommendation?.product_category || 'Financial Product';
  const score = recommendation?.score || 85;
  const reason = recommendation?.reason || 'This product matches your financial profile.';
  const features = recommendation?.features || [];
  const isViewed = recommendation?.is_viewed || false;
  const isClicked = recommendation?.is_clicked || false;
  const [isHelpful, setIsHelpful] = useState(null);

  const handleFeedback = async (isHelpfulFeedback) => {
    try {
      setIsSubmitting(true);
      await enhancedApiService.submitFeedback(id, isHelpfulFeedback);
      setFeedbackSubmitted(true);
      setIsHelpful(isHelpfulFeedback);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenDetails = () => {
    setDetailsOpen(true);
    if (!isClicked) {
      // enhancedApiService.trackRecommendationClick(id);
    }
  };

  const handleCloseDetails = () => setDetailsOpen(false);

  useEffect(() => {
    const trackView = async () => {
      if (!isViewed) {
        // await enhancedApiService.trackRecommendationView(id);
      }
    };
    trackView();
  }, [id, isViewed]);

  return (
    <Card elevation={2} sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="h6">{title}</Typography>
            <Typography variant="caption" color="text.secondary">{category}</Typography>
          </Box>
          <Chip 
            label={`${score}% Match`} 
            color="primary" 
            size="small"
            sx={{ fontWeight: 'medium' }}
          />
        </Box>
        
        <Box sx={{ my: 2 }}>
          {/* <Typography variant="subtitle2" gutterBottom></Typography> */}
          {/* <Typography variant="body2"><ReactMarkdown children={reason} /></Typography> */}
        </Box>
        
        {features && features.length > 0 && (
          <Box sx={{ my: 2 }}>
            <Typography variant="subtitle2" gutterBottom>Key Features</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {features.map((feature, index) => (
                <Chip 
                  key={index} 
                  label={feature} 
                  size="small" 
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            color="primary" 
            fullWidth
            onClick={handleOpenDetails}
          >
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
      
      <Dialog open={detailsOpen} onClose={handleCloseDetails}>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            {title}
            <IconButton onClick={handleCloseDetails}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent dividers>
          <Typography variant="subtitle1" gutterBottom>
            Product Details
          </Typography>
          <DialogContentText>
            {<ReactMarkdown children={reason} /> || 
             'Comprehensive financial solution designed for your needs.'}
          </DialogContentText>

          {features?.length > 0 && (
            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                Key Benefits:
              </Typography>
              <ul style={{ paddingLeft: 20, margin: 0 }}>
                {features.map((feature, index) => (
                  <li key={index}>
                    <Typography variant="body2">{feature}</Typography>
                  </li>
                ))}
              </ul>
            </Box>
          )}

          <Box mt={2}>
            <Typography variant="caption" color="text.secondary">
                These recommendations are generated by Artificial Intelligence and are prone to inaccuracies. 
            </Typography>
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseDetails} color="primary">
            Close
          </Button>
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => {
              handleCloseDetails();
              // Add your application logic here
            }}
          >
            Apply Now
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default RecommendationCard;

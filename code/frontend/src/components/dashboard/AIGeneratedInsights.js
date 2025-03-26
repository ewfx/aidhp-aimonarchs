// src/components/dashboard/AIGeneratedInsights.js
import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Chip, 
  Divider,
  Button,
  IconButton
} from '@mui/material';
import { 
  LightbulbOutlined as LightbulbIcon,
  CheckCircleOutline as CheckIcon,
  HighlightOff as CloseIcon
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import enhancedApiService from '../../services/enhanced-api.js';

const InsightItem = ({ insight, onMarkRead, onActionTaken }) => {
  const theme = useTheme();
  
  // Determine color based on importance
  const getColor = (importance) => {
    switch(importance?.toLowerCase()) {
      case 'high':
        return theme.palette.error.main;
      case 'medium':
        return theme.palette.warning.main;
      case 'low':
      default:
        return theme.palette.info.main;
    }
  };
  
  return (
    <Box sx={{ mb: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1, boxShadow: 1 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <LightbulbIcon 
            color="inherit" 
            sx={{ 
              mr: 1, 
              color: getColor(insight.importance)
            }} 
          />
          <Box>
            <Typography 
              variant="subtitle2" 
              component="div"
              sx={{ 
                fontWeight: insight.is_read ? 'normal' : 'bold',
                color: insight.is_read ? 'text.secondary' : 'text.primary'
              }}
            >
              {insight.category}
            </Typography>
            <Typography variant="body2">
              {insight.description}
            </Typography>
          </Box>
        </Box>
        
        {!insight.is_acted_upon && (
          <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
            <IconButton 
              size="small" 
              color="success"
              onClick={() => onActionTaken(insight, true)}
              title="Mark as actioned"
            >
              <CheckIcon fontSize="small" />
            </IconButton>
            <IconButton 
              size="small" 
              color="error"
              onClick={() => onActionTaken(insight, false)}
              title="Dismiss"
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        )}
      </Box>
      
      {insight.is_acted_upon !== null && (
        <Chip 
          label={insight.is_acted_upon ? "Actioned" : "Dismissed"} 
          size="small"
          color={insight.is_acted_upon ? "success" : "default"}
          variant="outlined"
          sx={{ mt: 1 }}
        />
      )}
    </Box>
  );
};

const AIGeneratedInsights = ({ insights, onRefresh }) => {
  const handleMarkRead = async (insight) => {
    try {
      await enhancedApiService.markInsightRead(insight.user_id, insight.insight_id);
      
      // This would typically trigger a refresh of insights from parent component
      if (onRefresh) {
        onRefresh();
      }
    } catch (error) {
      console.error('Error marking insight as read:', error);
    }
  };
  
  const handleActionTaken = async (insight, acted) => {
    try {
      await enhancedApiService.recordInsightAction(insight.user_id, insight.insight_id, acted);
      
      // This would typically trigger a refresh of insights from parent component
      if (onRefresh) {
        onRefresh();
      }
    } catch (error) {
      console.error('Error recording insight action:', error);
    }
  };
  
  // Filter out dismissed insights
  const visibleInsights = insights.filter(insight => insight.is_acted_upon !== false);
  
  return (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">AI-Generated Insights</Typography>
          <Button size="small" onClick={onRefresh}>
            Refresh
          </Button>
        </Box>
        
        {visibleInsights.length > 0 ? (
          visibleInsights.map((insight) => (
            <InsightItem 
              key={insight.insight_id} 
              insight={insight}
              onMarkRead={handleMarkRead}
              onActionTaken={handleActionTaken}
            />
          ))
        ) : (
          <Typography variant="body2" color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
            No financial insights available at this time.
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default AIGeneratedInsights;
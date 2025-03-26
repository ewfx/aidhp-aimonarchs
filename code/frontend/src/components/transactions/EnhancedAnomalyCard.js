// src/components/transactions/EnhancedAnomalyCard.js
import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Button,
  Alert,
  AlertTitle,
  LinearProgress,
  Collapse
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { 
  Error as ErrorIcon,
  ArrowUpward as ArrowUpIcon
} from '@mui/icons-material';
import enhancedApiService from '../../services/enhanced-api.js';

const EnhancedAnomalyCard = ({ anomalies, onRefresh, onAcknowledge }) => {
  const theme = useTheme();
  const [expanded, setExpanded] = React.useState(false);
  
  // Filter out acknowledged anomalies for initial display
  const unacknowledgedAnomalies = anomalies.filter(anomaly => !anomaly.is_acknowledged);
  
  const handleAcknowledge = async (anomalyId) => {
    try {
      await enhancedApiService.acknowledgeAnomaly(anomalyId);
      
      if (onAcknowledge) {
        onAcknowledge(anomalyId);
      }
    } catch (error) {
      console.error('Error acknowledging anomaly:', error);
    }
  };
  
  // Determine severity color
  const getSeverityColor = (severity) => {
    switch(severity?.toLowerCase()) {
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
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Spending Anomalies</Typography>
          <Button size="small" onClick={onRefresh}>
            Analyze
          </Button>
        </Box>
        
        {unacknowledgedAnomalies.length > 0 ? (
          <>
            {unacknowledgedAnomalies.slice(0, 1).map((anomaly) => (
              <Alert 
                key={anomaly.anomaly_id} 
                severity="warning"
                action={
                  <Button 
                    color="inherit" 
                    size="small"
                    onClick={() => handleAcknowledge(anomaly.anomaly_id)}
                  >
                    Acknowledge
                  </Button>
                }
                sx={{ mb: 2 }}
              >
                <AlertTitle>{anomaly.category}</AlertTitle>
                {anomaly.description}
              </Alert>
            ))}
            
            {unacknowledgedAnomalies.length > 1 && (
              <>
                <Button 
                  size="small" 
                  variant="text" 
                  onClick={() => setExpanded(!expanded)}
                  startIcon={<ArrowUpIcon sx={{ transform: expanded ? 'rotate(180deg)' : 'none' }}/>}
                  sx={{ mb: 2 }}
                >
                  {expanded ? 'Hide' : 'Show'} {unacknowledgedAnomalies.length - 1} more anomalies
                </Button>
                
                <Collapse in={expanded}>
                  {unacknowledgedAnomalies.slice(1).map((anomaly) => (
                    <Alert 
                      key={anomaly.anomaly_id} 
                      severity="warning"
                      action={
                        <Button 
                          color="inherit" 
                          size="small"
                          onClick={() => handleAcknowledge(anomaly.anomaly_id)}
                        >
                          Acknowledge
                        </Button>
                      }
                      sx={{ mb: 2 }}
                    >
                      <AlertTitle>{anomaly.category}</AlertTitle>
                      {anomaly.description}
                    </Alert>
                  ))}
                </Collapse>
              </>
            )}
          </>
        ) : (
          <Typography variant="body2" sx={{ mb: 2 }}>
            No unusual spending patterns detected.
          </Typography>
        )}
        
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
          <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
            Last analyzed: 2 hours ago
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={70} 
            sx={{ flexGrow: 1, height: 4, borderRadius: 1 }} 
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default EnhancedAnomalyCard;
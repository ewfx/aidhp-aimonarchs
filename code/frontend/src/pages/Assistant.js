// src/pages/Assistant.js
import React from 'react';
import { Box } from '@mui/material';
// Import the EnhancedChatInterface instead of regular ChatInterface
import EnhancedChatInterface from '../components/assistant/EnhancedChatInterface';

const Assistant = () => {
  return (
    <Box sx={{ height: 'calc(100vh - 140px)' }}>
      <EnhancedChatInterface />
    </Box>
  );
};

export default Assistant;
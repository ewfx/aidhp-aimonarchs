// src/pages/Assistant.js
import React from 'react';
import { Box } from '@mui/material';
import ChatInterface from '../components/assistant/ChatInterface';

const Assistant = () => {
  return (
    <Box sx={{ height: 'calc(100vh - 140px)' }}>
      <ChatInterface />
    </Box>
  );
};

export default Assistant;
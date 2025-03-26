// src/components/assistant/ChatMessage.js
import React from 'react';
import { Box, Paper, Typography, Avatar } from '@mui/material';
import { Person as PersonIcon, SmartToy as SmartToyIcon } from '@mui/icons-material';

const ChatMessage = ({ message }) => {
  const isUser = message.sender === 'user';
  
  return (
    <Box 
      sx={{ 
        display: 'flex', 
        justifyContent: isUser ? 'flex-start' : 'flex-end',
        mb: 2
      }}
    >
      {isUser && (
        <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
          <PersonIcon fontSize="small" />
        </Avatar>
      )}
      
      <Paper 
        elevation={1}
        sx={{ 
          p: 2, 
          maxWidth: '80%',
          bgcolor: isUser ? 'background.paper' : 'primary.main',
          color: isUser ? 'text.primary' : 'primary.contrastText'
        }}
      >
        <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
          {message.text}
        </Typography>
      </Paper>
      
      {!isUser && (
        <Avatar sx={{ ml: 1, bgcolor: 'primary.dark' }}>
          <SmartToyIcon fontSize="small" />
        </Avatar>
      )}
    </Box>
  );
};

export default ChatMessage;
// src/components/assistant/ChatInterface.js
import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  TextField, 
  Button,
  CircularProgress
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ChatMessage from './ChatMessage';
import enhancedApiService from '../../services/enhanced-api.js';
import { useAuth } from '../../context/AuthContext';

const ChatInterface = () => {
  const { getUserId } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);
//   const { getUserId } = useAuth();
// useEffect(() => {
//   apiService.initAuth({ getUserId });
// }, [getUserId]);
  // Fetch chat history
  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        setLoading(true);
        const userId = getUserId();
        const history = await enhancedApiService.getChatHistory(userId);
        setMessages(history);
      } catch (error) {
        console.error('Error fetching chat history:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchChatHistory();
  }, [getUserId]);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim()) return;
    
    const userId = getUserId();
    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: inputMessage
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setSending(true);
    
    try {
      const response = await enhancedApiService.sendMessage(userId, inputMessage);
      setMessages(prev => [...prev, {
        id: response.id,
        sender: 'assistant',
        text: response.text
      }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now(),
          sender: 'assistant',
          text: 'Sorry, I encountered an error. Please try again.'
        }
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <Paper elevation={2} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">AI Financial Assistant</Typography>
        <Typography variant="body2" color="text.secondary">
          Ask any question about your finances or get personalized advice
        </Typography>
      </Box>
      
      <Box sx={{ 
        flex: 1, 
        p: 2, 
        overflow: 'auto',
        bgcolor: 'grey.50'
      }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {sending && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                <CircularProgress size={24} />
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>
        )}
      </Box>
      
      <Box 
        component="form" 
        onSubmit={handleSendMessage}
        sx={{ 
          p: 2, 
          borderTop: 1, 
          borderColor: 'divider',
          display: 'flex' 
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          placeholder="Ask something about your finances..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          disabled={sending}
          sx={{ mr: 1 }}
        />
        <Button 
          type="submit" 
          variant="contained" 
          endIcon={<SendIcon />}
          disabled={sending || !inputMessage.trim()}
        >
          Send
        </Button>
      </Box>
    </Paper>
  );
};

export default ChatInterface;
import React, { useState, useRef, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  TextField, 
  Button,
  CircularProgress,
  Chip
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ChatMessage from './ChatMessage';
import enhancedApiService  from '../../services/enhanced-api';
import { useAuth } from '../../context/AuthContext';

const EnhancedChatInterface = () => {
  const { getUserId } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [typingText, setTypingText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const [relatedInsights, setRelatedInsights] = useState([]);

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

  // Simulate typing effect with parts of the message
  useEffect(() => {
    if (isTyping && typingText) {
      const messageParts = typingText.split(' ');
      let currentIndex = 0;
      let currentText = ''; // Keep track of the current text
      
      const typingInterval = setInterval(() => {
        if (currentIndex < messageParts.length) {
          const wordCount = Math.min(3, messageParts.length - currentIndex);
          const nextWords = messageParts.slice(currentIndex, currentIndex + wordCount).join(' ');
          
          // Update currentText
          currentText += (currentText ? ' ' : '') + nextWords;
          
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            
            if (lastMessage && lastMessage.sender === 'assistant' && lastMessage.isTyping) {
              lastMessage.text = currentText; // Update the text directly
            } else {
              newMessages.push({
                id: Date.now(),
                sender: 'assistant',
                text: currentText,
                isTyping: true
              });
            }
            
            return newMessages;
          });
          
          currentIndex += wordCount;
        } else {
          // Finished typing
          setIsTyping(false);
          setTypingText('');
          
          // Update the last message to remove typing indicator
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            
            if (lastMessage && lastMessage.isTyping) {
              lastMessage.isTyping = false;
            }
            
            return newMessages;
          });
          
          clearInterval(typingInterval);
        }
      }, 100); // Adjust speed as needed
      
      return () => clearInterval(typingInterval);
    }
  }, [isTyping, typingText]);
  

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
      // Use the streaming response from the enhanced API
      const fullResponse = await enhancedApiService.sendMessageStreaming(userId, inputMessage);
      console.log(fullResponse)
      // Set the typing effect
      setTypingText(fullResponse.data.text);
      setIsTyping(true);
      
      // // Update related insights if any
      // if (insights && insights.length > 0) {
      //   setRelatedInsights(insights);
      // }
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
        <Typography variant="h6">GenAI Financial Assistant</Typography>
        <Typography variant="body2" color="text.secondary">
          Ask any question about your finances or get personalized advice
        </Typography>
      </Box>
      
      <Box sx={{ 
        flex: 1, 
        p: 2, 
        overflow: 'auto',
        bgcolor: 'grey.50',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box sx={{ flex: 1 }}>
            {messages.map((message) => (
              <ChatMessage 
                key={message.id} 
                message={message} 
                isTyping={message.isTyping}
              />
            ))}
            {sending && !isTyping && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                <CircularProgress size={24} />
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>
        )}
        
        {relatedInsights.length > 0 && (
          <Box sx={{ mt: 2, p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="subtitle2" gutterBottom>Related Insights:</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {relatedInsights.map((insight, index) => (
                <Chip 
                  key={index}
                  label={insight.description}
                  variant="outlined"
                  color="primary"
                  size="small"
                  sx={{ maxWidth: '100%', height: 'auto', '& .MuiChip-label': { whiteSpace: 'normal', py: 0.5 } }}
                />
              ))}
            </Box>
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
          disabled={sending || isTyping}
          sx={{ mr: 1 }}
        />
        <Button 
          type="submit" 
          variant="contained" 
          endIcon={<SendIcon />}
          disabled={sending || isTyping || !inputMessage.trim()}
        >
          Send
        </Button>
      </Box>
    </Paper>
  );
};

export default EnhancedChatInterface;

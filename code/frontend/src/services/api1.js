import axios from 'axios';
import { userData, recommendations, transactionData, recentTransactions, chatMessages } from './mockData';

// API base URL
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper function to get user ID from localStorage
const getUserId = () => {
  return localStorage.getItem('userId') || 'user123';
};

// Set a default user ID if none exists (for hackathon simplicity)
if (!localStorage.getItem('userId')) {
  localStorage.setItem('userId', 'user123');
}

// Helper function to get auth headers
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// API service functions
const apiService = {
  // User data
  getUserProfile: async (specificUserId = null) => {
    try {
      const userId = specificUserId || getUserId();
      const response = await api.get(`/users/${userId}`, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching user profile:', error);
      return userData; // Fallback to mock data
    }
  },
  
  // Dashboard data
  getDashboardData: async (specificUserId = null) => {
    try {
      const userId = specificUserId || getUserId();
      const response = await api.get(`/dashboard/${userId}`, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      
      // Fallback to mock data
      return {
        user: userData,
        top_recommendation: recommendations[0],
        spending_breakdown: {
          'Housing': 35,
          'Food': 20,
          'Transportation': 15,
          'Entertainment': 10,
          'Other': 20
        },
        chart_data: transactionData
      };
    }
  },
  
  // Recommendations
  getRecommendations: async (specificUserId = null) => {
    try {
      const userId = specificUserId || getUserId();
      const response = await api.get(`/recommendations/${userId}`, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      return recommendations; // Fallback to mock data
    }
  },
  
  // Submit recommendation feedback
  submitFeedback: async (recommendationId, isHelpful) => {
    try {
      const response = await api.post(
        `/recommendations/${recommendationId}/feedback`, 
        { is_helpful: isHelpful },
        { headers: getAuthHeader() }
      );
      return response.data;
    } catch (error) {
      console.error('Error submitting feedback:', error);
      return { status: 'success' }; // Mock success for hackathon
    }
  },
  
  // Transaction data
  getTransactionHistory: async (specificUserId = null, limit = 50) => {
    try {
      const userId = specificUserId || getUserId();
      const response = await api.get(`/transactions/${userId}?limit=${limit}`, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching transactions:', error);
      return recentTransactions; // Fallback to mock data
    }
  },
  
  // Transaction analytics
  getTransactionAnalytics: async (specificUserId = null, months = 6) => {
    try {
      const userId = specificUserId || getUserId();
      const response = await api.get(`/transactions/${userId}/analytics?months=${months}`, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching transaction analytics:', error);
      return { monthly_data: transactionData }; // Fallback to mock data
    }
  },
  
  // Sentiment analysis
  getSentimentAnalysis: async (specificUserId = null) => {
    try {
      const userId = specificUserId || getUserId();
      const response = await api.get(`/transactions/${userId}/sentiment`, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching sentiment analysis:', error);
      
      // Mock response
      return {
        user_id: userId,
        sentiment_analysis: {
          overall_sentiment: userData.sentiment.toLowerCase(),
          confidence: 0.87,
          financial_health: userData.financialHealth.toLowerCase()
        }
      };
    }
  },
  
  // AI Assistant
  getChatHistory: async (specificUserId = null) => {
    try {
      const userId = specificUserId || getUserId();
      const response = await api.get(`/chat/${userId}/history`, {
        headers: getAuthHeader()
      });
      
      // Transform to expected format if needed
      const messages = response.data.map(msg => ({
        id: msg.message_id || msg.id,
        sender: msg.sender,
        text: msg.text
      }));
      
      return messages;
    } catch (error) {
      console.error('Error fetching chat history:', error);
      return chatMessages; // Fallback to mock data
    }
  },
  
  // Send message to AI assistant
  sendMessage: async (userId, messageText) => {
    try {
      userId = userId || getUserId();
      const response = await api.post(`/chat/${userId}/message`, 
        { message: messageText },
        { headers: getAuthHeader() }
      );
      
      // Transform to expected format
      return {
        id: response.data.message_id || Date.now(),
        sender: "assistant",
        text: response.data.text || "I'll analyze that and get back to you shortly."
      };
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Mock response for hackathon
      return {
        id: Date.now(),
        sender: "assistant",
        text: "I'll analyze that and get back to you shortly."
      };
    }
  },
  
  // Auth methods
  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login', { username: email, password });
      const { access_token, user_id } = response.data;
      
      // Store token and user ID
      localStorage.setItem('token', access_token);
      localStorage.setItem('userId', user_id);
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      
      // For hackathon, mock successful login
      localStorage.setItem('userId', 'user123');
      return true;
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
    // Don't remove userId for the hackathon to keep testing simple
  }
};

export default apiService;
// src/services/api.js
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

// API service functions
const apiService = {
  // User data
  getUserProfile: async (userId) => {
    try {
      // When backend is ready:
      const response = await api.get(`/users/${userId}`);
      return response.data;
      
      // Using mock data for now
      // return userData;
    } catch (error) {
      console.error('Error fetching user profile:', error);
      return userData; // Fallback to mock data
    }
  },
  
  // Recommendations
  getRecommendations: async (userId) => {
    try {
      // When backend is ready:
      const response = await api.get(`/recommendations/${userId}`);
      return response.data;
      
      // Using mock data for now
      return recommendations;
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      return recommendations; // Fallback to mock data
    }
  },
  
  // Submit recommendation feedback
  submitFeedback: async (recommendationId, isHelpful) => {
    try {
      // When backend is ready:
      const response = await api.post(`/recommendations/${recommendationId}/feedback`, {
        is_clicked: isHelpful
      });
      return response.data;
      
      // Mock response
      // return { status: 'success' };
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  },
  
  // Transaction data
  getTransactionHistory: async (userId) => {
    try {
      // When backend is ready:
      // const response = await api.get(`/transactions/${userId}`);
      // return response.data;
      
      // Using mock data for now
      return recentTransactions;
    } catch (error) {
      console.error('Error fetching transactions:', error);
      return recentTransactions; // Fallback to mock data
    }
  },
  
  // Transaction analytics
  getTransactionAnalytics: async (userId) => {
    try {
      // When backend is ready:
      // const response = await api.get(`/transactions/${userId}/analytics`);
      // return response.data;
      
      // Using mock data for now
      return transactionData;
    } catch (error) {
      console.error('Error fetching transaction analytics:', error);
      return transactionData; // Fallback to mock data
    }
  },
  
  // Sentiment analysis
  getSentimentAnalysis: async (userId) => {
    try {
      // When backend is ready:
      const response = await api.get(`/sentiment/${userId}`);
      return response.data;
      
      // Mock response
      return {
        user_id: userId,
        sentiment_analysis: {
          overall_sentiment: userData.sentiment.toLowerCase(),
          confidence: 0.87,
          financial_health: userData.financialHealth.toLowerCase()
        }
      };
    } catch (error) {
      console.error('Error fetching sentiment analysis:', error);
      throw error;
    }
  },
  
  // AI Assistant
  getChatHistory: async (userId) => {
    try {
      // When backend is ready:
      // const response = await api.get(`/chat/${userId}/history`);
      // return response.data;
      
      // Using mock data for now
      return chatMessages;
    } catch (error) {
      console.error('Error fetching chat history:', error);
      return chatMessages; // Fallback to mock data
    }
  },
  
  // Send message to AI assistant
  sendMessage: async (userId, message) => {
    try {
      // When backend is ready:
      // const response = await api.post(`/chat/${userId}/message`, { message });
      // return response.data;
      
      // Mock response
      return {
        id: Date.now(),
        sender: "assistant",
        text: "I'll analyze that and get back to you shortly."
      };
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }
};

export default apiService;
import axios from 'axios';
import { userData, recommendations, transactionData, chatMessages } from './mockData';

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


if (!localStorage.getItem('userId')) {
  localStorage.setItem('userId', 'user123');
}

// Helper function to get auth headers
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// Mock event source for streaming responses
class MockEventSource {
  constructor(url) {
    this.url = url;
    this.onmessage = null;
    this.onerror = null;
    this.onopen = null;
    this.readyState = 0; // 0 = CONNECTING, 1 = OPEN, 2 = CLOSED
    
    // Simulate connection
    setTimeout(() => {
      this.readyState = 1;
      if (this.onopen) this.onopen();
    }, 100);
  }
  
  close() {
    this.readyState = 2;
  }
  
  // Method to simulate streaming data
  simulateStream(response) {
    const words = response.split(' ');
    let currentIndex = 0;
    
    const sendNextChunk = () => {
      if (currentIndex >= words.length) {
        // End of stream
        if (this.onmessage) {
          this.onmessage({ data: '[DONE]' });
        }
        return;
      }
      
      // Send 1-3 words at a time
      const wordsToSend = Math.min(3, words.length - currentIndex);
      const chunk = words.slice(currentIndex, currentIndex + wordsToSend).join(' ');
      
      if (this.onmessage) {
        this.onmessage({ data: chunk });
      }
      
      currentIndex += wordsToSend;
      
      // Schedule next chunk
      setTimeout(sendNextChunk, 150);
    };
    
    // Start streaming
    sendNextChunk();
  }
}

// Extended API service with GenAI capabilities
const enhancedApiService = {

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
  
  // Dashboard data with enhanced insights
  getDashboardData: async (specificUserId = null) => {
    try {
      const userId = specificUserId || getUserId();
      const response = await api.get(`/dashboard/${userId}`, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      
      // Fallback to mock data with enhanced fields
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
        chart_data: transactionData,
        // Add AI-generated insights
        insights: [
          {
            insight_id: "ins1",
            category: "spending",
            description: "Your dining expenses have increased by 22% this month compared to your 3-month average.",
            importance: "medium",
            created_at: new Date().toISOString(),
            is_read: false,
            is_acted_upon: null
          },
          {
            insight_id: "ins2",
            category: "savings",
            description: "At your current savings rate, you'll reach your emergency fund goal in approximately 7 months.",
            importance: "high",
            created_at: new Date().toISOString(),
            is_read: false,
            is_acted_upon: null
          }
        ]
      };
    }
  },
  
  // Enhanced Recommendations
  getEnhancedRecommendations: async (specificUserId = null, refresh = false) => {
    try {
      const userId = specificUserId || getUserId();
      const endpoint = `/enhanced-recommendations/${userId}${refresh ? '?refresh=true' : ''}`;
      
      const response = await api.get(endpoint, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching enhanced recommendations:', error);
      
      // Fallback to mock data with enhanced details
      return recommendations.map(rec => ({
        ...rec,
        reason: rec.reason + " This recommendation is based on your recent transactions and financial goals.",
        metadata: {
          genai_generated: true,
          generation_time: new Date().toISOString()
        }
      }));
    }
  },
  
  // Compare recommendations
  compareRecommendations: async (recommendationIds) => {
    try {
      const response = await api.post(
        '/enhanced-recommendations/compare',
        { recommendation_ids: recommendationIds },
        { headers: getAuthHeader() }
      );
      return response.data;
    } catch (error) {
      console.error('Error comparing recommendations:', error);
      
      // Mock comparison data
      return {
        recommendations: recommendationIds.map(id => recommendations.find(r => r.id.toString() === id) || {}),
        comparison_points: [
          {
            name: "Interest Rate",
            description: "Annual interest rate or yield",
            values: recommendationIds.reduce((acc, id, index) => {
              acc[id] = (3 + index * 0.5).toFixed(2) + '%';
              return acc;
            }, {})
          },
          {
            name: "Fees",
            description: "Monthly or annual fees",
            values: recommendationIds.reduce((acc, id, index) => {
                acc[id] = '$' + (index * 5).toFixed(2);
              return acc;
            }, {})
          }
        ],
        recommendation: "Based on your profile, Option A provides better long-term value despite higher fees."
      };
    }
  },
  
  // AI Insights
  getUserInsights: async (specificUserId = null) => {
    try {
      const userId = specificUserId || getUserId();
      const response = await api.get(`/insights/${userId}`, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching user insights:', error);
      
      // Mock insights data
      return [
        {
          insight_id: "ins1",
          category: "spending",
          description: "Your dining expenses have increased by 22% this month compared to your 3-month average.",
          importance: "medium",
          created_at: new Date().toISOString(),
          is_read: false,
          is_acted_upon: null
        },
        {
          insight_id: "ins2",
          category: "savings",
          description: "At your current savings rate, you'll reach your emergency fund goal in approximately 7 months.",
          importance: "high",
          created_at: new Date().toISOString(),
          is_read: false,
          is_acted_upon: null
        },
        {
          insight_id: "ins3",
          category: "investment",
          description: "Your portfolio allocation is weighted heavily towards tech stocks. Consider diversifying to reduce risk.",
          importance: "high",
          created_at: new Date().toISOString(),
          is_read: true,
          is_acted_upon: true
        }
      ];
    }
  },
  
  refreshInsights: async (specificUserId = null) => {
    const userId = specificUserId || getUserId();
    try {
      const response = await api.post(`/insights/${userId}/refresh`, {}, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error refreshing insights:', error);
      return { status: "Insight generation started", user_id: userId };
    }
  },
  
  markInsightRead: async (userId, insightId) => {
    try {
      const response = await api.post(
        `/insights/${userId}/insight/${insightId}/read`,
        {},
        { headers: getAuthHeader() }
      );
      return response.data;
    } catch (error) {
      console.error('Error marking insight as read:', error);
      return { status: "success" };
    }
  },
  
  recordInsightAction: async (userId, insightId, actedUpon) => {
    try {
      const response = await api.post(
        `/insights/${userId}/insight/${insightId}/action`,
        { acted_upon: actedUpon },
        { headers: getAuthHeader() }
      );
      return response.data;
    } catch (error) {
      console.error('Error recording insight action:', error);
      return { status: "success" };
    }
  },
  
  // Transaction Intelligence
  getAnomalies: async (specificUserId = null, refresh = false) => {
    try {
      const userId = specificUserId || getUserId();
      const endpoint = `/transaction-intelligence/${userId}/anomalies${refresh ? '?refresh=true' : ''}`;
      
      const response = await api.get(endpoint, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching anomalies:', error);
      
      // Mock anomalies
      return [
        {
          anomaly_id: "ano1",
          category: "Entertainment",
          description: "Entertainment spending is 45% higher than your monthly average",
          severity: "medium",
          amount: 245.50,
          detection_date: new Date().toISOString(),
          is_acknowledged: false
        },
        {
          anomaly_id: "ano2",
          category: "Subscription",
          description: "Three new subscription services detected this month totaling $35.97",
          severity: "low",
          amount: 35.97,
          detection_date: new Date().toISOString(),
          is_acknowledged: false
        }
      ];
    }
  },
  
  acknowledgeAnomaly: async (anomalyId) => {
    try {
      // Extract userId from anomalyId or use default
      const userId = getUserId();
      
      const response = await api.post(
        `/transaction-intelligence/${userId}/acknowledge-anomaly/${anomalyId}`,
        {},
        { headers: getAuthHeader() }
      );
      return response.data;
    } catch (error) {
      console.error('Error acknowledging anomaly:', error);
      return { status: "success" };
    }
  },
  
  getPredictedExpenses: async (specificUserId = null, refresh = false) => {
    try {
      const userId = specificUserId || getUserId();
      const endpoint = `/transaction-intelligence/${userId}/predicted-expenses${refresh ? '?refresh=true' : ''}`;
      
      const response = await api.get(endpoint, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching predicted expenses:', error);
      
      // Mock predicted expenses
      return [
        {
          expense_id: "exp1",
          description: "Rent payment",
          amount: 1850.00,
          due_date: new Date(new Date().getTime() + 5 * 24 * 60 * 60 * 1000).toISOString(),
          category: "Housing",
          confidence: 0.95,
          is_recurring: true
        },
        {
          expense_id: "exp2",
          description: "Car insurance",
          amount: 128.75,
          due_date: new Date(new Date().getTime() + 10 * 24 * 60 * 60 * 1000).toISOString(),
          category: "Insurance",
          confidence: 0.92,
          is_recurring: true
        },
        {
          expense_id: "exp3",
          description: "Netflix subscription",
          amount: 15.99,
          due_date: new Date(new Date().getTime() + 15 * 24 * 60 * 60 * 1000).toISOString(),
          category: "Entertainment",
          confidence: 0.98,
          is_recurring: true
        }
      ];
    }
  },
  
  // Enhanced Chat with streaming
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
  
  getTransactionHistory: async (specificUserId = null, limit = 50) => {
    try {
      const userId = specificUserId || getUserId();
      const response = await api.get(`/transactions/${userId}?limit=${limit}`, {
        headers: getAuthHeader()
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching transactions:', error);
      return transactionData; // Fallback to mock data
    }
  },

  sendMessageStreaming: async (userId, messageText) => {
    try {
      // In a real implementation, this would use Server-Sent Events (SSE)
      // For the mockup, we'll simulate streaming
      
      // First, check if the real API endpoint is available
      try {
        // const streamingUrl = `${API_BASE_URL}/chat/${userId}/message/stream?message=${encodeURIComponent(messageText)}`;
        // const eventSource = new EventSource(streamingUrl);
        
        const response= api.post(`/chat/${userId}/message`, 
          { message: messageText },
          { headers: getAuthHeader() }
        ); 
        console.log(response)
        return response;
        // return new Promise((resolve, reject) => {
        //   let fullResponse = '';
          
        //   eventSource.onmessage = (event) => {
        //     if (event.data === '[DONE]') {
        //       eventSource.close();
        //       resolve({ 
        //         fullResponse, 
        //         insights: [] // No insights in this case
        //       });
        //     } else {
        //       fullResponse += event.data;
        //     }
        //   };
        //   console.log(fullResponse)
        //   eventSource.onerror = (error) => {
        //     eventSource.close();
        //     reject(error);
        //   };
        //   // Send the message to start the stream
        //   api.post(`/chat/${userId}/message`, 
        //     { message: messageText },
        //     { headers: getAuthHeader() }
        //   ); 
        // });
      } catch (error) {
        // Fall back to mock streaming
        console.log('Using mock streaming implementation');
        
        // Simulate response - in real implementation, this would come from the server
        const mockResponse = getAIResponse(messageText);
        const mockEventSource = new MockEventSource('mock-url');
        
        return new Promise((resolve) => {
          let fullResponse = '';
          
          mockEventSource.onmessage = (event) => {
            if (event.data === '[DONE]') {
              mockEventSource.close();
              
              // Generate some mock insights based on the message
              const insights = generateInsightsFromMessage(messageText);
              
              resolve({ fullResponse, insights });
            } else {
              fullResponse += event.data;
            }
          };
          
          // Start mock streaming
          mockEventSource.simulateStream(mockResponse);
        });
      }
    } catch (error) {
      console.error('Error in streaming message:', error);
      
      // Return a basic response
      return { 
        fullResponse: "I'll analyze that and get back to you shortly.",
        insights: []
      };
    }
  }
};

// Helper function to generate a mock AI response based on user message
function getAIResponse(message) {
  const messageLower = message.toLowerCase();
  
  // Simple pattern matching for different financial questions
  if (messageLower.includes('spend') || messageLower.includes('spending')) {
    return "Based on your transaction history, you've spent $428 on dining this month, which is 15% higher than your 3-month average. Your overall spending is still within your monthly budget of $3,200. Would you like to see a breakdown of your spending by category?";
  } else if (messageLower.includes('save') || messageLower.includes('saving')) {
    return "You're currently saving about $650 per month, which is 12% of your income. Financial experts typically recommend saving 15-20% of your income. At your current rate, you'll reach your emergency fund goal of $10,000 in approximately 7 months. Would you like some suggestions to increase your savings rate?";
  } else if (messageLower.includes('invest') || messageLower.includes('investment')) {
    return "Your investment portfolio has a current value of $45,200, with an allocation of 70% stocks, 20% bonds, and 10% cash. This is slightly more aggressive than the recommended allocation for someone with your moderate risk profile. Based on your goals and time horizon, I'd suggest increasing your bond allocation to 30% to better balance risk and return.";
  } else if (messageLower.includes('goal') || messageLower.includes('target')) {
    return "You have 3 active financial goals: Emergency Fund (60% complete), Home Down Payment (25% complete), and Retirement Savings (on track). Based on your current savings rate and investment returns, you're projected to reach your home down payment goal in 2.5 years, which aligns with your target timeline.";
  } else {
    return "I've analyzed your financial situation and can see you've made good progress on your emergency fund goal. Your income has been stable over the past 6 months, and your spending habits show discipline in most categories. One area to watch is your entertainment spending, which has increased by 18% recently. Would you like me to suggest some strategies to optimize this category?";
  }
}

// Helper function to generate mock insights based on user message
function generateInsightsFromMessage(message) {
  const messageLower = message.toLowerCase();
  const insights = [];
  
  if (messageLower.includes('spend') || messageLower.includes('budget')) {
    insights.push({
      description: "Entertainment spending increased 18% in the last 30 days",
      category: "spending"
    });
  }
  
  if (messageLower.includes('save') || messageLower.includes('emergency')) {
    insights.push({
      description: "At current rate, you'll reach your emergency fund goal in 7 months",
      category: "savings"
    });
  }
  
  if (messageLower.includes('invest') || messageLower.includes('stock')) {
    insights.push({
      description: "Your portfolio is weighted 15% higher in tech stocks than recommended",
      category: "investment"
    });
  }
  
  // Always return at least one insight for demo purposes
  if (insights.length === 0) {
    insights.push({
      description: "Your recurring expenses account for 65% of your monthly spending",
      category: "budget"
    });
  }
  
  return insights;
}

export default enhancedApiService;
import React, { createContext, useState, useEffect, useContext } from 'react';

// Create context
const AuthContext = createContext(null);

// Create provider component
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // For the hackathon, let's use a hardcoded user ID
    // In a real app, this would come from an API call after login
    const defaultUserId = localStorage.getItem('userId') || 'user123';
    
    // Store in localStorage for persistence
    localStorage.setItem('userId', defaultUserId);
    
    setCurrentUser({ userId: defaultUserId });
    setLoading(false);
  }, []);

  // Function to get user ID
  const getUserId = () => currentUser?.userId || 'user123';

  // Function for login (simplified)
  const login = (userId) => {
    localStorage.setItem('userId', userId);
    setCurrentUser({ userId });
  };

  // Function for logout
  const logout = () => {
    localStorage.removeItem('userId');
    setCurrentUser(null);
  };

  return (
    <AuthContext.Provider value={{ currentUser, getUserId, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
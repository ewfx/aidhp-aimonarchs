const authService = {
    login: async (email, password) => {
      try {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) throw new Error('Login failed');
        
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        return true;
      } catch (error) {
        console.error('Login error:', error);
        return false;
      }
    },
    
    getCurrentUser: async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) return null;
        
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) throw new Error('Failed to get user');
        return await response.json();
      } catch (error) {
        console.error('Get user error:', error);
        return null;
      }
    },
    
    logout: () => {
      localStorage.removeItem('token');
    }
  };
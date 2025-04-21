import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User } from '../types';
import { api, apiService } from '../utils/api';
import { env } from '../config/env';
import { useNotification } from './NotificationContext';

interface AuthContextType {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (name: string, email: string, password: string) => Promise<boolean>;
  logout: () => void;
  forgotPassword: (email: string) => Promise<boolean>;
  resetPassword: (token: string, password: string) => Promise<boolean>;
  updateProfile: (data: Partial<User>) => Promise<boolean>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<boolean>;
  refreshUserData: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { showNotification } = useNotification();
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem(env.AUTH_TOKEN_KEY));
  const [refreshToken, setRefreshToken] = useState<string | null>(localStorage.getItem(env.AUTH_REFRESH_TOKEN_KEY));
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState<boolean>(false);

  // Fetch user data
  const fetchUserData = useCallback(async (authToken: string): Promise<User | null> => {
    try {
      const response = await api.get('/auth/me', {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
      return response.data;
    } catch (err) {
      console.error('Failed to fetch user data:', err);
      return null;
    }
  }, []);

  // Refresh user data
  const refreshUserData = useCallback(async (): Promise<void> => {
    if (!token) return;
    
    try {
      const userData = await fetchUserData(token);
      if (userData) {
        setUser(userData);
      }
    } catch (err) {
      console.error('Failed to refresh user data:', err);
    }
  }, [token, fetchUserData]);

  // Initialize authentication
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem(env.AUTH_TOKEN_KEY);
      const storedRefreshToken = localStorage.getItem(env.AUTH_REFRESH_TOKEN_KEY);
      
      if (storedToken) {
        setIsLoading(true);
        try {
          const userData = await fetchUserData(storedToken);
          
          if (userData) {
            setUser(userData);
            setToken(storedToken);
            setRefreshToken(storedRefreshToken);
          } else {
            // Token is invalid, try to refresh
            if (storedRefreshToken) {
              try {
                const response = await api.post('/auth/refresh-token', {
                  refresh_token: storedRefreshToken,
                });
                
                const { token: newToken, refresh_token: newRefreshToken } = response.data;
                
                localStorage.setItem(env.AUTH_TOKEN_KEY, newToken);
                localStorage.setItem(env.AUTH_REFRESH_TOKEN_KEY, newRefreshToken);
                
                setToken(newToken);
                setRefreshToken(newRefreshToken);
                
                const newUserData = await fetchUserData(newToken);
                if (newUserData) {
                  setUser(newUserData);
                } else {
                  handleLogout();
                }
              } catch (refreshErr) {
                console.error('Failed to refresh token:', refreshErr);
                handleLogout();
              }
            } else {
              handleLogout();
            }
          }
        } catch (err) {
          console.error('Auth initialization error:', err);
          handleLogout();
        } finally {
          setIsLoading(false);
        }
      }
      
      setIsInitialized(true);
    };

    initAuth();
  }, [fetchUserData]);

  // Set auth header for all requests when token changes
  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem(env.AUTH_TOKEN_KEY, token);
    } else {
      delete api.defaults.headers.common['Authorization'];
      localStorage.removeItem(env.AUTH_TOKEN_KEY);
    }
  }, [token]);

  // Handle logout
  const handleLogout = useCallback(() => {
    setUser(null);
    setToken(null);
    setRefreshToken(null);
    localStorage.removeItem(env.AUTH_TOKEN_KEY);
    localStorage.removeItem(env.AUTH_REFRESH_TOKEN_KEY);
    delete api.defaults.headers.common['Authorization'];
  }, []);

  // Login user
  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.auth.login(email, password);
      const { user: userData, token: authToken, refresh_token: authRefreshToken } = response.data;
      
      setUser(userData);
      setToken(authToken);
      setRefreshToken(authRefreshToken);
      
      localStorage.setItem(env.AUTH_TOKEN_KEY, authToken);
      if (authRefreshToken) {
        localStorage.setItem(env.AUTH_REFRESH_TOKEN_KEY, authRefreshToken);
      }
      
      showNotification({
        title: 'Login Successful',
        message: `Welcome back, ${userData.name || userData.email}!`,
        type: 'success',
      });
      
      return true;
    } catch (err: any) {
      console.error('Login error:', err);
      const errorMessage = err.response?.data?.message || 'Failed to login. Please check your credentials.';
      setError(errorMessage);
      
      showNotification({
        title: 'Login Failed',
        message: errorMessage,
        type: 'error',
      });
      
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Register user
  const register = async (name: string, email: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.auth.register(name, email, password);
      const { user: userData, token: authToken, refresh_token: authRefreshToken } = response.data;
      
      setUser(userData);
      setToken(authToken);
      setRefreshToken(authRefreshToken);
      
      localStorage.setItem(env.AUTH_TOKEN_KEY, authToken);
      if (authRefreshToken) {
        localStorage.setItem(env.AUTH_REFRESH_TOKEN_KEY, authRefreshToken);
      }
      
      showNotification({
        title: 'Registration Successful',
        message: `Welcome, ${name}! Your account has been created.`,
        type: 'success',
      });
      
      return true;
    } catch (err: any) {
      console.error('Registration error:', err);
      const errorMessage = err.response?.data?.message || 'Failed to register. Please try again.';
      setError(errorMessage);
      
      showNotification({
        title: 'Registration Failed',
        message: errorMessage,
        type: 'error',
      });
      
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout user
  const logout = () => {
    handleLogout();
    
    showNotification({
      title: 'Logged Out',
      message: 'You have been successfully logged out.',
      type: 'info',
    });
  };

  // Forgot password
  const forgotPassword = async (email: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      await apiService.auth.forgotPassword(email);
      
      showNotification({
        title: 'Password Reset Email Sent',
        message: 'Please check your email for instructions to reset your password.',
        type: 'success',
      });
      
      return true;
    } catch (err: any) {
      console.error('Forgot password error:', err);
      const errorMessage = err.response?.data?.message || 'Failed to send reset link. Please try again.';
      setError(errorMessage);
      
      showNotification({
        title: 'Request Failed',
        message: errorMessage,
        type: 'error',
      });
      
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Reset password
  const resetPassword = async (token: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      await apiService.auth.resetPassword(token, password);
      
      showNotification({
        title: 'Password Reset Successful',
        message: 'Your password has been reset. You can now log in with your new password.',
        type: 'success',
      });
      
      return true;
    } catch (err: any) {
      console.error('Reset password error:', err);
      const errorMessage = err.response?.data?.message || 'Failed to reset password. Please try again.';
      setError(errorMessage);
      
      showNotification({
        title: 'Password Reset Failed',
        message: errorMessage,
        type: 'error',
      });
      
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Update user profile
  const updateProfile = async (data: Partial<User>): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.auth.updateProfile(data);
      setUser(response.data);
      
      showNotification({
        title: 'Profile Updated',
        message: 'Your profile has been successfully updated.',
        type: 'success',
      });
      
      return true;
    } catch (err: any) {
      console.error('Update profile error:', err);
      const errorMessage = err.response?.data?.message || 'Failed to update profile. Please try again.';
      setError(errorMessage);
      
      showNotification({
        title: 'Update Failed',
        message: errorMessage,
        type: 'error',
      });
      
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Change password
  const changePassword = async (currentPassword: string, newPassword: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      await apiService.auth.changePassword(currentPassword, newPassword);
      
      showNotification({
        title: 'Password Changed',
        message: 'Your password has been successfully changed.',
        type: 'success',
      });
      
      return true;
    } catch (err: any) {
      console.error('Change password error:', err);
      const errorMessage = err.response?.data?.message || 'Failed to change password. Please try again.';
      setError(errorMessage);
      
      showNotification({
        title: 'Password Change Failed',
        message: errorMessage,
        type: 'error',
      });
      
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Clear error
  const clearError = () => {
    setError(null);
  };

  // Provide auth context
  const value = {
    user,
    token,
    refreshToken,
    isAuthenticated: !!user,
    isLoading,
    isInitialized,
    error,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
    updateProfile,
    changePassword,
    refreshUserData,
    clearError,
  };

  // Only render children when auth is initialized
  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-white">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600 text-sm">Initializing application...</p>
        </div>
      </div>
    );
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

// Auth guard component
export const AuthGuard: React.FC<{ 
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ children, fallback }) => {
  const { isAuthenticated, isLoading, isInitialized } = useAuth();
  
  if (!isInitialized || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-600 mb-3"></div>
          <p className="text-gray-600 text-sm">Loading...</p>
        </div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return fallback ? <>{fallback}</> : null;
  }
  
  return <>{children}</>;
};

// Guest guard component (only for non-authenticated users)
export const GuestGuard: React.FC<{ 
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ children, fallback }) => {
  const { isAuthenticated, isLoading, isInitialized } = useAuth();
  
  if (!isInitialized || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-600 mb-3"></div>
          <p className="text-gray-600 text-sm">Loading...</p>
        </div>
      </div>
    );
  }
  
  if (isAuthenticated) {
    return fallback ? <>{fallback}</> : null;
  }
  
  return <>{children}</>;
};
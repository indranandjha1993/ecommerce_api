import { PasswordReset, PasswordResetRequest, Token, User, UserCreate, UserLogin } from '../types';
import { apiService } from './api';

export const authService = {
  register: (userData: UserCreate): Promise<User> => 
    apiService.post<User>('/auth/register', userData),
    
  login: (credentials: UserLogin): Promise<Token> => 
    apiService.post<Token>('/auth/login/email', credentials),
    
  refreshToken: (refreshToken: string): Promise<Token> => 
    apiService.post<Token>('/auth/refresh', { refresh_token: refreshToken }),
    
  requestPasswordReset: (data: PasswordResetRequest): Promise<{ message: string }> => 
    apiService.post<{ message: string }>('/auth/password-reset/request', data),
    
  resetPassword: (data: PasswordReset): Promise<{ message: string }> => 
    apiService.post<{ message: string }>('/auth/password-reset/confirm', data),
    
  verifyEmail: (token: string): Promise<{ message: string }> => 
    apiService.post<{ message: string }>('/auth/verify-email', { token }),
    
  logout: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
  
  getCurrentUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch (e) {
        return null;
      }
    }
    return null;
  },
  
  setCurrentUser: (user: User): void => {
    localStorage.setItem('user', JSON.stringify(user));
  },
  
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('access_token');
  }
};
import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }
        
        const response = await axios.post(`${api.defaults.baseURL}/auth/refresh`, {
          refresh_token: refreshToken
        });
        
        const { access_token, refresh_token } = response.data;
        
        // Update tokens in localStorage
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        
        // Update the authorization header
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        
        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, logout the user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        
        // Redirect to login page
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// Helper functions for API calls
export const apiService = {
  get: <T>(url: string, config?: AxiosRequestConfig): Promise<T> => 
    api.get<T, AxiosResponse<T>>(url, config).then(response => response.data),
    
  post: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    api.post<T, AxiosResponse<T>>(url, data, config).then(response => response.data),
    
  put: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    api.put<T, AxiosResponse<T>>(url, data, config).then(response => response.data),
    
  patch: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    api.patch<T, AxiosResponse<T>>(url, data, config).then(response => response.data),
    
  delete: <T>(url: string, config?: AxiosRequestConfig): Promise<T> => 
    api.delete<T, AxiosResponse<T>>(url, config).then(response => response.data),
};

export default api;
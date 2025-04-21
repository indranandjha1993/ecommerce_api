import axios from 'axios';

// Import environment configuration
import { env } from '../config/env';

// Create axios instance with base URL and default headers
export const api = axios.create({
  baseURL: env.API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Add a request interceptor
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem(env.AUTH_TOKEN_KEY);
    
    // If token exists, add it to the request headers
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If the error is due to an expired token (401) and we haven't tried to refresh yet
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem(env.AUTH_REFRESH_TOKEN_KEY);
        
        if (refreshToken) {
          const response = await axios.post(`${env.API_URL}/auth/refresh-token`, {
            refresh_token: refreshToken,
          });
          
          const { token, refresh_token } = response.data;
          
          // Update tokens in localStorage
          localStorage.setItem(env.AUTH_TOKEN_KEY, token);
          localStorage.setItem(env.AUTH_REFRESH_TOKEN_KEY, refresh_token);
          
          // Update the Authorization header
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          
          // Retry the original request
          return api(originalRequest);
        }
      } catch (refreshError) {
        // If refresh token is invalid, log the user out
        localStorage.removeItem(env.AUTH_TOKEN_KEY);
        localStorage.removeItem(env.AUTH_REFRESH_TOKEN_KEY);
        
        // Redirect to login page
        window.location.href = '/login';
        
        return Promise.reject(refreshError);
      }
    }
    
    // Handle specific error status codes
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response error:', error.response.status, error.response.data);
      
      // Handle specific error codes
      switch (error.response.status) {
        case 400:
          // Bad request
          break;
        case 403:
          // Forbidden
          break;
        case 404:
          // Not found
          break;
        case 500:
          // Server error
          break;
        default:
          break;
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Request error:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// API service functions
export const apiService = {
  // Auth endpoints
  auth: {
    login: (email: string, password: string) => api.post('/auth/login', { email, password }),
    register: (name: string, email: string, password: string) => api.post('/auth/register', { name, email, password }),
    forgotPassword: (email: string) => api.post('/auth/forgot-password', { email }),
    resetPassword: (token: string, password: string) => api.post('/auth/reset-password', { token, password }),
    me: () => api.get('/auth/me'),
    updateProfile: (data: any) => api.put('/auth/profile', data),
    changePassword: (currentPassword: string, newPassword: string) => api.post('/auth/change-password', { current_password: currentPassword, new_password: newPassword }),
  },
  
  // Products endpoints
  products: {
    getAll: (params?: any) => api.get('/products', { params }),
    getById: (id: string) => api.get(`/products/${id}`),
    getBySlug: (slug: string) => api.get(`/products/slug/${slug}`),
    getRelated: (id: string) => api.get(`/products/${id}/related`),
    getFeatured: () => api.get('/products/featured'),
    getNew: () => api.get('/products/new'),
    getBestsellers: () => api.get('/products/bestsellers'),
    search: (query: string) => api.get('/products/search', { params: { q: query } }),
  },
  
  // Categories endpoints
  categories: {
    getAll: () => api.get('/categories'),
    getById: (id: string) => api.get(`/categories/${id}`),
    getBySlug: (slug: string) => api.get(`/categories/slug/${slug}`),
    getProducts: (id: string, params?: any) => api.get(`/categories/${id}/products`, { params }),
  },
  
  // Brands endpoints
  brands: {
    getAll: () => api.get('/brands'),
    getById: (id: string) => api.get(`/brands/${id}`),
    getBySlug: (slug: string) => api.get(`/brands/slug/${slug}`),
    getProducts: (id: string, params?: any) => api.get(`/brands/${id}/products`, { params }),
  },
  
  // Cart endpoints
  cart: {
    get: () => api.get('/cart'),
    addItem: (productId: string, quantity: number, variantId?: string) => api.post('/cart/items', { product_id: productId, quantity, variant_id: variantId }),
    updateItem: (itemId: string, quantity: number) => api.put(`/cart/items/${itemId}`, { quantity }),
    removeItem: (itemId: string) => api.delete(`/cart/items/${itemId}`),
    clear: () => api.delete('/cart'),
    applyCoupon: (code: string) => api.post('/cart/coupon', { code }),
    removeCoupon: () => api.delete('/cart/coupon'),
  },
  
  // Wishlist endpoints
  wishlist: {
    get: () => api.get('/wishlist'),
    addItem: (productId: string) => api.post('/wishlist/items', { product_id: productId }),
    removeItem: (productId: string) => api.delete(`/wishlist/items/${productId}`),
    clear: () => api.delete('/wishlist'),
  },
  
  // Orders endpoints
  orders: {
    getAll: () => api.get('/orders'),
    getById: (id: string) => api.get(`/orders/${id}`),
    create: (data: any) => api.post('/orders', data),
    cancel: (id: string) => api.post(`/orders/${id}/cancel`),
  },
  
  // Addresses endpoints
  addresses: {
    getAll: () => api.get('/addresses'),
    getById: (id: string) => api.get(`/addresses/${id}`),
    create: (data: any) => api.post('/addresses', data),
    update: (id: string, data: any) => api.put(`/addresses/${id}`, data),
    delete: (id: string) => api.delete(`/addresses/${id}`),
    setDefault: (id: string) => api.post(`/addresses/${id}/default`),
  },
  
  // Reviews endpoints
  reviews: {
    getByProduct: (productId: string) => api.get(`/products/${productId}/reviews`),
    create: (productId: string, data: any) => api.post(`/products/${productId}/reviews`, data),
    update: (reviewId: string, data: any) => api.put(`/reviews/${reviewId}`, data),
    delete: (reviewId: string) => api.delete(`/reviews/${reviewId}`),
  },
};

export default apiService;
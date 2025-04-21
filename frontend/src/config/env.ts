// Environment variables with fallbacks
export const env = {
  // API
  API_URL: import.meta.env.VITE_API_URL || '/api/v1',
  
  // Auth
  AUTH_TOKEN_KEY: import.meta.env.VITE_AUTH_TOKEN_KEY || 'token',
  AUTH_REFRESH_TOKEN_KEY: import.meta.env.VITE_AUTH_REFRESH_TOKEN_KEY || 'refreshToken',
  
  // App
  APP_NAME: import.meta.env.VITE_APP_NAME || 'E-commerce Store',
  
  // Features
  ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  
  // External services
  STRIPE_PUBLIC_KEY: import.meta.env.VITE_STRIPE_PUBLIC_KEY || '',
  
  // Development
  IS_DEV: import.meta.env.DEV || false,
};
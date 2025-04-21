import React, { createContext, useContext, useState, useCallback } from 'react';
import { api } from '../utils/api';
import { Product, ProductSearchQuery } from '../types';

interface ProductContextType {
  products: Product[];
  featuredProducts: Product[];
  newArrivals: Product[];
  bestsellers: Product[];
  currentProduct: Product | null;
  searchResults: Product[];
  loading: boolean;
  error: string | null;
  fetchProducts: (params?: ProductSearchQuery) => Promise<boolean>;
  fetchProductById: (id: string) => Promise<boolean>;
  fetchProductBySlug: (slug: string) => Promise<boolean>;
  fetchFeaturedProducts: (limit?: number) => Promise<boolean>;
  fetchNewArrivals: (params?: { limit?: number; days?: number }) => Promise<boolean>;
  fetchBestsellers: (params?: { limit?: number; period?: 'week' | 'month' | 'year' | 'all' }) => Promise<boolean>;
  searchProducts: (query: string, limit?: number) => Promise<boolean>;
  resetCurrentProduct: () => void;
  resetSearchResults: () => void;
}

const ProductContext = createContext<ProductContextType | undefined>(undefined);

export const ProductProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [newArrivals, setNewArrivals] = useState<Product[]>([]);
  const [bestsellers, setBestsellers] = useState<Product[]>([]);
  const [currentProduct, setCurrentProduct] = useState<Product | null>(null);
  const [searchResults, setSearchResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch all products with optional filters
  const fetchProducts = useCallback(async (params: ProductSearchQuery = {}): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/products', { params });
      setProducts(response.data.results || response.data);
      return true;
    } catch (err: any) {
      console.error('Failed to fetch products:', err);
      setError(err.response?.data?.message || 'Failed to fetch products');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch a product by ID
  const fetchProductById = useCallback(async (id: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/products/${id}`);
      setCurrentProduct(response.data);
      return true;
    } catch (err: any) {
      console.error(`Failed to fetch product with ID ${id}:`, err);
      setError(err.response?.data?.message || 'Failed to fetch product');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch a product by slug
  const fetchProductBySlug = useCallback(async (slug: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/products/slug/${slug}`);
      setCurrentProduct(response.data);
      return true;
    } catch (err: any) {
      console.error(`Failed to fetch product with slug ${slug}:`, err);
      setError(err.response?.data?.message || 'Failed to fetch product');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch featured products
  const fetchFeaturedProducts = useCallback(async (limit: number = 10): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/products/featured', { params: { limit } });
      setFeaturedProducts(response.data.results || response.data);
      return true;
    } catch (err: any) {
      console.error('Failed to fetch featured products:', err);
      setError(err.response?.data?.message || 'Failed to fetch featured products');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch new arrivals
  const fetchNewArrivals = useCallback(async (params: { limit?: number; days?: number } = {}): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/products/new-arrivals', { params });
      setNewArrivals(response.data.results || response.data);
      return true;
    } catch (err: any) {
      console.error('Failed to fetch new arrivals:', err);
      setError(err.response?.data?.message || 'Failed to fetch new arrivals');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch bestsellers
  const fetchBestsellers = useCallback(async (params: { limit?: number; period?: 'week' | 'month' | 'year' | 'all' } = {}): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/products/bestsellers', { params });
      setBestsellers(response.data.results || response.data);
      return true;
    } catch (err: any) {
      console.error('Failed to fetch bestsellers:', err);
      setError(err.response?.data?.message || 'Failed to fetch bestsellers');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Search products
  const searchProducts = useCallback(async (query: string, limit: number = 10): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/products/search', { params: { query, limit } });
      setSearchResults(response.data.results || response.data);
      return true;
    } catch (err: any) {
      console.error('Failed to search products:', err);
      setError(err.response?.data?.message || 'Failed to search products');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Reset current product
  const resetCurrentProduct = useCallback(() => {
    setCurrentProduct(null);
  }, []);

  // Reset search results
  const resetSearchResults = useCallback(() => {
    setSearchResults([]);
  }, []);

  const value = {
    products,
    featuredProducts,
    newArrivals,
    bestsellers,
    currentProduct,
    searchResults,
    loading,
    error,
    fetchProducts,
    fetchProductById,
    fetchProductBySlug,
    fetchFeaturedProducts,
    fetchNewArrivals,
    fetchBestsellers,
    searchProducts,
    resetCurrentProduct,
    resetSearchResults,
  };

  return (
    <ProductContext.Provider value={value}>
      {children}
    </ProductContext.Provider>
  );
};

// Custom hook to use product context
export const useProducts = () => {
  const context = useContext(ProductContext);
  
  if (context === undefined) {
    throw new Error('useProducts must be used within a ProductProvider');
  }
  
  return context;
};
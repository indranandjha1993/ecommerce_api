import React, { createContext, useContext, useState, useCallback } from 'react';
import { api } from '../utils/api';
import { Brand } from '../types';

interface BrandContextType {
  brands: Brand[];
  topBrands: Brand[];
  currentBrand: Brand | null;
  loading: boolean;
  error: string | null;
  fetchBrands: (includeInactive?: boolean) => Promise<boolean>;
  fetchTopBrands: (limit?: number) => Promise<boolean>;
  fetchBrandById: (id: string) => Promise<boolean>;
  fetchBrandBySlug: (slug: string) => Promise<boolean>;
  resetCurrentBrand: () => void;
}

const BrandContext = createContext<BrandContextType | undefined>(undefined);

export const BrandProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [topBrands, setTopBrands] = useState<Brand[]>([]);
  const [currentBrand, setCurrentBrand] = useState<Brand | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch all brands
  const fetchBrands = useCallback(async (includeInactive: boolean = false): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/brands', { params: { include_inactive: includeInactive } });
      setBrands(response.data.results || response.data);
      return true;
    } catch (err: any) {
      console.error('Failed to fetch brands:', err);
      setError(err.response?.data?.message || 'Failed to fetch brands');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch top brands
  const fetchTopBrands = useCallback(async (limit: number = 10): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/brands/top', { params: { limit } });
      setTopBrands(response.data.results || response.data);
      return true;
    } catch (err: any) {
      console.error('Failed to fetch top brands:', err);
      setError(err.response?.data?.message || 'Failed to fetch top brands');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch a brand by ID
  const fetchBrandById = useCallback(async (id: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/brands/${id}`);
      setCurrentBrand(response.data);
      return true;
    } catch (err: any) {
      console.error(`Failed to fetch brand with ID ${id}:`, err);
      setError(err.response?.data?.message || 'Failed to fetch brand');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch a brand by slug
  const fetchBrandBySlug = useCallback(async (slug: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/brands/slug/${slug}`);
      setCurrentBrand(response.data);
      return true;
    } catch (err: any) {
      console.error(`Failed to fetch brand with slug ${slug}:`, err);
      setError(err.response?.data?.message || 'Failed to fetch brand');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Reset current brand
  const resetCurrentBrand = useCallback(() => {
    setCurrentBrand(null);
  }, []);

  const value = {
    brands,
    topBrands,
    currentBrand,
    loading,
    error,
    fetchBrands,
    fetchTopBrands,
    fetchBrandById,
    fetchBrandBySlug,
    resetCurrentBrand,
  };

  return (
    <BrandContext.Provider value={value}>
      {children}
    </BrandContext.Provider>
  );
};

// Custom hook to use brand context
export const useBrands = () => {
  const context = useContext(BrandContext);
  
  if (context === undefined) {
    throw new Error('useBrands must be used within a BrandProvider');
  }
  
  return context;
};
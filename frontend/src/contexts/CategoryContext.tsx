import React, { createContext, useContext, useState, useCallback } from 'react';
import { api } from '../utils/api';
import { Category } from '../types';

interface CategoryContextType {
  categories: Category[];
  topCategories: Category[];
  currentCategory: Category | null;
  subcategories: Record<string, Category[]>;
  loading: boolean;
  error: string | null;
  fetchCategories: (includeInactive?: boolean) => Promise<boolean>;
  fetchTopCategories: (limit?: number) => Promise<boolean>;
  fetchCategoryById: (id: string) => Promise<boolean>;
  fetchCategoryBySlug: (slug: string) => Promise<boolean>;
  fetchSubcategories: (parentId: string, includeInactive?: boolean) => Promise<boolean>;
  getSubcategories: (parentId: string) => Category[];
  resetCurrentCategory: () => void;
}

const CategoryContext = createContext<CategoryContextType | undefined>(undefined);

export const CategoryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [topCategories, setTopCategories] = useState<Category[]>([]);
  const [currentCategory, setCurrentCategory] = useState<Category | null>(null);
  const [subcategories, setSubcategories] = useState<Record<string, Category[]>>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch all categories
  const fetchCategories = useCallback(async (includeInactive: boolean = false): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/categories', { params: { include_inactive: includeInactive } });
      setCategories(response.data.results || response.data);
      return true;
    } catch (err: any) {
      console.error('Failed to fetch categories:', err);
      setError(err.response?.data?.message || 'Failed to fetch categories');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch top categories
  const fetchTopCategories = useCallback(async (limit: number = 10): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/categories/top', { params: { limit } });
      setTopCategories(response.data.results || response.data);
      return true;
    } catch (err: any) {
      console.error('Failed to fetch top categories:', err);
      setError(err.response?.data?.message || 'Failed to fetch top categories');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch a category by ID
  const fetchCategoryById = useCallback(async (id: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/categories/${id}`);
      setCurrentCategory(response.data);
      return true;
    } catch (err: any) {
      console.error(`Failed to fetch category with ID ${id}:`, err);
      setError(err.response?.data?.message || 'Failed to fetch category');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch a category by slug
  const fetchCategoryBySlug = useCallback(async (slug: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/categories/slug/${slug}`);
      setCurrentCategory(response.data);
      return true;
    } catch (err: any) {
      console.error(`Failed to fetch category with slug ${slug}:`, err);
      setError(err.response?.data?.message || 'Failed to fetch category');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch subcategories
  const fetchSubcategories = useCallback(async (parentId: string, includeInactive: boolean = false): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get(`/categories/${parentId}/subcategories`, {
        params: { include_inactive: includeInactive }
      });
      const fetchedSubcategories = response.data.results || response.data;
      
      setSubcategories(prev => ({
        ...prev,
        [parentId]: fetchedSubcategories
      }));
      
      return true;
    } catch (err: any) {
      console.error(`Failed to fetch subcategories for parent ID ${parentId}:`, err);
      setError(err.response?.data?.message || 'Failed to fetch subcategories');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Get subcategories for a parent category
  const getSubcategories = useCallback((parentId: string): Category[] => {
    return subcategories[parentId] || [];
  }, [subcategories]);

  // Reset current category
  const resetCurrentCategory = useCallback(() => {
    setCurrentCategory(null);
  }, []);

  const value = {
    categories,
    topCategories,
    currentCategory,
    subcategories,
    loading,
    error,
    fetchCategories,
    fetchTopCategories,
    fetchCategoryById,
    fetchCategoryBySlug,
    fetchSubcategories,
    getSubcategories,
    resetCurrentCategory,
  };

  return (
    <CategoryContext.Provider value={value}>
      {children}
    </CategoryContext.Provider>
  );
};

// Custom hook to use category context
export const useCategories = () => {
  const context = useContext(CategoryContext);
  
  if (context === undefined) {
    throw new Error('useCategories must be used within a CategoryProvider');
  }
  
  return context;
};
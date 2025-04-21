import { Category } from '../types';
import { apiService } from './api';

export const categoryService = {
  getCategories: (includeInactive: boolean = false): Promise<Category[]> => 
    apiService.get<Category[]>(`/categories?include_inactive=${includeInactive}`),
    
  getCategoryById: (id: string): Promise<Category> => 
    apiService.get<Category>(`/categories/${id}`),
    
  getCategoryBySlug: (slug: string): Promise<Category> => 
    apiService.get<Category>(`/categories/slug/${slug}`),
    
  getTopCategories: (limit: number = 10): Promise<Category[]> => 
    apiService.get<Category[]>(`/categories/top?limit=${limit}`),
    
  getSubcategories: (parentId: string, includeInactive: boolean = false): Promise<Category[]> => 
    apiService.get<Category[]>(`/categories/parent/${parentId}?include_inactive=${includeInactive}`),
};
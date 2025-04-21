import { Brand } from '../types';
import { apiService } from './api';

export const brandService = {
  getBrands: (includeInactive: boolean = false): Promise<Brand[]> => 
    apiService.get<Brand[]>(`/brands?include_inactive=${includeInactive}`),
    
  getBrandById: (id: string): Promise<Brand> => 
    apiService.get<Brand>(`/brands/${id}`),
    
  getBrandBySlug: (slug: string): Promise<Brand> => 
    apiService.get<Brand>(`/brands/slug/${slug}`),
    
  getTopBrands: (limit: number = 10): Promise<Brand[]> => 
    apiService.get<Brand[]>(`/brands/top?limit=${limit}`),
};
import { Product, ProductList, ProductListItem, ProductSearchQuery, ProductWithRelations } from '../types';
import { apiService } from './api';

export const productService = {
  getProducts: (params: ProductSearchQuery = {}): Promise<ProductList> => {
    const queryParams = new URLSearchParams();
    
    if (params.query) queryParams.append('query', params.query);
    if (params.category_id) queryParams.append('category_id', params.category_id);
    if (params.brand_id) queryParams.append('brand_id', params.brand_id);
    if (params.min_price !== undefined) queryParams.append('min_price', params.min_price.toString());
    if (params.max_price !== undefined) queryParams.append('max_price', params.max_price.toString());
    if (params.in_stock !== undefined) queryParams.append('in_stock', params.in_stock.toString());
    if (params.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params.sort_order) queryParams.append('sort_order', params.sort_order);
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.size) queryParams.append('size', params.size.toString());
    
    return apiService.get<ProductList>(`/products?${queryParams.toString()}`);
  },
  
  getProductById: (id: string): Promise<ProductWithRelations> => 
    apiService.get<ProductWithRelations>(`/products/${id}`),
    
  getProductBySlug: (slug: string): Promise<ProductWithRelations> => 
    apiService.get<ProductWithRelations>(`/products/slug/${slug}`),
    
  getFeaturedProducts: (limit: number = 10): Promise<ProductListItem[]> => 
    apiService.get<ProductListItem[]>(`/products/featured?limit=${limit}`),
    
  getNewArrivals: (limit: number = 10, days: number = 30): Promise<ProductListItem[]> => 
    apiService.get<ProductListItem[]>(`/products/new-arrivals?limit=${limit}&days=${days}`),
    
  getBestsellers: (limit: number = 10, period: 'week' | 'month' | 'year' | 'all' = 'month'): Promise<ProductListItem[]> => 
    apiService.get<ProductListItem[]>(`/products/bestsellers?limit=${limit}&period=${period}`),
    
  getProductsByCategory: (
    categoryId: string, 
    page: number = 1, 
    size: number = 20,
    includeSubcategories: boolean = true,
    sortBy: string = 'created_at',
    sortOrder: 'asc' | 'desc' = 'desc'
  ): Promise<ProductList> => 
    apiService.get<ProductList>(
      `/products/category/${categoryId}?page=${page}&size=${size}&include_subcategories=${includeSubcategories}&sort_by=${sortBy}&sort_order=${sortOrder}`
    ),
    
  getProductsByBrand: (
    brandId: string, 
    page: number = 1, 
    size: number = 20,
    categoryId?: string,
    sortBy: string = 'created_at',
    sortOrder: 'asc' | 'desc' = 'desc'
  ): Promise<ProductList> => {
    let url = `/products/brand/${brandId}?page=${page}&size=${size}&sort_by=${sortBy}&sort_order=${sortOrder}`;
    if (categoryId) url += `&category_id=${categoryId}`;
    return apiService.get<ProductList>(url);
  },
  
  searchProducts: (query: string, limit: number = 10): Promise<ProductListItem[]> => 
    apiService.get<ProductListItem[]>(`/products/search?q=${encodeURIComponent(query)}&limit=${limit}`),
};
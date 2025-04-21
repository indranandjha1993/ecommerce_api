import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useProducts } from '../hooks/useProducts';
import { useCategories } from '../hooks/useCategories';
import { useBrands } from '../hooks/useBrands';
import { useUI } from '../hooks/useUI';
import ProductGrid from '../components/product/ProductGrid';
import Pagination from '../components/ui/Pagination';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';

const ProductsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { filterDrawerOpen, setFilterDrawerOpen } = useUI();
  
  const { products, loading, fetchProducts } = useProducts();
  const { categories, fetchCategories } = useCategories();
  const { brands, fetchBrands } = useBrands();
  
  const [filters, setFilters] = useState({
    query: searchParams.get('query') || '',
    category_id: searchParams.get('category_id') || '',
    brand_id: searchParams.get('brand_id') || '',
    min_price: searchParams.get('min_price') || '',
    max_price: searchParams.get('max_price') || '',
    in_stock: searchParams.get('in_stock') === 'true',
    sort_by: searchParams.get('sort_by') || 'created_at',
    sort_order: searchParams.get('sort_order') || 'desc',
    page: parseInt(searchParams.get('page') || '1', 10),
    size: parseInt(searchParams.get('size') || '12', 10),
  });
  
  useEffect(() => {
    fetchCategories();
    fetchBrands();
  }, [fetchCategories, fetchBrands]);
  
  useEffect(() => {
    fetchProducts({
      query: filters.query || undefined,
      category_id: filters.category_id || undefined,
      brand_id: filters.brand_id || undefined,
      min_price: filters.min_price ? parseFloat(filters.min_price) : undefined,
      max_price: filters.max_price ? parseFloat(filters.max_price) : undefined,
      in_stock: filters.in_stock || undefined,
      sort_by: filters.sort_by,
      sort_order: filters.sort_order as 'asc' | 'desc',
      page: filters.page,
      size: filters.size,
    });
    
    // Update URL with filters
    const params = new URLSearchParams();
    if (filters.query) params.set('query', filters.query);
    if (filters.category_id) params.set('category_id', filters.category_id);
    if (filters.brand_id) params.set('brand_id', filters.brand_id);
    if (filters.min_price) params.set('min_price', filters.min_price);
    if (filters.max_price) params.set('max_price', filters.max_price);
    if (filters.in_stock) params.set('in_stock', 'true');
    if (filters.sort_by !== 'created_at') params.set('sort_by', filters.sort_by);
    if (filters.sort_order !== 'desc') params.set('sort_order', filters.sort_order);
    if (filters.page !== 1) params.set('page', filters.page.toString());
    if (filters.size !== 12) params.set('size', filters.size.toString());
    
    setSearchParams(params);
  }, [filters, fetchProducts, setSearchParams]);
  
  const handleFilterChange = (name: string, value: string | boolean | number) => {
    setFilters((prev) => ({
      ...prev,
      [name]: value,
      // Reset page when changing filters
      ...(name !== 'page' && { page: 1 }),
    }));
  };
  
  const handlePageChange = (page: number) => {
    handleFilterChange('page', page);
    // Scroll to top when changing page
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  
  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    const [sort_by, sort_order] = value.split('-');
    
    setFilters((prev) => ({
      ...prev,
      sort_by,
      sort_order: sort_order as 'asc' | 'desc',
      page: 1,
    }));
  };
  
  const clearFilters = () => {
    setFilters({
      query: '',
      category_id: '',
      brand_id: '',
      min_price: '',
      max_price: '',
      in_stock: false,
      sort_by: 'created_at',
      sort_order: 'desc',
      page: 1,
      size: 12,
    });
  };
  
  const toggleFilterDrawer = () => {
    setFilterDrawerOpen(!filterDrawerOpen);
  };
  
  const sortOptions = [
    { value: 'created_at-desc', label: 'Newest' },
    { value: 'created_at-asc', label: 'Oldest' },
    { value: 'price-asc', label: 'Price: Low to High' },
    { value: 'price-desc', label: 'Price: High to Low' },
    { value: 'name-asc', label: 'Name: A to Z' },
    { value: 'name-desc', label: 'Name: Z to A' },
  ];
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Products</h1>
      
      <div className="flex flex-col md:flex-row gap-8">
        {/* Filters - Desktop */}
        <div className="hidden md:block w-64 flex-shrink-0">
          <div className="sticky top-24 bg-white rounded-lg shadow-sm p-6">
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={clearFilters}
                className="w-full"
              >
                Clear All Filters
              </Button>
            </div>
            
            {/* Categories */}
            <div className="mb-6">
              <h4 className="font-medium text-gray-900 mb-2">Categories</h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                <div className="flex items-center">
                  <input
                    id="category-all"
                    type="radio"
                    name="category"
                    checked={!filters.category_id}
                    onChange={() => handleFilterChange('category_id', '')}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="category-all" className="ml-2 text-sm text-gray-700">
                    All Categories
                  </label>
                </div>
                
                {categories.map((category) => (
                  <div key={category.id} className="flex items-center">
                    <input
                      id={`category-${category.id}`}
                      type="radio"
                      name="category"
                      checked={filters.category_id === category.id}
                      onChange={() => handleFilterChange('category_id', category.id)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor={`category-${category.id}`} className="ml-2 text-sm text-gray-700">
                      {category.name}
                    </label>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Brands */}
            <div className="mb-6">
              <h4 className="font-medium text-gray-900 mb-2">Brands</h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                <div className="flex items-center">
                  <input
                    id="brand-all"
                    type="radio"
                    name="brand"
                    checked={!filters.brand_id}
                    onChange={() => handleFilterChange('brand_id', '')}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="brand-all" className="ml-2 text-sm text-gray-700">
                    All Brands
                  </label>
                </div>
                
                {brands.map((brand) => (
                  <div key={brand.id} className="flex items-center">
                    <input
                      id={`brand-${brand.id}`}
                      type="radio"
                      name="brand"
                      checked={filters.brand_id === brand.id}
                      onChange={() => handleFilterChange('brand_id', brand.id)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor={`brand-${brand.id}`} className="ml-2 text-sm text-gray-700">
                      {brand.name}
                    </label>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Price Range */}
            <div className="mb-6">
              <h4 className="font-medium text-gray-900 mb-2">Price Range</h4>
              <div className="grid grid-cols-2 gap-2">
                <Input
                  type="number"
                  placeholder="Min"
                  value={filters.min_price}
                  onChange={(e) => handleFilterChange('min_price', e.target.value)}
                  min="0"
                />
                <Input
                  type="number"
                  placeholder="Max"
                  value={filters.max_price}
                  onChange={(e) => handleFilterChange('max_price', e.target.value)}
                  min="0"
                />
              </div>
            </div>
            
            {/* Availability */}
            <div className="mb-6">
              <h4 className="font-medium text-gray-900 mb-2">Availability</h4>
              <div className="flex items-center">
                <input
                  id="in-stock"
                  type="checkbox"
                  checked={filters.in_stock}
                  onChange={(e) => handleFilterChange('in_stock', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="in-stock" className="ml-2 text-sm text-gray-700">
                  In Stock Only
                </label>
              </div>
            </div>
          </div>
        </div>
        
        {/* Products */}
        <div className="flex-1">
          {/* Toolbar */}
          <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
            <div className="flex items-center">
              <Button
                variant="outline"
                size="sm"
                className="md:hidden mr-2"
                onClick={toggleFilterDrawer}
              >
                <svg
                  className="h-5 w-5 mr-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
                  />
                </svg>
                Filters
              </Button>
              
              <span className="text-sm text-gray-500">
                {products ? `Showing ${products.items.length} of ${products.total} products` : 'Loading products...'}
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <div>
                <label htmlFor="sort" className="sr-only">
                  Sort by
                </label>
                <select
                  id="sort"
                  value={`${filters.sort_by}-${filters.sort_order}`}
                  onChange={handleSortChange}
                  className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                >
                  {sortOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label htmlFor="per-page" className="sr-only">
                  Products per page
                </label>
                <select
                  id="per-page"
                  value={filters.size}
                  onChange={(e) => handleFilterChange('size', parseInt(e.target.value, 10))}
                  className="block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                >
                  <option value="12">12 per page</option>
                  <option value="24">24 per page</option>
                  <option value="48">48 per page</option>
                </select>
              </div>
            </div>
          </div>
          
          {/* Search */}
          <div className="mb-6">
            <Input
              type="text"
              placeholder="Search products..."
              value={filters.query}
              onChange={(e) => handleFilterChange('query', e.target.value)}
              fullWidth
              leftIcon={
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              }
            />
          </div>
          
          {/* Active Filters */}
          {(filters.query || filters.category_id || filters.brand_id || filters.min_price || filters.max_price || filters.in_stock) && (
            <div className="mb-6">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-sm font-medium text-gray-700">Active Filters:</span>
                
                {filters.query && (
                  <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
                    Search: {filters.query}
                    <button
                      type="button"
                      className="ml-1 inline-flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full text-blue-600 hover:bg-blue-200 hover:text-blue-800 focus:outline-none"
                      onClick={() => handleFilterChange('query', '')}
                    >
                      <span className="sr-only">Remove filter</span>
                      <svg className="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
                        <path strokeLinecap="round" strokeWidth="1.5" d="M1 1l6 6m0-6L1 7" />
                      </svg>
                    </button>
                  </span>
                )}
                
                {filters.category_id && (
                  <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
                    Category: {categories.find(c => c.id === filters.category_id)?.name || 'Unknown'}
                    <button
                      type="button"
                      className="ml-1 inline-flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full text-blue-600 hover:bg-blue-200 hover:text-blue-800 focus:outline-none"
                      onClick={() => handleFilterChange('category_id', '')}
                    >
                      <span className="sr-only">Remove filter</span>
                      <svg className="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
                        <path strokeLinecap="round" strokeWidth="1.5" d="M1 1l6 6m0-6L1 7" />
                      </svg>
                    </button>
                  </span>
                )}
                
                {filters.brand_id && (
                  <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
                    Brand: {brands.find(b => b.id === filters.brand_id)?.name || 'Unknown'}
                    <button
                      type="button"
                      className="ml-1 inline-flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full text-blue-600 hover:bg-blue-200 hover:text-blue-800 focus:outline-none"
                      onClick={() => handleFilterChange('brand_id', '')}
                    >
                      <span className="sr-only">Remove filter</span>
                      <svg className="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
                        <path strokeLinecap="round" strokeWidth="1.5" d="M1 1l6 6m0-6L1 7" />
                      </svg>
                    </button>
                  </span>
                )}
                
                {(filters.min_price || filters.max_price) && (
                  <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
                    Price: {filters.min_price ? `$${filters.min_price}` : '$0'} - {filters.max_price ? `$${filters.max_price}` : 'Any'}
                    <button
                      type="button"
                      className="ml-1 inline-flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full text-blue-600 hover:bg-blue-200 hover:text-blue-800 focus:outline-none"
                      onClick={() => {
                        handleFilterChange('min_price', '');
                        handleFilterChange('max_price', '');
                      }}
                    >
                      <span className="sr-only">Remove filter</span>
                      <svg className="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
                        <path strokeLinecap="round" strokeWidth="1.5" d="M1 1l6 6m0-6L1 7" />
                      </svg>
                    </button>
                  </span>
                )}
                
                {filters.in_stock && (
                  <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
                    In Stock Only
                    <button
                      type="button"
                      className="ml-1 inline-flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full text-blue-600 hover:bg-blue-200 hover:text-blue-800 focus:outline-none"
                      onClick={() => handleFilterChange('in_stock', false)}
                    >
                      <span className="sr-only">Remove filter</span>
                      <svg className="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
                        <path strokeLinecap="round" strokeWidth="1.5" d="M1 1l6 6m0-6L1 7" />
                      </svg>
                    </button>
                  </span>
                )}
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearFilters}
                >
                  Clear All
                </Button>
              </div>
            </div>
          )}
          
          {/* Product Grid */}
          <ProductGrid
            products={products?.items || []}
            loading={loading}
            columns={3}
            emptyMessage="No products found matching your criteria"
          />
          
          {/* Pagination */}
          {products && (
            <Pagination
              currentPage={filters.page}
              totalPages={products.pages}
              onPageChange={handlePageChange}
              className="mt-8"
            />
          )}
        </div>
      </div>
      
      {/* Mobile Filter Drawer */}
      {filterDrawerOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black bg-opacity-50" onClick={toggleFilterDrawer}></div>
          <div className="absolute inset-y-0 left-0 w-full max-w-xs bg-white shadow-xl">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-medium text-gray-900">Filters</h3>
              <button
                type="button"
                className="text-gray-400 hover:text-gray-500"
                onClick={toggleFilterDrawer}
              >
                <svg
                  className="h-6 w-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
            
            <div className="p-4 overflow-y-auto h-full pb-20">
              <div className="mb-6">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    clearFilters();
                    toggleFilterDrawer();
                  }}
                  className="w-full"
                >
                  Clear All Filters
                </Button>
              </div>
              
              {/* Categories */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Categories</h4>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      id="mobile-category-all"
                      type="radio"
                      name="mobile-category"
                      checked={!filters.category_id}
                      onChange={() => handleFilterChange('category_id', '')}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="mobile-category-all" className="ml-2 text-sm text-gray-700">
                      All Categories
                    </label>
                  </div>
                  
                  {categories.map((category) => (
                    <div key={category.id} className="flex items-center">
                      <input
                        id={`mobile-category-${category.id}`}
                        type="radio"
                        name="mobile-category"
                        checked={filters.category_id === category.id}
                        onChange={() => handleFilterChange('category_id', category.id)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor={`mobile-category-${category.id}`} className="ml-2 text-sm text-gray-700">
                        {category.name}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Brands */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Brands</h4>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      id="mobile-brand-all"
                      type="radio"
                      name="mobile-brand"
                      checked={!filters.brand_id}
                      onChange={() => handleFilterChange('brand_id', '')}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="mobile-brand-all" className="ml-2 text-sm text-gray-700">
                      All Brands
                    </label>
                  </div>
                  
                  {brands.map((brand) => (
                    <div key={brand.id} className="flex items-center">
                      <input
                        id={`mobile-brand-${brand.id}`}
                        type="radio"
                        name="mobile-brand"
                        checked={filters.brand_id === brand.id}
                        onChange={() => handleFilterChange('brand_id', brand.id)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor={`mobile-brand-${brand.id}`} className="ml-2 text-sm text-gray-700">
                        {brand.name}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Price Range */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Price Range</h4>
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    type="number"
                    placeholder="Min"
                    value={filters.min_price}
                    onChange={(e) => handleFilterChange('min_price', e.target.value)}
                    min="0"
                  />
                  <Input
                    type="number"
                    placeholder="Max"
                    value={filters.max_price}
                    onChange={(e) => handleFilterChange('max_price', e.target.value)}
                    min="0"
                  />
                </div>
              </div>
              
              {/* Availability */}
              <div className="mb-6">
                <h4 className="font-medium text-gray-900 mb-2">Availability</h4>
                <div className="flex items-center">
                  <input
                    id="mobile-in-stock"
                    type="checkbox"
                    checked={filters.in_stock}
                    onChange={(e) => handleFilterChange('in_stock', e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="mobile-in-stock" className="ml-2 text-sm text-gray-700">
                    In Stock Only
                  </label>
                </div>
              </div>
            </div>
            
            <div className="absolute bottom-0 left-0 right-0 p-4 border-t bg-white">
              <Button
                variant="primary"
                fullWidth
                onClick={toggleFilterDrawer}
              >
                Apply Filters
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductsPage;
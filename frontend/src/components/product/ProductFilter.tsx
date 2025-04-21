import React, { useState } from 'react';
import { twMerge } from 'tailwind-merge';
import { Category, Brand } from '../../types';
import Button from '../ui/Button';
import Badge from '../ui/Badge';

export interface ProductFilterProps {
  categories: Category[];
  brands: Brand[];
  selectedCategory: string | null;
  selectedBrand: string | null;
  priceRange: [number, number];
  onCategoryChange: (categoryId: string | null) => void;
  onBrandChange: (brandId: string | null) => void;
  onPriceRangeChange: (range: [number, number]) => void;
  onClearFilters: () => void;
  className?: string;
  mobileView?: boolean;
  onCloseMobile?: () => void;
}

const ProductFilter: React.FC<ProductFilterProps> = ({
  categories,
  brands,
  selectedCategory,
  selectedBrand,
  priceRange,
  onCategoryChange,
  onBrandChange,
  onPriceRangeChange,
  onClearFilters,
  className,
  mobileView = false,
  onCloseMobile,
}) => {
  const [minPrice, setMinPrice] = useState(priceRange[0].toString());
  const [maxPrice, setMaxPrice] = useState(priceRange[1].toString());
  const [expandedSections, setExpandedSections] = useState({
    categories: true,
    brands: true,
    price: true,
  });

  // Toggle section visibility
  const toggleSection = (section: 'categories' | 'brands' | 'price') => {
    setExpandedSections({
      ...expandedSections,
      [section]: !expandedSections[section],
    });
  };

  // Handle price range submission
  const handlePriceSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const min = parseInt(minPrice) || 0;
    const max = parseInt(maxPrice) || 1000;
    onPriceRangeChange([min, max]);
  };

  // Count active filters
  const getActiveFilterCount = (): number => {
    let count = 0;
    if (selectedCategory !== null) count++;
    if (selectedBrand !== null) count++;
    
    // Check if price range is different from default
    if (parseInt(minPrice) !== priceRange[0] || parseInt(maxPrice) !== priceRange[1]) {
      count++;
    }
    
    return count;
  };

  // Filter section component
  const FilterSection: React.FC<{
    title: string;
    children: React.ReactNode;
    isExpanded: boolean;
    onToggle: () => void;
  }> = ({ title, children, isExpanded, onToggle }) => {
    return (
      <div className="border-b border-neutral-200 pb-4 mb-4 last:border-0 last:mb-0 last:pb-0">
        <button
          type="button"
          className="flex w-full items-center justify-between text-sm font-medium text-neutral-900 focus:outline-none"
          onClick={onToggle}
        >
          <span>{title}</span>
          <span className="ml-6 flex items-center">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className={`h-5 w-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </span>
        </button>
        {isExpanded && (
          <div className="pt-4 space-y-2">
            {children}
          </div>
        )}
      </div>
    );
  };

  // Active filters section
  const ActiveFilters = () => {
    const activeCount = getActiveFilterCount();
    
    if (activeCount === 0) return null;
    
    return (
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-medium text-neutral-900">Active Filters</h3>
          <Button
            variant="link"
            size="sm"
            onClick={onClearFilters}
          >
            Clear All
          </Button>
        </div>
        <div className="flex flex-wrap gap-2">
          {selectedCategory !== null && (
            <Badge
              variant="primary"
              size="sm"
              shape="pill"
              removable
              onRemove={() => onCategoryChange(null)}
            >
              {categories.find(c => c.id === selectedCategory)?.name || 'Category'}
            </Badge>
          )}
          
          {selectedBrand !== null && (
            <Badge
              variant="secondary"
              size="sm"
              shape="pill"
              removable
              onRemove={() => onBrandChange(null)}
            >
              {brands.find(b => b.id === selectedBrand)?.name || 'Brand'}
            </Badge>
          )}
          
          {(parseInt(minPrice) !== priceRange[0] || parseInt(maxPrice) !== priceRange[1]) && (
            <Badge
              variant="info"
              size="sm"
              shape="pill"
              removable
              onRemove={() => {
                setMinPrice(priceRange[0].toString());
                setMaxPrice(priceRange[1].toString());
                onPriceRangeChange(priceRange);
              }}
            >
              ${minPrice} - ${maxPrice}
            </Badge>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className={twMerge('bg-white rounded-lg p-4', mobileView ? 'h-full overflow-auto' : '', className)}>
      {mobileView && (
        <div className="flex justify-between items-center mb-4 sticky top-0 bg-white z-10 pb-2 border-b border-neutral-200">
          <h2 className="text-lg font-medium">Filters</h2>
          <button
            type="button"
            className="text-neutral-500 hover:text-neutral-700"
            onClick={onCloseMobile}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}
      
      <ActiveFilters />
      
      {/* Categories */}
      <FilterSection
        title="Categories"
        isExpanded={expandedSections.categories}
        onToggle={() => toggleSection('categories')}
      >
        <div className="space-y-2 max-h-60 overflow-y-auto">
          <div className="flex items-center">
            <input
              id="category-all"
              name="category"
              type="radio"
              className="h-4 w-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500"
              checked={selectedCategory === null}
              onChange={() => onCategoryChange(null)}
            />
            <label htmlFor="category-all" className="ml-3 text-sm text-neutral-700">
              All Categories
            </label>
          </div>
          {categories.map((category) => (
            <div key={category.id} className="flex items-center">
              <input
                id={`category-${category.id}`}
                name="category"
                type="radio"
                className="h-4 w-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500"
                checked={selectedCategory === category.id}
                onChange={() => onCategoryChange(category.id)}
              />
              <label htmlFor={`category-${category.id}`} className="ml-3 text-sm text-neutral-700">
                {category.name}
              </label>
              {category.product_count !== undefined && (
                <span className="ml-auto text-xs text-neutral-500">({category.product_count})</span>
              )}
            </div>
          ))}
        </div>
      </FilterSection>

      {/* Brands */}
      <FilterSection
        title="Brands"
        isExpanded={expandedSections.brands}
        onToggle={() => toggleSection('brands')}
      >
        <div className="space-y-2 max-h-60 overflow-y-auto">
          <div className="flex items-center">
            <input
              id="brand-all"
              name="brand"
              type="radio"
              className="h-4 w-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500"
              checked={selectedBrand === null}
              onChange={() => onBrandChange(null)}
            />
            <label htmlFor="brand-all" className="ml-3 text-sm text-neutral-700">
              All Brands
            </label>
          </div>
          {brands.map((brand) => (
            <div key={brand.id} className="flex items-center">
              <input
                id={`brand-${brand.id}`}
                name="brand"
                type="radio"
                className="h-4 w-4 text-primary-600 border-neutral-300 rounded focus:ring-primary-500"
                checked={selectedBrand === brand.id}
                onChange={() => onBrandChange(brand.id)}
              />
              <label htmlFor={`brand-${brand.id}`} className="ml-3 text-sm text-neutral-700">
                {brand.name}
              </label>
              {brand.product_count !== undefined && (
                <span className="ml-auto text-xs text-neutral-500">({brand.product_count})</span>
              )}
            </div>
          ))}
        </div>
      </FilterSection>

      {/* Price Range */}
      <FilterSection
        title="Price Range"
        isExpanded={expandedSections.price}
        onToggle={() => toggleSection('price')}
      >
        <form onSubmit={handlePriceSubmit}>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-neutral-700">
              ${minPrice} - ${maxPrice}
            </span>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="min-price" className="block text-xs text-neutral-500 mb-1">
                Min Price
              </label>
              <input
                type="number"
                id="min-price"
                name="min-price"
                min="0"
                className="w-full rounded-md border-neutral-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="max-price" className="block text-xs text-neutral-500 mb-1">
                Max Price
              </label>
              <input
                type="number"
                id="max-price"
                name="max-price"
                min="0"
                className="w-full rounded-md border-neutral-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
              />
            </div>
          </div>
          
          <Button type="submit" variant="outline" size="sm" fullWidth>
            Apply Price Range
          </Button>
        </form>
      </FilterSection>
      
      {mobileView && (
        <div className="sticky bottom-0 bg-white pt-4 border-t border-neutral-200 mt-4">
          <div className="flex space-x-4">
            <Button
              variant="outline"
              size="md"
              fullWidth
              onClick={onClearFilters}
            >
              Clear All
            </Button>
            <Button
              variant="primary"
              size="md"
              fullWidth
              onClick={onCloseMobile}
            >
              Apply Filters
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductFilter;
import React, { useState } from 'react';
import { twMerge } from 'tailwind-merge';
import { ProductListItem } from '../../types';
import ProductCard from './ProductCard';

export interface ProductGridProps {
  products: ProductListItem[];
  loading?: boolean;
  emptyMessage?: string;
  columns?: 2 | 3 | 4 | 5;
  gap?: 'sm' | 'md' | 'lg';
  className?: string;
  showQuickView?: boolean;
  showWishlist?: boolean;
}

const ProductGrid: React.FC<ProductGridProps> = ({
  products,
  loading = false,
  emptyMessage = 'No products found',
  columns = 4,
  gap = 'md',
  className,
  showQuickView = true,
  showWishlist = true,
}) => {
  const [quickViewProduct, setQuickViewProduct] = useState<ProductListItem | null>(null);

  // Column classes
  const columnClasses = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
    5: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5',
  };

  // Gap classes
  const gapClasses = {
    sm: 'gap-4',
    md: 'gap-6',
    lg: 'gap-8',
  };

  // Handle quick view
  const handleQuickView = (product: ProductListItem) => {
    setQuickViewProduct(product);
    // Here you would typically open a modal or drawer
    console.log('Quick view:', product);
  };

  // Handle add to wishlist
  const handleAddToWishlist = (product: ProductListItem) => {
    // Implement wishlist functionality
    console.log('Add to wishlist:', product);
  };

  // Loading skeleton
  if (loading) {
    return (
      <div className={twMerge(`grid ${columnClasses[columns]} ${gapClasses[gap]} animate-pulse`, className)}>
        {Array.from({ length: 8 }).map((_, index) => (
          <div
            key={index}
            className="bg-white rounded-lg shadow-sm overflow-hidden"
          >
            <div className="aspect-square bg-neutral-200" />
            <div className="p-4 space-y-3">
              <div className="h-2 bg-neutral-200 rounded w-1/4" />
              <div className="h-4 bg-neutral-200 rounded w-3/4" />
              <div className="h-2 bg-neutral-200 rounded w-1/2" />
              <div className="flex justify-between items-center pt-2">
                <div className="h-5 bg-neutral-200 rounded w-1/4" />
                <div className="h-3 bg-neutral-200 rounded w-1/4" />
              </div>
              <div className="h-8 bg-neutral-200 rounded w-full mt-3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Empty state
  if (products.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-12 w-12 text-neutral-400 mb-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
          />
        </svg>
        <h3 className="text-lg font-medium text-neutral-900 mb-1">{emptyMessage}</h3>
        <p className="text-neutral-500">Try adjusting your search or filter to find what you're looking for.</p>
      </div>
    );
  }

  return (
    <div className={twMerge(`grid ${columnClasses[columns]} ${gapClasses[gap]}`, className)}>
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onQuickView={showQuickView ? handleQuickView : undefined}
          onAddToWishlist={showWishlist ? handleAddToWishlist : undefined}
        />
      ))}
    </div>
  );
};

export default ProductGrid;
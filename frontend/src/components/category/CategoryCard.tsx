import React from 'react';
import { Link } from 'react-router-dom';
import { Category } from '../../types';

interface CategoryCardProps {
  category: Category;
  className?: string;
}

const CategoryCard: React.FC<CategoryCardProps> = ({ category, className = '' }) => {
  return (
    <Link
      to={`/products?category=${category.id}`}
      className={`block group relative rounded-lg overflow-hidden bg-white shadow-sm hover:shadow-md transition-all duration-300 ${className}`}
    >
      <div className="aspect-square">
        {category.image_url ? (
          <img
            src={category.image_url}
            alt={category.name}
            className="h-full w-full object-cover object-center transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="h-full w-full bg-gray-200 flex items-center justify-center">
            <svg
              className="h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}
      </div>
      
      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent opacity-80 group-hover:opacity-90 transition-opacity" />
      
      <div className="absolute bottom-0 left-0 right-0 p-4">
        <h3 className="text-lg font-semibold text-white">{category.name}</h3>
        {category.product_count !== undefined && (
          <p className="text-sm text-gray-200 mt-1">
            {category.product_count} {category.product_count === 1 ? 'product' : 'products'}
          </p>
        )}
      </div>
    </Link>
  );
};

export default CategoryCard;
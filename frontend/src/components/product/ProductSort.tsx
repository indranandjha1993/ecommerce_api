import React from 'react';

interface ProductSortProps {
  value: string;
  onChange: (value: string) => void;
}

const ProductSort: React.FC<ProductSortProps> = ({ value, onChange }) => {
  return (
    <div className="flex items-center">
      <label htmlFor="sort-by" className="text-sm font-medium text-gray-700 mr-2">
        Sort by:
      </label>
      <select
        id="sort-by"
        name="sort-by"
        className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="newest">Newest</option>
        <option value="price_asc">Price: Low to High</option>
        <option value="price_desc">Price: High to Low</option>
        <option value="name_asc">Name: A to Z</option>
        <option value="name_desc">Name: Z to A</option>
        <option value="rating_desc">Highest Rated</option>
        <option value="popularity">Popularity</option>
      </select>
    </div>
  );
};

export default ProductSort;
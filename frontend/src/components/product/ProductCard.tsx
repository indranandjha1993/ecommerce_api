import React from 'react';
import { Link } from 'react-router-dom';
import { twMerge } from 'tailwind-merge';
import { ProductListItem } from '../../types';
import { formatPrice, calculateDiscount } from '../../utils/formatters';
import Badge from '../ui/Badge';
import Button from '../ui/Button';
import Rating from '../ui/Rating';
import Card from '../ui/Card';
import { useCart } from '../../hooks/useCart';

interface ProductCardProps {
  product: ProductListItem;
  className?: string;
  onQuickView?: (product: ProductListItem) => void;
  onAddToWishlist?: (product: ProductListItem) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ 
  product, 
  className,
  onQuickView,
  onAddToWishlist
}) => {
  const { addToCart, loading } = useCart();
  
  const handleAddToCart = async (e?: React.MouseEvent) => {
    if (e) e.preventDefault();
    await addToCart({
      product_id: product.id,
      quantity: 1,
    });
  };
  
  const handleQuickView = (e: React.MouseEvent) => {
    e.preventDefault();
    if (onQuickView) {
      onQuickView(product);
    }
  };

  const handleAddToWishlist = (e: React.MouseEvent) => {
    e.preventDefault();
    if (onAddToWishlist) {
      onAddToWishlist(product);
    }
  };
  
  const discount = calculateDiscount(product.price, product.compare_price);
  
  return (
    <Card
      as={Link}
      to={`/products/${product.slug}`}
      className={twMerge('group relative overflow-hidden transition-all duration-300 hover:-translate-y-1', className)}
      variant="default"
      padding="none"
      shadow="sm"
      hoverEffect={false}
      clickable
    >
      {/* Product badges */}
      <div className="absolute top-2 left-2 z-10 flex flex-col gap-2">
        {product.is_new && (
          <Badge variant="primary" shape="pill" size="sm">
            New
          </Badge>
        )}
        {product.is_featured && (
          <Badge variant="secondary" shape="pill" size="sm">
            Featured
          </Badge>
        )}
        {discount > 0 && (
          <Badge variant="danger" shape="pill" size="sm">
            {discount}% Off
          </Badge>
        )}
        {!product.is_in_stock && (
          <Badge variant="neutral" shape="pill" size="sm">
            Out of Stock
          </Badge>
        )}
      </div>

      {/* Quick actions */}
      <div className="absolute top-2 right-2 z-10 flex flex-col gap-2 opacity-0 transform translate-x-4 transition-all duration-300 group-hover:opacity-100 group-hover:translate-x-0">
        {onAddToWishlist && (
          <Button
            variant="ghost"
            size="sm"
            pill
            className="w-8 h-8 p-0 bg-white text-primary-600 hover:bg-primary-50 hover:text-primary-700 shadow-md"
            onClick={handleAddToWishlist}
            aria-label="Add to wishlist"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="w-4 h-4"
            >
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
            </svg>
          </Button>
        )}
        {onQuickView && (
          <Button
            variant="ghost"
            size="sm"
            pill
            className="w-8 h-8 p-0 bg-white text-primary-600 hover:bg-primary-50 hover:text-primary-700 shadow-md"
            onClick={handleQuickView}
            aria-label="Quick view"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="w-4 h-4"
            >
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </Button>
        )}
      </div>

      {/* Product image */}
      <div className="relative aspect-square overflow-hidden bg-neutral-100">
        {product.primary_image ? (
          <img
            src={product.primary_image.image_url}
            alt={product.primary_image.alt_text || product.name}
            className="w-full h-full object-cover object-center transition-transform duration-500 group-hover:scale-110"
          />
        ) : (
          <div className="h-full w-full bg-neutral-200 flex items-center justify-center">
            <span className="text-neutral-500">No image</span>
          </div>
        )}
        {!product.is_in_stock && (
          <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center">
            <span className="text-white font-medium text-lg">Out of Stock</span>
          </div>
        )}
      </div>

      {/* Product info */}
      <div className="p-4">
        {/* Category */}
        {product.category && (
          <Link 
            to={`/categories/${product.category.slug}`}
            className="text-xs text-neutral-500 hover:text-neutral-700"
            onClick={(e) => e.stopPropagation()}
          >
            {product.category.name}
          </Link>
        )}
        
        {/* Product name */}
        <h3 className="mt-1 font-medium text-neutral-900 truncate-2 min-h-[2.5rem] hover:text-primary-600">
          {product.name}
        </h3>
        
        {/* Brand */}
        {product.brand && (
          <Link 
            to={`/brands/${product.brand.slug}`}
            className="mt-1 text-xs text-neutral-500 hover:text-neutral-700 block"
            onClick={(e) => e.stopPropagation()}
          >
            {product.brand.name}
          </Link>
        )}
        
        <div className="mt-2 flex items-center justify-between">
          <div className="flex items-baseline gap-1">
            <span className="font-semibold text-neutral-900">
              {formatPrice(product.price)}
            </span>
            {product.compare_price && (
              <span className="text-sm text-neutral-500 line-through">
                {formatPrice(product.compare_price)}
              </span>
            )}
          </div>
          
          {/* Rating */}
          {product.average_rating && (
            <div className="flex items-center gap-1">
              <Rating 
                value={product.average_rating} 
                size="sm" 
                readOnly 
              />
              {product.review_count > 0 && (
                <span className="text-xs text-neutral-500">({product.review_count})</span>
              )}
            </div>
          )}
        </div>

        {/* Add to cart button */}
        <div className="mt-3">
          <Button
            variant={product.is_in_stock ? 'primary' : 'outline'}
            size="sm"
            fullWidth
            onClick={handleAddToCart}
            isLoading={loading}
            disabled={!product.is_in_stock}
            animated
          >
            {product.is_in_stock ? 'Add to Cart' : 'Out of Stock'}
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default ProductCard;
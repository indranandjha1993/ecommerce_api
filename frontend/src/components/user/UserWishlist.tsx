import React from 'react';
import { Link } from 'react-router-dom';
import { twMerge } from 'tailwind-merge';
import Card from '../ui/Card';
import Button from '../ui/Button';
import { Product } from '../../types';
import { formatPrice } from '../../utils/formatters';
import { useCart } from '../../hooks/useCart';

export interface UserWishlistProps {
  products: Product[];
  onRemoveFromWishlist: (productId: string) => Promise<void>;
  isLoading?: boolean;
  className?: string;
}

const UserWishlist: React.FC<UserWishlistProps> = ({
  products,
  onRemoveFromWishlist,
  isLoading = false,
  className,
}) => {
  const { addToCart, loading: cartLoading } = useCart();

  // Handle add to cart
  const handleAddToCart = async (productId: string) => {
    await addToCart({
      product_id: productId,
      quantity: 1,
    });
  };

  // Handle remove from wishlist
  const handleRemoveFromWishlist = async (productId: string) => {
    await onRemoveFromWishlist(productId);
  };

  // Loading skeleton
  if (isLoading) {
    return (
      <Card 
        className={twMerge('w-full', className)}
        padding="lg"
        shadow="sm"
      >
        <div className="animate-pulse">
          <div className="h-8 bg-neutral-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...Array(4)].map((_, index) => (
              <div key={index} className="flex space-x-4">
                <div className="h-24 w-24 bg-neutral-200 rounded"></div>
                <div className="flex-1">
                  <div className="h-5 bg-neutral-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-neutral-200 rounded w-1/2 mb-2"></div>
                  <div className="h-8 bg-neutral-200 rounded w-1/3 mt-4"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card 
      className={twMerge('w-full', className)}
      padding="lg"
      shadow="sm"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-neutral-900">Your Wishlist</h2>
      </div>

      {products.length === 0 ? (
        <div className="text-center py-8">
          <svg
            className="mx-auto h-12 w-12 text-neutral-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-neutral-900">Your wishlist is empty</h3>
          <p className="mt-1 text-sm text-neutral-500">Save items you love to your wishlist.</p>
          <div className="mt-6">
            <Button
              as={Link}
              to="/products"
              variant="primary"
              size="md"
            >
              Discover Products
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {products.map((product) => (
            <div key={product.id} className="flex flex-col sm:flex-row border border-neutral-200 rounded-lg overflow-hidden">
              <div className="w-full sm:w-32 h-32 flex-shrink-0">
                {product.primary_image ? (
                  <img
                    src={product.primary_image.image_url}
                    alt={product.primary_image.alt_text || product.name}
                    className="h-full w-full object-cover object-center"
                  />
                ) : (
                  <div className="h-full w-full bg-neutral-200 flex items-center justify-center">
                    <span className="text-neutral-500">No image</span>
                  </div>
                )}
              </div>
              
              <div className="flex-1 p-4 flex flex-col">
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-neutral-900">
                    <Link to={`/products/${product.slug}`} className="hover:text-primary-600">
                      {product.name}
                    </Link>
                  </h3>
                  
                  {product.brand && (
                    <p className="mt-1 text-xs text-neutral-500">
                      {product.brand.name}
                    </p>
                  )}
                  
                  <div className="mt-2 flex items-center">
                    <span className="text-sm font-medium text-neutral-900">
                      {formatPrice(product.price)}
                    </span>
                    
                    {product.compare_price && product.compare_price > product.price && (
                      <span className="ml-2 text-xs text-neutral-500 line-through">
                        {formatPrice(product.compare_price)}
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="mt-4 flex flex-col sm:flex-row sm:items-center gap-2">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleAddToCart(product.id)}
                    isLoading={cartLoading}
                    disabled={!product.is_in_stock}
                  >
                    {product.is_in_stock ? 'Add to Cart' : 'Out of Stock'}
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleRemoveFromWishlist(product.id)}
                  >
                    Remove
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};

export default UserWishlist;
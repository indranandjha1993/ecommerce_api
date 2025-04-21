import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ProductWithRelations, ProductVariant, CartItemCreate } from '../../types';
import { formatPrice, calculateDiscount } from '../../utils/formatters';
import { useCart } from '../../hooks/useCart';
import { useDispatch } from 'react-redux';
import { addNotification } from '../../store/slices/uiSlice';
import Button from '../ui/Button';
import Badge from '../ui/Badge';

interface ProductDetailProps {
  product: ProductWithRelations;
}

const ProductDetail: React.FC<ProductDetailProps> = ({ product }) => {
  const dispatch = useDispatch();
  const { addToCart, loading } = useCart();
  
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(
    product.variants.length > 0 ? product.variants[0] : null
  );
  const [quantity, setQuantity] = useState(1);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  
  const handleQuantityChange = (newQuantity: number) => {
    if (newQuantity >= 1) {
      setQuantity(newQuantity);
    }
  };
  
  const handleVariantChange = (variant: ProductVariant) => {
    setSelectedVariant(variant);
  };
  
  const handleAddToCart = async () => {
    const cartItem: CartItemCreate = {
      product_id: product.id,
      quantity,
    };
    
    if (selectedVariant) {
      cartItem.variant_id = selectedVariant.id;
    }
    
    const success = await addToCart(cartItem);
    
    if (success) {
      dispatch(
        addNotification({
          type: 'success',
          message: `${product.name} added to cart!`,
        })
      );
    } else {
      dispatch(
        addNotification({
          type: 'error',
          message: 'Failed to add item to cart. Please try again.',
        })
      );
    }
  };
  
  // Determine the current price and discount
  const currentPrice = selectedVariant?.price || product.price;
  const comparePrice = selectedVariant?.compare_price || product.compare_price;
  const discount = calculateDiscount(currentPrice, comparePrice);
  
  // Get all images (product images + variant images)
  const allImages = [
    ...product.images,
    ...(selectedVariant ? selectedVariant.images : []),
  ];
  
  // Get the current image
  const currentImage = allImages[activeImageIndex] || product.primary_image;
  
  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-6">
        {/* Product Images */}
        <div>
          {/* Main Image */}
          <div className="aspect-square overflow-hidden rounded-lg border border-gray-200 mb-4">
            {currentImage ? (
              <img
                src={currentImage.image_url}
                alt={currentImage.alt_text || product.name}
                className="h-full w-full object-cover object-center"
              />
            ) : (
              <div className="h-full w-full bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500">No image available</span>
              </div>
            )}
          </div>
          
          {/* Thumbnail Images */}
          {allImages.length > 1 && (
            <div className="grid grid-cols-5 gap-2">
              {allImages.map((image, index) => (
                <button
                  key={image.id}
                  className={`aspect-square rounded-md overflow-hidden border ${
                    index === activeImageIndex
                      ? 'border-blue-500 ring-2 ring-blue-500'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setActiveImageIndex(index)}
                >
                  <img
                    src={image.image_url}
                    alt={image.alt_text || `${product.name} - Image ${index + 1}`}
                    className="h-full w-full object-cover object-center"
                  />
                </button>
              ))}
            </div>
          )}
        </div>
        
        {/* Product Info */}
        <div>
          {/* Breadcrumbs */}
          <nav className="flex items-center text-sm text-gray-500 mb-4">
            <Link to="/" className="hover:text-gray-700">Home</Link>
            <span className="mx-2">/</span>
            {product.category && (
              <>
                <Link to={`/categories/${product.category.slug}`} className="hover:text-gray-700">
                  {product.category.name}
                </Link>
                <span className="mx-2">/</span>
              </>
            )}
            <span className="text-gray-900">{product.name}</span>
          </nav>
          
          {/* Product Name */}
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{product.name}</h1>
          
          {/* Brand */}
          {product.brand && (
            <Link
              to={`/brands/${product.brand.slug}`}
              className="inline-block text-sm text-gray-600 hover:text-blue-600 mb-4"
            >
              By {product.brand.name}
            </Link>
          )}
          
          {/* Rating */}
          {product.average_rating !== undefined && (
            <div className="flex items-center mb-4">
              <div className="flex items-center">
                {[1, 2, 3, 4, 5].map((star) => (
                  <svg
                    key={star}
                    className={`h-5 w-5 ${
                      star <= Math.round(product.average_rating || 0)
                        ? 'text-yellow-400'
                        : 'text-gray-300'
                    }`}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              <span className="ml-2 text-sm text-gray-600">
                {product.average_rating?.toFixed(1)} out of 5
              </span>
            </div>
          )}
          
          {/* Price */}
          <div className="flex items-center mb-6">
            <span className="text-2xl font-bold text-gray-900">
              {formatPrice(currentPrice)}
            </span>
            
            {comparePrice && comparePrice > currentPrice && (
              <span className="ml-2 text-lg text-gray-500 line-through">
                {formatPrice(comparePrice)}
              </span>
            )}
            
            {discount && (
              <Badge variant="danger" className="ml-4">
                {discount}% OFF
              </Badge>
            )}
          </div>
          
          {/* Short Description */}
          {product.short_description && (
            <div className="mb-6">
              <p className="text-gray-700">{product.short_description}</p>
            </div>
          )}
          
          {/* Variants */}
          {product.variants.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-900 mb-2">Options</h3>
              <div className="grid grid-cols-2 gap-2">
                {product.variants.map((variant) => (
                  <button
                    key={variant.id}
                    className={`border rounded-md py-2 px-3 flex items-center justify-between ${
                      selectedVariant?.id === variant.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                    onClick={() => handleVariantChange(variant)}
                  >
                    <span className="text-sm">
                      {variant.name || 
                        variant.variant_attributes
                          .map((attr) => attr.attribute_value.value)
                          .join(' / ')}
                    </span>
                    {variant.price && (
                      <span className="text-sm font-medium">
                        {formatPrice(variant.price)}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {/* Quantity */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-900 mb-2">Quantity</h3>
            <div className="flex items-center">
              <button
                type="button"
                className="w-10 h-10 border border-gray-300 rounded-l-md flex items-center justify-center text-gray-600 hover:bg-gray-100"
                onClick={() => handleQuantityChange(quantity - 1)}
                disabled={quantity <= 1}
              >
                -
              </button>
              <input
                type="number"
                className="w-16 h-10 border-t border-b border-gray-300 text-center"
                value={quantity}
                onChange={(e) => handleQuantityChange(parseInt(e.target.value) || 1)}
                min="1"
              />
              <button
                type="button"
                className="w-10 h-10 border border-gray-300 rounded-r-md flex items-center justify-center text-gray-600 hover:bg-gray-100"
                onClick={() => handleQuantityChange(quantity + 1)}
              >
                +
              </button>
            </div>
          </div>
          
          {/* Add to Cart */}
          <div className="flex space-x-4 mb-6">
            <Button
              variant="primary"
              size="lg"
              onClick={handleAddToCart}
              isLoading={loading}
              disabled={!product.is_active || (product.inventory_quantity !== undefined && product.inventory_quantity <= 0)}
              fullWidth
            >
              {product.inventory_quantity !== undefined && product.inventory_quantity <= 0
                ? 'Out of Stock'
                : 'Add to Cart'}
            </Button>
            
            <Button
              variant="outline"
              size="lg"
              onClick={() => {
                // Add to wishlist functionality
              }}
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
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                />
              </svg>
            </Button>
          </div>
          
          {/* Product Attributes */}
          {product.attribute_values.length > 0 && (
            <div className="border-t border-gray-200 pt-4">
              <h3 className="text-sm font-medium text-gray-900 mb-2">Specifications</h3>
              <dl className="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
                {product.attribute_values.map((attrValue) => (
                  <div key={attrValue.id} className="border-b border-gray-200 pb-2">
                    <dt className="text-sm font-medium text-gray-500">{attrValue.attribute.name}</dt>
                    <dd className="mt-1 text-sm text-gray-900">{attrValue.value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
          
          {/* SKU, Barcode, etc. */}
          <div className="border-t border-gray-200 pt-4 mt-4">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
              {product.sku && (
                <div className="border-b border-gray-200 pb-2">
                  <dt className="text-sm font-medium text-gray-500">SKU</dt>
                  <dd className="mt-1 text-sm text-gray-900">{product.sku}</dd>
                </div>
              )}
              {product.barcode && (
                <div className="border-b border-gray-200 pb-2">
                  <dt className="text-sm font-medium text-gray-500">Barcode</dt>
                  <dd className="mt-1 text-sm text-gray-900">{product.barcode}</dd>
                </div>
              )}
              {product.weight && (
                <div className="border-b border-gray-200 pb-2">
                  <dt className="text-sm font-medium text-gray-500">Weight</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {product.weight} {product.weight_unit || 'kg'}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>
      </div>
      
      {/* Product Description */}
      {product.description && (
        <div className="border-t border-gray-200 p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Description</h2>
          <div className="prose prose-sm max-w-none text-gray-700">
            {product.description.split('\n').map((paragraph, index) => (
              <p key={index} className="mb-4">
                {paragraph}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetail;
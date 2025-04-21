import React from 'react';
import { Link } from 'react-router-dom';
import { CartItem as CartItemType } from '../../types';
import { formatPrice } from '../../utils/formatters';
import { useCart } from '../../contexts/CartContext';

interface CartItemProps {
  item: CartItemType;
}

const CartItem: React.FC<CartItemProps> = ({ item }) => {
  const { updateItem, removeItem, isLoading } = useCart();

  const handleQuantityChange = async (newQuantity: number) => {
    if (newQuantity >= 1) {
      await updateItem(item.id, newQuantity);
    }
  };

  const handleRemove = async () => {
    await removeItem(item.id);
  };

  return (
    <div className="flex py-6 border-b border-gray-200">
      {/* Product image */}
      <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-md border border-gray-200">
        {item.product.primary_image ? (
          <img
            src={item.product.primary_image.image_url}
            alt={item.product.primary_image.alt_text || item.product.name}
            className="h-full w-full object-cover object-center"
          />
        ) : (
          <div className="h-full w-full bg-gray-200 flex items-center justify-center">
            <span className="text-gray-500 text-xs">No image</span>
          </div>
        )}
      </div>

      {/* Product details */}
      <div className="ml-4 flex flex-1 flex-col">
        <div>
          <div className="flex justify-between text-base font-medium text-gray-900">
            <h3>
              <Link to={`/products/${item.product.slug}`}>
                {item.product.name}
              </Link>
            </h3>
            <p className="ml-4">{formatPrice(item.unit_price)}</p>
          </div>
          {item.variant && (
            <p className="mt-1 text-sm text-gray-500">
              {item.variant.name || 'Variant'}
            </p>
          )}
        </div>
        
        <div className="flex flex-1 items-end justify-between text-sm">
          {/* Quantity selector */}
          <div className="flex items-center">
            <span className="text-gray-500 mr-2">Qty</span>
            <div className="flex items-center border border-gray-300 rounded">
              <button
                type="button"
                className="w-8 h-8 flex items-center justify-center text-gray-600 hover:bg-gray-100"
                onClick={() => handleQuantityChange(item.quantity - 1)}
                disabled={isLoading || item.quantity <= 1}
              >
                -
              </button>
              <span className="w-8 h-8 flex items-center justify-center">
                {item.quantity}
              </span>
              <button
                type="button"
                className="w-8 h-8 flex items-center justify-center text-gray-600 hover:bg-gray-100"
                onClick={() => handleQuantityChange(item.quantity + 1)}
                disabled={isLoading}
              >
                +
              </button>
            </div>
          </div>

          {/* Remove button */}
          <div className="flex">
            <button
              type="button"
              className="font-medium text-blue-600 hover:text-blue-500"
              onClick={handleRemove}
              disabled={isLoading}
            >
              Remove
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartItem;
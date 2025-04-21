import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../../contexts/CartContext';
import { formatPrice } from '../../utils/formatters';
import Button from '../ui/Button';
import CartItem from './CartItem';
import LoadingSpinner from '../ui/LoadingSpinner';
import { twMerge } from 'tailwind-merge';

interface CartDrawerProps {
  onClose: () => void;
}

const CartDrawer: React.FC<CartDrawerProps> = ({ onClose }) => {
  const { items, refreshCart, isLoading, clearCart, totalAmount, itemCount } = useCart();

  useEffect(() => {
    refreshCart();
  }, [refreshCart]);

  const closeDrawer = () => {
    onClose();
  };

  const handleClearCart = async () => {
    await clearCart();
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 flex max-w-full">
      <div 
        className="w-screen max-w-md transform transition-transform duration-300 ease-in-out"
        style={{ boxShadow: '-10px 0 30px rgba(0, 0, 0, 0.15)' }}
      >
        <div className="flex h-full flex-col overflow-hidden bg-white">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-5 sm:px-6 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 flex items-center">
              <svg 
                className="h-6 w-6 text-blue-600 mr-2" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" 
                />
              </svg>
              Shopping Cart
              {itemCount > 0 && (
                <span className="ml-2 text-sm text-gray-500">({itemCount} {itemCount === 1 ? 'item' : 'items'})</span>
              )}
            </h2>
            <button
              type="button"
              className="rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none"
              onClick={closeDrawer}
            >
              <span className="sr-only">Close panel</span>
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
          
          {/* Content */}
          <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
            {isLoading ? (
              <div className="flex items-center justify-center h-40">
                <LoadingSpinner size="md" color="primary" variant="spinner" />
              </div>
            ) : !items || items.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="rounded-full bg-blue-50 p-6 mb-4">
                  <svg
                    className="h-12 w-12 text-blue-500"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900">Your cart is empty</h3>
                <p className="mt-2 text-sm text-gray-500 max-w-xs">
                  Looks like you haven't added anything to your cart yet. Start shopping to add items to your cart.
                </p>
                <div className="mt-6">
                  <Button
                    variant="primary"
                    onClick={closeDrawer}
                    size="lg"
                  >
                    Continue Shopping
                  </Button>
                </div>
              </div>
            ) : (
              <div>
                <div className="space-y-6 pb-6">
                  {items.map((item) => (
                    <CartItem key={item.id} item={item} />
                  ))}
                </div>
                
                {items.length > 0 && (
                  <div className="flex justify-end border-t border-gray-200 pt-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleClearCart}
                      className="text-red-600 border-red-200 hover:bg-red-50"
                    >
                      <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      Clear Cart
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Footer */}
          {items && items.length > 0 && (
            <div className="border-t border-gray-200 px-4 py-6 sm:px-6">
              <div className="space-y-4 mb-6">
                <div className="flex justify-between text-base text-gray-500">
                  <p>Subtotal</p>
                  <p>{formatPrice(totalAmount)}</p>
                </div>
                <div className="flex justify-between text-base text-gray-500">
                  <p>Shipping</p>
                  <p>Calculated at checkout</p>
                </div>
                <div className="flex justify-between text-base text-gray-500">
                  <p>Tax</p>
                  <p>Calculated at checkout</p>
                </div>
                <div className="h-px bg-gray-200 my-2"></div>
                <div className="flex justify-between text-lg font-medium text-gray-900">
                  <p>Total</p>
                  <p>{formatPrice(totalAmount)}</p>
                </div>
              </div>
              
              <div className="space-y-3">
                <Link
                  to="/checkout"
                  onClick={closeDrawer}
                  className="w-full"
                >
                  <Button
                    variant="primary"
                    fullWidth
                    size="lg"
                  >
                    Proceed to Checkout
                  </Button>
                </Link>
                <Button
                  variant="outline"
                  fullWidth
                  onClick={closeDrawer}
                >
                  Continue Shopping
                </Button>
              </div>
              
              <div className="mt-6 flex items-center justify-center space-x-4">
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-gray-400 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <span className="text-xs text-gray-500">Secure Checkout</span>
                </div>
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-gray-400 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                  </svg>
                  <span className="text-xs text-gray-500">Multiple Payment Options</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CartDrawer;
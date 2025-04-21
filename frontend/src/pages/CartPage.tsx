import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../hooks/useCart';
import { formatPrice } from '../utils/formatters';
import CartItem from '../components/cart/CartItem';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const CartPage: React.FC = () => {
  const { cart, fetchCart, loading, error, clearCart } = useCart();

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const handleClearCart = async () => {
    if (window.confirm('Are you sure you want to clear your cart?')) {
      await clearCart();
    }
  };

  if (loading && !cart) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Shopping Cart</h1>
        <div className="flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Shopping Cart</h1>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Shopping Cart</h1>
        <div className="bg-white p-8 rounded-lg shadow-sm text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
            />
          </svg>
          <h2 className="mt-2 text-lg font-medium text-gray-900">Your cart is empty</h2>
          <p className="mt-1 text-gray-500">
            Looks like you haven't added any products to your cart yet.
          </p>
          <div className="mt-6">
            <Link to="/products">
              <Button variant="primary">Continue Shopping</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Shopping Cart</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-medium text-gray-900">
                  Cart Items ({cart.items.length})
                </h2>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClearCart}
                  disabled={loading}
                >
                  Clear Cart
                </Button>
              </div>
            </div>

            <div className="divide-y divide-gray-200">
              {cart.items.map((item) => (
                <div key={item.id} className="p-6">
                  <CartItem item={item} />
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8">
            <Link to="/products">
              <Button variant="outline">
                <svg
                  className="h-5 w-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 19l-7-7m0 0l7-7m-7 7h18"
                  />
                </svg>
                Continue Shopping
              </Button>
            </Link>
          </div>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm overflow-hidden sticky top-24">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Order Summary</h2>
            </div>

            <div className="p-6 space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="text-gray-900 font-medium">{formatPrice(cart.total_amount)}</span>
              </div>

              {cart.discount_amount > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Discount</span>
                  <span className="text-green-600 font-medium">-{formatPrice(cart.discount_amount)}</span>
                </div>
              )}

              {cart.tax_amount > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax</span>
                  <span className="text-gray-900 font-medium">{formatPrice(cart.tax_amount)}</span>
                </div>
              )}

              {cart.shipping_amount > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Shipping</span>
                  <span className="text-gray-900 font-medium">{formatPrice(cart.shipping_amount)}</span>
                </div>
              )}

              <div className="border-t border-gray-200 pt-4 flex justify-between">
                <span className="text-lg font-medium text-gray-900">Total</span>
                <span className="text-lg font-bold text-gray-900">{formatPrice(cart.total_amount)}</span>
              </div>

              <div className="mt-6">
                <Link to="/checkout">
                  <Button variant="primary" fullWidth>
                    Proceed to Checkout
                  </Button>
                </Link>
              </div>

              {/* Accepted Payment Methods */}
              <div className="mt-6">
                <p className="text-xs text-gray-500 mb-2">We accept:</p>
                <div className="flex space-x-2">
                  <div className="h-8 w-12 bg-gray-100 rounded flex items-center justify-center text-gray-500">
                    Visa
                  </div>
                  <div className="h-8 w-12 bg-gray-100 rounded flex items-center justify-center text-gray-500">
                    MC
                  </div>
                  <div className="h-8 w-12 bg-gray-100 rounded flex items-center justify-center text-gray-500">
                    Amex
                  </div>
                  <div className="h-8 w-12 bg-gray-100 rounded flex items-center justify-center text-gray-500">
                    PayPal
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;
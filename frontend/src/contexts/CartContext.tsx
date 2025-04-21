import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { useAuth } from './AuthContext';
import { api } from '../utils/api';
import { CartItem, CartSummary } from '../types';

interface CartContextType {
  items: CartItem[];
  summary: CartSummary;
  isLoading: boolean;
  error: string | null;
  itemCount: number;
  totalAmount: number;
  addToCart: (item: { product_id: string; quantity: number; variant_id?: string }) => Promise<void>;
  updateCartItem: (itemId: string, quantity: number) => Promise<void>;
  removeCartItem: (itemId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  applyCoupon: (code: string) => Promise<void>;
  removeCoupon: () => Promise<void>;
  refreshCart: () => Promise<void>;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [items, setItems] = useState<CartItem[]>([]);
  const [summary, setSummary] = useState<CartSummary>({
    subtotal: 0,
    discount: 0,
    tax: 0,
    shipping: 0,
    total: 0,
    coupon: null,
  });
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch cart data on mount and when auth state changes
  useEffect(() => {
    refreshCart();
  }, [isAuthenticated]);

  // Refresh cart data
  const refreshCart = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get('/cart');
      setItems(response.data.items || []);
      setSummary(response.data.summary || {
        subtotal: 0,
        discount: 0,
        tax: 0,
        shipping: 0,
        total: 0,
        coupon: null,
      });
    } catch (err: any) {
      console.error('Failed to fetch cart:', err);
      setError('Failed to load your cart. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Add item to cart
  const addToCart = async (item: { product_id: string; quantity: number; variant_id?: string }): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      await api.post('/cart/items', item);
      await refreshCart();
    } catch (err: any) {
      console.error('Failed to add item to cart:', err);
      setError(err.response?.data?.message || 'Failed to add item to cart. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Update cart item quantity
  const updateCartItem = async (itemId: string, quantity: number): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      await api.put(`/cart/items/${itemId}`, { quantity });
      await refreshCart();
    } catch (err: any) {
      console.error('Failed to update cart item:', err);
      setError(err.response?.data?.message || 'Failed to update cart item. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Remove item from cart
  const removeCartItem = async (itemId: string): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      await api.delete(`/cart/items/${itemId}`);
      await refreshCart();
    } catch (err: any) {
      console.error('Failed to remove cart item:', err);
      setError(err.response?.data?.message || 'Failed to remove cart item. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Clear cart
  const clearCart = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      await api.delete('/cart');
      await refreshCart();
    } catch (err: any) {
      console.error('Failed to clear cart:', err);
      setError(err.response?.data?.message || 'Failed to clear cart. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Apply coupon
  const applyCoupon = async (code: string): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      await api.post('/cart/coupon', { code });
      await refreshCart();
    } catch (err: any) {
      console.error('Failed to apply coupon:', err);
      setError(err.response?.data?.message || 'Failed to apply coupon. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Remove coupon
  const removeCoupon = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      await api.delete('/cart/coupon');
      await refreshCart();
    } catch (err: any) {
      console.error('Failed to remove coupon:', err);
      setError(err.response?.data?.message || 'Failed to remove coupon. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate derived values
  const itemCount = useMemo(() => {
    return items.reduce((total, item) => total + item.quantity, 0);
  }, [items]);

  const totalAmount = useMemo(() => {
    return summary.total || summary.subtotal || 0;
  }, [summary]);

  // Provide cart context
  const value = {
    items,
    summary,
    isLoading,
    error,
    itemCount,
    totalAmount,
    addToCart,
    updateCartItem,
    removeCartItem,
    clearCart,
    applyCoupon,
    removeCoupon,
    refreshCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};

// Custom hook to use cart context
export const useCart = () => {
  const context = useContext(CartContext);
  
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  
  return context;
};
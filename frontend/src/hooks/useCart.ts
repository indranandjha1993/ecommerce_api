import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  addToCart as addToCartAction,
  updateCartItem as updateCartItemAction,
  removeCartItem as removeCartItemAction,
  clearCart as clearCartAction,
  fetchCart as fetchCartAction,
  applyCoupon as applyCouponAction,
  removeCoupon as removeCouponAction,
  selectCart,
  selectCartItemsCount,
  selectCartTotalAmount,
  selectCartLoading,
  selectCartError,
} from '../store/slices/cartSlice';
import { CartItemCreate } from '../types';
import { AppDispatch } from '../store';

export const useCart = () => {
  const dispatch = useDispatch<AppDispatch>();
  const cart = useSelector(selectCart);
  const itemsCount = useSelector(selectCartItemsCount);
  const totalAmount = useSelector(selectCartTotalAmount);
  const loading = useSelector(selectCartLoading);
  const error = useSelector(selectCartError);

  const fetchCart = useCallback(async () => {
    try {
      const resultAction = await dispatch(fetchCartAction());
      return fetchCartAction.fulfilled.match(resultAction);
    } catch (error) {
      return false;
    }
  }, [dispatch]);

  const addToCart = useCallback(
    async (item: CartItemCreate) => {
      try {
        const resultAction = await dispatch(addToCartAction(item));
        return addToCartAction.fulfilled.match(resultAction);
      } catch (error) {
        return false;
      }
    },
    [dispatch]
  );

  const updateCartItem = useCallback(
    async (itemId: string, quantity: number) => {
      try {
        const resultAction = await dispatch(updateCartItemAction({ itemId, quantity }));
        return updateCartItemAction.fulfilled.match(resultAction);
      } catch (error) {
        return false;
      }
    },
    [dispatch]
  );

  const removeCartItem = useCallback(
    async (itemId: string) => {
      try {
        const resultAction = await dispatch(removeCartItemAction(itemId));
        return removeCartItemAction.fulfilled.match(resultAction);
      } catch (error) {
        return false;
      }
    },
    [dispatch]
  );

  const clearCart = useCallback(async () => {
    try {
      const resultAction = await dispatch(clearCartAction());
      return clearCartAction.fulfilled.match(resultAction);
    } catch (error) {
      return false;
    }
  }, [dispatch]);

  const applyCoupon = useCallback(
    async (code: string) => {
      try {
        const resultAction = await dispatch(applyCouponAction(code));
        return applyCouponAction.fulfilled.match(resultAction);
      } catch (error) {
        return false;
      }
    },
    [dispatch]
  );

  const removeCoupon = useCallback(async () => {
    try {
      const resultAction = await dispatch(removeCouponAction());
      return removeCouponAction.fulfilled.match(resultAction);
    } catch (error) {
      return false;
    }
  }, [dispatch]);

  return {
    cart,
    itemsCount,
    totalAmount,
    loading,
    error,
    fetchCart,
    addToCart,
    updateCartItem,
    removeCartItem,
    clearCart,
    applyCoupon,
    removeCoupon,
  };
};
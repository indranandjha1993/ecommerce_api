import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  createOrder as createOrderAction,
  selectCheckoutLoading,
  selectCheckoutError,
} from '../store/slices/checkoutSlice';
import { AppDispatch } from '../store';

export interface CheckoutAddress {
  first_name: string;
  last_name: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone_number?: string;
}

export interface CheckoutData {
  shipping_address: CheckoutAddress;
  billing_address: CheckoutAddress;
  shipping_method: string;
  payment_method: string;
  payment_details?: any;
  email: string;
  notes?: string;
  coupon_code?: string;
}

export const useCheckout = () => {
  const dispatch = useDispatch<AppDispatch>();
  const loading = useSelector(selectCheckoutLoading);
  const error = useSelector(selectCheckoutError);

  const createOrder = useCallback(
    async (checkoutData: CheckoutData) => {
      try {
        const resultAction = await dispatch(createOrderAction(checkoutData));
        if (createOrderAction.fulfilled.match(resultAction)) {
          return resultAction.payload;
        }
        return null;
      } catch (error) {
        return null;
      }
    },
    [dispatch]
  );

  return {
    loading,
    error,
    createOrder,
  };
};
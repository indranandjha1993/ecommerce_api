import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  fetchOrders as fetchOrdersAction,
  fetchOrder as fetchOrderAction,
  selectOrders,
  selectOrder,
  selectOrdersLoading,
  selectOrdersError,
} from '../store/slices/orderSlice';
import { AppDispatch } from '../store';

export const useOrder = () => {
  const dispatch = useDispatch<AppDispatch>();
  const orders = useSelector(selectOrders);
  const order = useSelector(selectOrder);
  const loading = useSelector(selectOrdersLoading);
  const error = useSelector(selectOrdersError);

  const fetchOrders = useCallback(async () => {
    try {
      const resultAction = await dispatch(fetchOrdersAction());
      return fetchOrdersAction.fulfilled.match(resultAction);
    } catch (error) {
      return false;
    }
  }, [dispatch]);

  const fetchOrder = useCallback(
    async (orderId: string) => {
      try {
        const resultAction = await dispatch(fetchOrderAction(orderId));
        return fetchOrderAction.fulfilled.match(resultAction);
      } catch (error) {
        return false;
      }
    },
    [dispatch]
  );

  return {
    orders,
    order,
    loading,
    error,
    fetchOrders,
    fetchOrder,
  };
};
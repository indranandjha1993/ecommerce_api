import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  fetchOrders, 
  fetchOrderById, 
  fetchOrderByNumber, 
  createOrder, 
  cancelOrder,
  clearError,
  clearCurrentOrder,
  selectOrders,
  selectCurrentOrder,
  selectOrderLoading,
  selectOrderError
} from '../store/slices/orderSlice';
import { AppDispatch, RootState } from '../store';

export const useOrders = () => {
  const dispatch = useDispatch<AppDispatch>();
  
  const orders = useSelector(selectOrders);
  const currentOrder = useSelector(selectCurrentOrder);
  const loading = useSelector(selectOrderLoading);
  const error = useSelector(selectOrderError);
  
  const getOrders = useCallback((page = 1, size = 10) => {
    return dispatch(fetchOrders({ page, size }));
  }, [dispatch]);
  
  const getOrderById = useCallback((id: string) => {
    return dispatch(fetchOrderById(id));
  }, [dispatch]);
  
  const getOrderByNumber = useCallback((orderNumber: string) => {
    return dispatch(fetchOrderByNumber(orderNumber));
  }, [dispatch]);
  
  const placeOrder = useCallback((orderData: any) => {
    return dispatch(createOrder(orderData));
  }, [dispatch]);
  
  const cancelOrderById = useCallback((id: string, reason?: string) => {
    return dispatch(cancelOrder({ id, reason }));
  }, [dispatch]);
  
  const resetError = useCallback(() => {
    dispatch(clearError());
  }, [dispatch]);
  
  const resetCurrentOrder = useCallback(() => {
    dispatch(clearCurrentOrder());
  }, [dispatch]);
  
  return {
    orders,
    currentOrder,
    loading,
    error,
    fetchOrders: getOrders,
    fetchOrderById: getOrderById,
    fetchOrderByNumber: getOrderByNumber,
    createOrder: placeOrder,
    cancelOrder: cancelOrderById,
    clearError: resetError,
    resetCurrentOrder
  };
};
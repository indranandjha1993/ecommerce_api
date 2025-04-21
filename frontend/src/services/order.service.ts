import { Order } from '../types';
import { apiService } from './api';

export const orderService = {
  getOrders: (page: number = 1, size: number = 10): Promise<{ items: Order[], total: number, page: number, size: number, pages: number }> => 
    apiService.get<{ items: Order[], total: number, page: number, size: number, pages: number }>(`/orders?page=${page}&size=${size}`),
    
  getOrderById: (id: string): Promise<Order> => 
    apiService.get<Order>(`/orders/${id}`),
    
  getOrderByNumber: (orderNumber: string): Promise<Order> => 
    apiService.get<Order>(`/orders/number/${orderNumber}`),
    
  createOrder: (data: any): Promise<Order> => 
    apiService.post<Order>('/orders', data),
    
  cancelOrder: (id: string, reason?: string): Promise<Order> => 
    apiService.post<Order>(`/orders/${id}/cancel`, { reason }),
};
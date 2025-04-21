import { Cart, CartItemCreate } from '../types';
import { apiService } from './api';

export const cartService = {
  getCurrentCart: (): Promise<Cart> => 
    apiService.get<Cart>('/carts/current'),
    
  addToCart: (item: CartItemCreate): Promise<Cart> => 
    apiService.post<Cart>('/carts/items', item),
    
  updateCartItem: (itemId: string, quantity: number): Promise<Cart> => 
    apiService.patch<Cart>(`/carts/items/${itemId}`, { quantity }),
    
  removeCartItem: (itemId: string): Promise<Cart> => 
    apiService.delete<Cart>(`/carts/items/${itemId}`),
    
  clearCart: (): Promise<{ message: string }> => 
    apiService.delete<{ message: string }>('/carts/clear'),
    
  applyCoupon: (code: string): Promise<Cart> => 
    apiService.post<Cart>('/carts/apply-coupon', { code }),
    
  removeCoupon: (): Promise<Cart> => 
    apiService.delete<Cart>('/carts/remove-coupon'),
};
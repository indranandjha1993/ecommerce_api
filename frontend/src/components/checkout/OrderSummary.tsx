import React from 'react';
import { Cart } from '../../types';

interface OrderSummaryProps {
  cart: Cart | null;
  shippingMethod?: string;
}

const OrderSummary: React.FC<OrderSummaryProps> = ({ cart, shippingMethod = 'standard' }) => {
  if (!cart) return null;

  // Calculate shipping cost based on method
  const getShippingCost = (): number => {
    switch (shippingMethod) {
      case 'express':
        return 12.99;
      case 'overnight':
        return 19.99;
      case 'standard':
      default:
        return 5.99;
    }
  };

  const shippingCost = getShippingCost();
  
  // Calculate tax (example: 8% of subtotal)
  const taxRate = 0.08;
  const taxAmount = cart.total_amount * taxRate;
  
  // Calculate total
  const totalAmount = cart.total_amount + shippingCost + taxAmount;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 sticky top-20">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Order Summary</h2>
      
      <div className="flow-root">
        <ul className="-my-4 divide-y divide-gray-200">
          {cart.items.map((item) => (
            <li key={item.id} className="py-4 flex">
              <div className="flex-shrink-0 w-16 h-16 rounded-md overflow-hidden">
                <img
                  src={item.product.primary_image?.image_url || '/placeholder-product.png'}
                  alt={item.product.name}
                  className="w-full h-full object-center object-cover"
                />
              </div>
              <div className="ml-4 flex-1 flex flex-col">
                <div>
                  <div className="flex justify-between text-sm font-medium text-gray-900">
                    <h4 className="line-clamp-1">{item.product.name}</h4>
                    <p className="ml-2">${item.total_price.toFixed(2)}</p>
                  </div>
                  {item.variant && (
                    <p className="mt-1 text-xs text-gray-500">
                      {item.variant.name || 'Variant'}
                    </p>
                  )}
                </div>
                <div className="flex-1 flex items-end justify-between text-xs">
                  <p className="text-gray-500">Qty {item.quantity}</p>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
      
      <div className="border-t border-gray-200 mt-6 pt-6">
        <div className="flow-root">
          <dl className="-my-4 text-sm divide-y divide-gray-200">
            <div className="py-4 flex items-center justify-between">
              <dt className="text-gray-600">Subtotal</dt>
              <dd className="font-medium text-gray-900">${cart.total_amount.toFixed(2)}</dd>
            </div>
            
            <div className="py-4 flex items-center justify-between">
              <dt className="text-gray-600">Shipping</dt>
              <dd className="font-medium text-gray-900">${shippingCost.toFixed(2)}</dd>
            </div>
            
            <div className="py-4 flex items-center justify-between">
              <dt className="text-gray-600">Tax (8%)</dt>
              <dd className="font-medium text-gray-900">${taxAmount.toFixed(2)}</dd>
            </div>
            
            <div className="py-4 flex items-center justify-between">
              <dt className="text-base font-medium text-gray-900">Order Total</dt>
              <dd className="text-base font-medium text-gray-900">${totalAmount.toFixed(2)}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
};

export default OrderSummary;
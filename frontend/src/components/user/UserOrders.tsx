import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { twMerge } from 'tailwind-merge';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import { Order } from '../../types';
import { formatPrice, formatDate } from '../../utils/formatters';

export interface UserOrdersProps {
  orders: Order[];
  isLoading?: boolean;
  className?: string;
}

const UserOrders: React.FC<UserOrdersProps> = ({
  orders,
  isLoading = false,
  className,
}) => {
  const [activeTab, setActiveTab] = useState<'all' | 'processing' | 'completed' | 'cancelled'>('all');

  // Filter orders based on active tab
  const filteredOrders = orders.filter(order => {
    if (activeTab === 'all') return true;
    if (activeTab === 'processing') return ['pending', 'processing', 'shipped'].includes(order.status);
    if (activeTab === 'completed') return order.status === 'delivered';
    if (activeTab === 'cancelled') return order.status === 'cancelled';
    return true;
  });

  // Get status badge variant and text
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return { variant: 'warning', text: 'Pending' };
      case 'processing':
        return { variant: 'info', text: 'Processing' };
      case 'shipped':
        return { variant: 'primary', text: 'Shipped' };
      case 'delivered':
        return { variant: 'success', text: 'Delivered' };
      case 'cancelled':
        return { variant: 'error', text: 'Cancelled' };
      default:
        return { variant: 'neutral', text: status };
    }
  };

  // Loading skeleton
  if (isLoading) {
    return (
      <Card 
        className={twMerge('w-full', className)}
        padding="lg"
        shadow="sm"
      >
        <div className="animate-pulse">
          <div className="h-8 bg-neutral-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[...Array(3)].map((_, index) => (
              <div key={index} className="border border-neutral-200 rounded-lg p-4">
                <div className="flex justify-between mb-4">
                  <div className="h-5 bg-neutral-200 rounded w-1/4"></div>
                  <div className="h-5 bg-neutral-200 rounded w-1/6"></div>
                </div>
                <div className="h-4 bg-neutral-200 rounded w-1/3 mb-2"></div>
                <div className="h-4 bg-neutral-200 rounded w-1/2 mb-4"></div>
                <div className="flex justify-between items-center">
                  <div className="h-6 bg-neutral-200 rounded w-1/5"></div>
                  <div className="h-8 bg-neutral-200 rounded w-1/6"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card 
      className={twMerge('w-full', className)}
      padding="lg"
      shadow="sm"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-neutral-900">Your Orders</h2>
      </div>

      {/* Tabs */}
      <div className="border-b border-neutral-200 mb-6">
        <nav className="flex space-x-8" aria-label="Order filters">
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'all'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300'
            }`}
            onClick={() => setActiveTab('all')}
          >
            All Orders
          </button>
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'processing'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300'
            }`}
            onClick={() => setActiveTab('processing')}
          >
            Processing
          </button>
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'completed'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300'
            }`}
            onClick={() => setActiveTab('completed')}
          >
            Completed
          </button>
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'cancelled'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300'
            }`}
            onClick={() => setActiveTab('cancelled')}
          >
            Cancelled
          </button>
        </nav>
      </div>

      {/* Orders list */}
      {filteredOrders.length === 0 ? (
        <div className="text-center py-8">
          <svg
            className="mx-auto h-12 w-12 text-neutral-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-neutral-900">No orders found</h3>
          <p className="mt-1 text-sm text-neutral-500">
            {activeTab === 'all'
              ? "You haven't placed any orders yet."
              : `You don't have any ${activeTab} orders.`}
          </p>
          <div className="mt-6">
            <Button
              as={Link}
              to="/products"
              variant="primary"
              size="md"
            >
              Start Shopping
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredOrders.map((order) => {
            const statusBadge = getStatusBadge(order.status);
            
            return (
              <div key={order.id} className="border border-neutral-200 rounded-lg overflow-hidden">
                <div className="bg-neutral-50 p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-neutral-200">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-neutral-700">Order #{order.order_number}</span>
                      <Badge variant={statusBadge.variant as any} size="sm" shape="pill">
                        {statusBadge.text}
                      </Badge>
                    </div>
                    <p className="text-xs text-neutral-500 mt-1">
                      Placed on {formatDate(order.created_at)}
                    </p>
                  </div>
                  <div className="mt-2 sm:mt-0 flex items-center space-x-2">
                    <span className="text-sm font-medium text-neutral-900">
                      {formatPrice(order.total_amount)}
                    </span>
                    <Button
                      as={Link}
                      to={`/account/orders/${order.id}`}
                      variant="outline"
                      size="sm"
                    >
                      View Details
                    </Button>
                  </div>
                </div>
                
                <div className="p-4">
                  <div className="space-y-3">
                    {order.items.slice(0, 2).map((item) => (
                      <div key={item.id} className="flex items-center space-x-3">
                        <div className="h-16 w-16 flex-shrink-0 overflow-hidden rounded-md border border-neutral-200">
                          {item.product.primary_image ? (
                            <img
                              src={item.product.primary_image.image_url}
                              alt={item.product.name}
                              className="h-full w-full object-cover object-center"
                            />
                          ) : (
                            <div className="h-full w-full bg-neutral-200 flex items-center justify-center">
                              <span className="text-neutral-500 text-xs">No image</span>
                            </div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-neutral-900 truncate">
                            {item.product.name}
                          </h4>
                          <p className="text-xs text-neutral-500">
                            Qty: {item.quantity} × {formatPrice(item.unit_price)}
                          </p>
                          {item.variant_options && (
                            <p className="text-xs text-neutral-500">
                              {Object.entries(item.variant_options)
                                .map(([key, value]) => `${key}: ${value}`)
                                .join(', ')}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                    
                    {order.items.length > 2 && (
                      <p className="text-xs text-neutral-500 italic">
                        + {order.items.length - 2} more items
                      </p>
                    )}
                  </div>
                  
                  {order.status === 'delivered' && (
                    <div className="mt-4 flex justify-end">
                      <Button
                        as={Link}
                        to={`/account/orders/${order.id}/review`}
                        variant="outline"
                        size="sm"
                      >
                        Write a Review
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
};

export default UserOrders;
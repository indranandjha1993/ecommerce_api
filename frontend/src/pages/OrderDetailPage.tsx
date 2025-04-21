import React, { useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useOrders } from '../hooks/useOrders';
import { formatPrice, formatDate } from '../utils/formatters';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';

const OrderDetailPage: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { fetchOrderById, currentOrder, loading, error } = useOrders();
  
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login?redirect=orders');
      return;
    }
    
    if (orderId) {
      fetchOrderById(orderId);
    }
  }, [isAuthenticated, navigate, orderId, fetchOrderById]);
  
  useEffect(() => {
    if (error) {
      navigate('/not-found', { replace: true });
    }
  }, [error, navigate]);
  
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="warning">Pending</Badge>;
      case 'processing':
        return <Badge variant="info">Processing</Badge>;
      case 'shipped':
        return <Badge variant="primary">Shipped</Badge>;
      case 'delivered':
        return <Badge variant="success">Delivered</Badge>;
      case 'cancelled':
        return <Badge variant="danger">Cancelled</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };
  
  if (!isAuthenticated) {
    return null; // Will redirect to login page
  }
  
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }
  
  if (!currentOrder) {
    return null; // Will redirect to not-found page due to the error effect
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Order #{currentOrder.order_number}
          </h1>
          <p className="text-gray-600 mt-1">
            Placed on {formatDate(currentOrder.created_at)}
          </p>
        </div>
        
        <div className="mt-4 md:mt-0">
          <Link to="/orders">
            <Button variant="outline">Back to Orders</Button>
          </Link>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {/* Order Items */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Order Items</h2>
            </div>
            
            <div className="divide-y divide-gray-200">
              {currentOrder.items.map((item) => (
                <div key={item.id} className="p-6 flex">
                  <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-md border border-gray-200">
                    {item.product.primary_image ? (
                      <img
                        src={item.product.primary_image.image_url}
                        alt={item.product.primary_image.alt_text || item.product.name}
                        className="h-full w-full object-cover object-center"
                      />
                    ) : (
                      <div className="h-full w-full bg-gray-200 flex items-center justify-center">
                        <span className="text-gray-500 text-xs">No image</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="ml-6 flex-1">
                    <div className="flex justify-between">
                      <div>
                        <h3 className="text-base font-medium text-gray-900">
                          <Link to={`/products/${item.product.slug}`} className="hover:text-blue-600">
                            {item.product.name}
                          </Link>
                        </h3>
                        
                        {item.variant && (
                          <p className="mt-1 text-sm text-gray-500">
                            {item.variant.name || 'Variant'}
                          </p>
                        )}
                        
                        <p className="mt-1 text-sm text-gray-500">
                          Quantity: {item.quantity}
                        </p>
                      </div>
                      
                      <p className="text-base font-medium text-gray-900">
                        {formatPrice(item.unit_price)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Order Timeline */}
          {currentOrder.status_history && currentOrder.status_history.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-8">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Order Timeline</h2>
              </div>
              
              <div className="p-6">
                <div className="flow-root">
                  <ul className="-mb-8">
                    {currentOrder.status_history.map((statusChange, index) => (
                      <li key={index}>
                        <div className="relative pb-8">
                          {index !== currentOrder.status_history.length - 1 ? (
                            <span
                              className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                              aria-hidden="true"
                            ></span>
                          ) : null}
                          <div className="relative flex space-x-3">
                            <div>
                              <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                                <svg
                                  className="h-5 w-5 text-white"
                                  xmlns="http://www.w3.org/2000/svg"
                                  viewBox="0 0 20 20"
                                  fill="currentColor"
                                  aria-hidden="true"
                                >
                                  <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clipRule="evenodd"
                                  />
                                </svg>
                              </span>
                            </div>
                            <div className="min-w-0 flex-1 pt-1.5">
                              <div>
                                <p className="text-sm font-medium text-gray-900">
                                  {getStatusBadge(statusChange.status)}
                                </p>
                                <p className="mt-1 text-sm text-gray-500">
                                  {formatDate(statusChange.timestamp)}
                                </p>
                              </div>
                              {statusChange.comment && (
                                <div className="mt-2 text-sm text-gray-700">
                                  <p>{statusChange.comment}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div>
          {/* Order Summary */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Order Summary</h2>
            </div>
            
            <div className="p-6">
              <div className="flex justify-between mb-2">
                <span className="text-gray-600">Status</span>
                <span>{getStatusBadge(currentOrder.status)}</span>
              </div>
              
              <div className="border-t border-gray-200 pt-4 mt-4">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="text-gray-900">{formatPrice(currentOrder.subtotal)}</span>
                </div>
                
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Shipping</span>
                  <span className="text-gray-900">{formatPrice(currentOrder.shipping_amount)}</span>
                </div>
                
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Tax</span>
                  <span className="text-gray-900">{formatPrice(currentOrder.tax_amount)}</span>
                </div>
                
                <div className="flex justify-between pt-4 border-t border-gray-200 font-medium">
                  <span className="text-gray-900">Total</span>
                  <span className="text-blue-600">{formatPrice(currentOrder.total_amount)}</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Shipping Information */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-8">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Shipping Information</h2>
            </div>
            
            <div className="p-6">
              {currentOrder.shipping_address ? (
                <div>
                  <p className="font-medium">{currentOrder.shipping_address.full_name}</p>
                  <p>{currentOrder.shipping_address.street_address}</p>
                  <p>
                    {currentOrder.shipping_address.city}, {currentOrder.shipping_address.state}{' '}
                    {currentOrder.shipping_address.postal_code}
                  </p>
                  <p>{currentOrder.shipping_address.country}</p>
                  <p className="mt-2">{currentOrder.shipping_address.phone_number}</p>
                </div>
              ) : (
                <p className="text-gray-500">No shipping information available</p>
              )}
              
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="font-medium">Shipping Method</p>
                <p className="text-gray-600">
                  {currentOrder.shipping_method === 'express'
                    ? 'Express Shipping (1-2 business days)'
                    : 'Standard Shipping (3-5 business days)'}
                </p>
              </div>
            </div>
          </div>
          
          {/* Payment Information */}
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Payment Information</h2>
            </div>
            
            <div className="p-6">
              <p className="font-medium">Payment Method</p>
              <p className="text-gray-600">
                {currentOrder.payment_method === 'credit_card'
                  ? 'Credit Card'
                  : currentOrder.payment_method === 'paypal'
                  ? 'PayPal'
                  : 'Cash on Delivery'}
              </p>
              
              {currentOrder.payment_status && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="font-medium">Payment Status</p>
                  <p className="text-gray-600">
                    {currentOrder.payment_status === 'paid' ? (
                      <span className="text-green-600">Paid</span>
                    ) : currentOrder.payment_status === 'pending' ? (
                      <span className="text-yellow-600">Pending</span>
                    ) : (
                      <span className="text-red-600">Failed</span>
                    )}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderDetailPage;
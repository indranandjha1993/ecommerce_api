import React, { useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useOrders } from '../hooks/useOrders';
import { formatPrice, formatDate } from '../utils/formatters';
import Button from '../components/ui/Button';

const OrderSuccessPage: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const { fetchOrderById, currentOrder, loading, error } = useOrders();
  
  useEffect(() => {
    if (orderId) {
      fetchOrderById(orderId);
    }
  }, [orderId, fetchOrderById]);
  
  useEffect(() => {
    if (error) {
      navigate('/not-found', { replace: true });
    }
  }, [error, navigate]);
  
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
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8 text-center">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6">
            <svg
              className="h-8 w-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Order Confirmed!</h1>
          
          <p className="text-lg text-gray-600 mb-8">
            Thank you for your purchase. Your order has been received and is being processed.
          </p>
          
          <div className="border border-gray-200 rounded-lg p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Order Number</h3>
                <p className="text-lg font-medium text-gray-900">{currentOrder.order_number}</p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Date</h3>
                <p className="text-lg font-medium text-gray-900">
                  {formatDate(currentOrder.created_at)}
                </p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Total Amount</h3>
                <p className="text-lg font-medium text-gray-900">
                  {formatPrice(currentOrder.total_amount)}
                </p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Payment Method</h3>
                <p className="text-lg font-medium text-gray-900">
                  {currentOrder.payment_method === 'credit_card'
                    ? 'Credit Card'
                    : currentOrder.payment_method === 'paypal'
                    ? 'PayPal'
                    : 'Cash on Delivery'}
                </p>
              </div>
            </div>
          </div>
          
          <div className="space-y-4 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Order Details</h2>
            
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Product
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Quantity
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Price
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {currentOrder.items.map((item) => (
                    <tr key={item.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 flex-shrink-0">
                            {item.product.primary_image ? (
                              <img
                                className="h-10 w-10 rounded object-cover"
                                src={item.product.primary_image.image_url}
                                alt={item.product.name}
                              />
                            ) : (
                              <div className="h-10 w-10 rounded bg-gray-200"></div>
                            )}
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {item.product.name}
                            </div>
                            {item.variant && (
                              <div className="text-sm text-gray-500">
                                {item.variant.name || 'Variant'}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                        {item.quantity}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                        {formatPrice(item.unit_price)}
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot className="bg-gray-50">
                  <tr>
                    <th
                      scope="row"
                      colSpan={2}
                      className="px-6 py-3 text-right text-sm font-medium text-gray-900"
                    >
                      Subtotal
                    </th>
                    <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                      {formatPrice(currentOrder.subtotal)}
                    </td>
                  </tr>
                  <tr>
                    <th
                      scope="row"
                      colSpan={2}
                      className="px-6 py-3 text-right text-sm font-medium text-gray-900"
                    >
                      Shipping
                    </th>
                    <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                      {formatPrice(currentOrder.shipping_amount)}
                    </td>
                  </tr>
                  <tr>
                    <th
                      scope="row"
                      colSpan={2}
                      className="px-6 py-3 text-right text-sm font-medium text-gray-900"
                    >
                      Tax
                    </th>
                    <td className="px-6 py-3 whitespace-nowrap text-right text-sm text-gray-900">
                      {formatPrice(currentOrder.tax_amount)}
                    </td>
                  </tr>
                  <tr>
                    <th
                      scope="row"
                      colSpan={2}
                      className="px-6 py-3 text-right text-sm font-medium text-gray-900"
                    >
                      Total
                    </th>
                    <td className="px-6 py-3 whitespace-nowrap text-right text-sm font-medium text-blue-600">
                      {formatPrice(currentOrder.total_amount)}
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <Link to="/orders">
              <Button variant="outline">View All Orders</Button>
            </Link>
            <Link to="/products">
              <Button variant="primary">Continue Shopping</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderSuccessPage;
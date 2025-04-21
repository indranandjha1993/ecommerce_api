import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useDispatch } from 'react-redux';
import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';
import { useCheckout } from '../hooks/useCheckout';
import { formatPrice } from '../utils/formatters';
import { checkoutSchema } from '../utils/validation';
import { addNotification } from '../store/slices/uiSlice';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';

type CheckoutFormValues = {
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  shipping_method: string;
  payment_method: string;
  card_number: string;
  card_expiry: string;
  card_cvc: string;
  save_payment_method: boolean;
};

const CheckoutPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { isAuthenticated, user } = useAuth();
  const { cart, fetchCart, loading: cartLoading } = useCart();
  const { createOrder, loading: orderLoading } = useCheckout();
  
  const [step, setStep] = useState(1);
  
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<CheckoutFormValues>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: {
      shipping_method: 'standard',
      payment_method: 'credit_card',
      save_payment_method: false,
    },
  });
  
  const shippingMethod = watch('shipping_method');
  const paymentMethod = watch('payment_method');
  
  useEffect(() => {
    fetchCart();
  }, [fetchCart]);
  
  useEffect(() => {
    // Pre-fill form with user data if authenticated
    if (isAuthenticated && user) {
      setValue('first_name', user.first_name || '');
      setValue('last_name', user.last_name || '');
      setValue('email', user.email || '');
      setValue('phone_number', user.phone_number || '');
      
      // If user has addresses, pre-fill with the default one
      if (user.addresses && user.addresses.length > 0) {
        const defaultAddress = user.addresses.find(addr => addr.is_default) || user.addresses[0];
        setValue('address_line1', defaultAddress.address_line1 || '');
        setValue('address_line2', defaultAddress.address_line2 || '');
        setValue('city', defaultAddress.city || '');
        setValue('state', defaultAddress.state || '');
        setValue('postal_code', defaultAddress.postal_code || '');
        setValue('country', defaultAddress.country || '');
      }
    }
  }, [isAuthenticated, user, setValue]);
  
  const onSubmit = async (data: CheckoutFormValues) => {
    if (!cart) {
      dispatch(
        addNotification({
          type: 'error',
          message: 'Your cart is empty. Please add items to your cart before checkout.',
        })
      );
      navigate('/cart');
      return;
    }
    
    try {
      const order = await createOrder({
        shipping_address: {
          first_name: data.first_name,
          last_name: data.last_name,
          address_line1: data.address_line1,
          address_line2: data.address_line2,
          city: data.city,
          state: data.state,
          postal_code: data.postal_code,
          country: data.country,
          phone_number: data.phone_number,
        },
        billing_address: {
          first_name: data.first_name,
          last_name: data.last_name,
          address_line1: data.address_line1,
          address_line2: data.address_line2,
          city: data.city,
          state: data.state,
          postal_code: data.postal_code,
          country: data.country,
          phone_number: data.phone_number,
        },
        shipping_method: data.shipping_method,
        payment_method: data.payment_method,
        payment_details: {
          card_number: data.card_number,
          card_expiry: data.card_expiry,
          card_cvc: data.card_cvc,
          save_payment_method: data.save_payment_method,
        },
        email: data.email,
      });
      
      if (order) {
        dispatch(
          addNotification({
            type: 'success',
            message: 'Your order has been placed successfully!',
          })
        );
        navigate(`/order-success/${order.id}`);
      }
    } catch (error) {
      dispatch(
        addNotification({
          type: 'error',
          message: 'Failed to place your order. Please try again.',
        })
      );
    }
  };
  
  if (cartLoading && !cart) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-2 space-y-4">
              <div className="h-12 bg-gray-200 rounded mb-4"></div>
              <div className="h-12 bg-gray-200 rounded mb-4"></div>
              <div className="h-12 bg-gray-200 rounded mb-4"></div>
            </div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }
  
  if (!cart || cart.items.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>
        <div className="bg-white p-8 rounded-lg shadow-sm text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
            />
          </svg>
          <h2 className="mt-2 text-lg font-medium text-gray-900">Your cart is empty</h2>
          <p className="mt-1 text-gray-500">
            You need to add items to your cart before proceeding to checkout.
          </p>
          <div className="mt-6">
            <Link to="/products">
              <Button variant="primary">Shop Now</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>
      
      {/* Checkout Steps */}
      <div className="mb-8">
        <div className="flex items-center">
          <div className={`flex items-center justify-center h-10 w-10 rounded-full ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'}`}>
            1
          </div>
          <div className={`flex-1 h-1 mx-2 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
          <div className={`flex items-center justify-center h-10 w-10 rounded-full ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'}`}>
            2
          </div>
          <div className={`flex-1 h-1 mx-2 ${step >= 3 ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
          <div className={`flex items-center justify-center h-10 w-10 rounded-full ${step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'}`}>
            3
          </div>
        </div>
        <div className="flex justify-between mt-2">
          <div className="text-center w-1/3">
            <span className={`text-sm font-medium ${step >= 1 ? 'text-blue-600' : 'text-gray-500'}`}>
              Shipping
            </span>
          </div>
          <div className="text-center w-1/3">
            <span className={`text-sm font-medium ${step >= 2 ? 'text-blue-600' : 'text-gray-500'}`}>
              Payment
            </span>
          </div>
          <div className="text-center w-1/3">
            <span className={`text-sm font-medium ${step >= 3 ? 'text-blue-600' : 'text-gray-500'}`}>
              Review
            </span>
          </div>
        </div>
      </div>
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Checkout Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              {/* Step 1: Shipping Information */}
              {step === 1 && (
                <div>
                  <div className="p-6 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Shipping Information</h2>
                  </div>
                  
                  <div className="p-6 space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <Input
                          label="First Name"
                          {...register('first_name')}
                          error={errors.first_name?.message}
                          fullWidth
                        />
                      </div>
                      <div>
                        <Input
                          label="Last Name"
                          {...register('last_name')}
                          error={errors.last_name?.message}
                          fullWidth
                        />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <Input
                          label="Email Address"
                          type="email"
                          {...register('email')}
                          error={errors.email?.message}
                          fullWidth
                        />
                      </div>
                      <div>
                        <Input
                          label="Phone Number"
                          {...register('phone_number')}
                          error={errors.phone_number?.message}
                          fullWidth
                        />
                      </div>
                    </div>
                    
                    <div>
                      <Input
                        label="Address Line 1"
                        {...register('address_line1')}
                        error={errors.address_line1?.message}
                        fullWidth
                      />
                    </div>
                    
                    <div>
                      <Input
                        label="Address Line 2 (Optional)"
                        {...register('address_line2')}
                        error={errors.address_line2?.message}
                        fullWidth
                      />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div>
                        <Input
                          label="City"
                          {...register('city')}
                          error={errors.city?.message}
                          fullWidth
                        />
                      </div>
                      <div>
                        <Input
                          label="State/Province"
                          {...register('state')}
                          error={errors.state?.message}
                          fullWidth
                        />
                      </div>
                      <div>
                        <Input
                          label="Postal Code"
                          {...register('postal_code')}
                          error={errors.postal_code?.message}
                          fullWidth
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Country
                      </label>
                      <select
                        {...register('country')}
                        className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${
                          errors.country ? 'border-red-500' : ''
                        }`}
                      >
                        <option value="">Select a country</option>
                        <option value="US">United States</option>
                        <option value="CA">Canada</option>
                        <option value="GB">United Kingdom</option>
                        <option value="AU">Australia</option>
                        <option value="DE">Germany</option>
                        <option value="FR">France</option>
                        <option value="JP">Japan</option>
                        <option value="IN">India</option>
                      </select>
                      {errors.country && (
                        <p className="mt-1 text-sm text-red-600">{errors.country.message}</p>
                      )}
                    </div>
                    
                    <div>
                      <h3 className="text-base font-medium text-gray-900 mb-3">Shipping Method</h3>
                      <div className="space-y-4">
                        <div className="flex items-center">
                          <input
                            id="shipping-standard"
                            type="radio"
                            value="standard"
                            {...register('shipping_method')}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                          />
                          <label htmlFor="shipping-standard" className="ml-3 block">
                            <span className="text-sm font-medium text-gray-900">Standard Shipping</span>
                            <span className="block text-sm text-gray-500">4-7 business days</span>
                            <span className="block text-sm font-medium text-gray-900">$5.99</span>
                          </label>
                        </div>
                        
                        <div className="flex items-center">
                          <input
                            id="shipping-express"
                            type="radio"
                            value="express"
                            {...register('shipping_method')}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                          />
                          <label htmlFor="shipping-express" className="ml-3 block">
                            <span className="text-sm font-medium text-gray-900">Express Shipping</span>
                            <span className="block text-sm text-gray-500">2-3 business days</span>
                            <span className="block text-sm font-medium text-gray-900">$12.99</span>
                          </label>
                        </div>
                        
                        <div className="flex items-center">
                          <input
                            id="shipping-overnight"
                            type="radio"
                            value="overnight"
                            {...register('shipping_method')}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                          />
                          <label htmlFor="shipping-overnight" className="ml-3 block">
                            <span className="text-sm font-medium text-gray-900">Overnight Shipping</span>
                            <span className="block text-sm text-gray-500">Next business day</span>
                            <span className="block text-sm font-medium text-gray-900">$24.99</span>
                          </label>
                        </div>
                      </div>
                      {errors.shipping_method && (
                        <p className="mt-1 text-sm text-red-600">{errors.shipping_method.message}</p>
                      )}
                    </div>
                  </div>
                  
                  <div className="p-6 border-t border-gray-200 flex justify-between">
                    <Link to="/cart">
                      <Button variant="outline">
                        Back to Cart
                      </Button>
                    </Link>
                    <Button
                      variant="primary"
                      onClick={() => setStep(2)}
                    >
                      Continue to Payment
                    </Button>
                  </div>
                </div>
              )}
              
              {/* Step 2: Payment Information */}
              {step === 2 && (
                <div>
                  <div className="p-6 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Payment Information</h2>
                  </div>
                  
                  <div className="p-6 space-y-6">
                    <div>
                      <h3 className="text-base font-medium text-gray-900 mb-3">Payment Method</h3>
                      <div className="space-y-4">
                        <div className="flex items-center">
                          <input
                            id="payment-credit-card"
                            type="radio"
                            value="credit_card"
                            {...register('payment_method')}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                          />
                          <label htmlFor="payment-credit-card" className="ml-3 block">
                            <span className="text-sm font-medium text-gray-900">Credit Card</span>
                            <span className="block text-sm text-gray-500">Visa, Mastercard, American Express</span>
                          </label>
                        </div>
                        
                        <div className="flex items-center">
                          <input
                            id="payment-paypal"
                            type="radio"
                            value="paypal"
                            {...register('payment_method')}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                          />
                          <label htmlFor="payment-paypal" className="ml-3 block">
                            <span className="text-sm font-medium text-gray-900">PayPal</span>
                            <span className="block text-sm text-gray-500">You will be redirected to PayPal</span>
                          </label>
                        </div>
                      </div>
                      {errors.payment_method && (
                        <p className="mt-1 text-sm text-red-600">{errors.payment_method.message}</p>
                      )}
                    </div>
                    
                    {paymentMethod === 'credit_card' && (
                      <div className="space-y-6">
                        <div>
                          <Input
                            label="Card Number"
                            placeholder="1234 5678 9012 3456"
                            {...register('card_number')}
                            error={errors.card_number?.message}
                            fullWidth
                          />
                        </div>
                        
                        <div className="grid grid-cols-2 gap-6">
                          <div>
                            <Input
                              label="Expiration Date"
                              placeholder="MM/YY"
                              {...register('card_expiry')}
                              error={errors.card_expiry?.message}
                              fullWidth
                            />
                          </div>
                          <div>
                            <Input
                              label="CVC"
                              placeholder="123"
                              {...register('card_cvc')}
                              error={errors.card_cvc?.message}
                              fullWidth
                            />
                          </div>
                        </div>
                        
                        <div className="flex items-center">
                          <input
                            id="save-payment-method"
                            type="checkbox"
                            {...register('save_payment_method')}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                          <label htmlFor="save-payment-method" className="ml-2 block text-sm text-gray-900">
                            Save this payment method for future purchases
                          </label>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="p-6 border-t border-gray-200 flex justify-between">
                    <Button
                      variant="outline"
                      onClick={() => setStep(1)}
                    >
                      Back to Shipping
                    </Button>
                    <Button
                      variant="primary"
                      onClick={() => setStep(3)}
                    >
                      Review Order
                    </Button>
                  </div>
                </div>
              )}
              
              {/* Step 3: Review Order */}
              {step === 3 && (
                <div>
                  <div className="p-6 border-b border-gray-200">
                    <h2 className="text-lg font-medium text-gray-900">Review Your Order</h2>
                  </div>
                  
                  <div className="p-6 space-y-6">
                    {/* Shipping Information */}
                    <div>
                      <h3 className="text-base font-medium text-gray-900 mb-3">Shipping Information</h3>
                      <div className="bg-gray-50 p-4 rounded-md">
                        <p className="text-sm text-gray-700">
                          {watch('first_name')} {watch('last_name')}
                        </p>
                        <p className="text-sm text-gray-700">{watch('address_line1')}</p>
                        {watch('address_line2') && (
                          <p className="text-sm text-gray-700">{watch('address_line2')}</p>
                        )}
                        <p className="text-sm text-gray-700">
                          {watch('city')}, {watch('state')} {watch('postal_code')}
                        </p>
                        <p className="text-sm text-gray-700">{watch('country')}</p>
                        <p className="text-sm text-gray-700">{watch('phone_number')}</p>
                        <p className="text-sm text-gray-700">{watch('email')}</p>
                      </div>
                      <button
                        type="button"
                        className="mt-2 text-sm text-blue-600 hover:text-blue-500"
                        onClick={() => setStep(1)}
                      >
                        Edit
                      </button>
                    </div>
                    
                    {/* Shipping Method */}
                    <div>
                      <h3 className="text-base font-medium text-gray-900 mb-3">Shipping Method</h3>
                      <div className="bg-gray-50 p-4 rounded-md">
                        <p className="text-sm text-gray-700">
                          {shippingMethod === 'standard' && 'Standard Shipping (4-7 business days)'}
                          {shippingMethod === 'express' && 'Express Shipping (2-3 business days)'}
                          {shippingMethod === 'overnight' && 'Overnight Shipping (Next business day)'}
                        </p>
                      </div>
                      <button
                        type="button"
                        className="mt-2 text-sm text-blue-600 hover:text-blue-500"
                        onClick={() => setStep(1)}
                      >
                        Edit
                      </button>
                    </div>
                    
                    {/* Payment Method */}
                    <div>
                      <h3 className="text-base font-medium text-gray-900 mb-3">Payment Method</h3>
                      <div className="bg-gray-50 p-4 rounded-md">
                        {paymentMethod === 'credit_card' && (
                          <p className="text-sm text-gray-700">
                            Credit Card ending in {watch('card_number').slice(-4)}
                          </p>
                        )}
                        {paymentMethod === 'paypal' && (
                          <p className="text-sm text-gray-700">PayPal</p>
                        )}
                      </div>
                      <button
                        type="button"
                        className="mt-2 text-sm text-blue-600 hover:text-blue-500"
                        onClick={() => setStep(2)}
                      >
                        Edit
                      </button>
                    </div>
                    
                    {/* Order Items */}
                    <div>
                      <h3 className="text-base font-medium text-gray-900 mb-3">Order Items</h3>
                      <div className="bg-gray-50 p-4 rounded-md space-y-4">
                        {cart.items.map((item) => (
                          <div key={item.id} className="flex items-center">
                            <div className="h-16 w-16 flex-shrink-0 overflow-hidden rounded-md border border-gray-200">
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
                            <div className="ml-4 flex-1">
                              <h4 className="text-sm font-medium text-gray-900">{item.product.name}</h4>
                              {item.variant && (
                                <p className="mt-1 text-sm text-gray-500">
                                  {item.variant.name || 'Variant'}
                                </p>
                              )}
                              <div className="flex justify-between mt-1">
                                <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                                <p className="text-sm font-medium text-gray-900">
                                  {formatPrice(item.unit_price * item.quantity)}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      <Link
                        to="/cart"
                        className="mt-2 text-sm text-blue-600 hover:text-blue-500"
                      >
                        Edit
                      </Link>
                    </div>
                  </div>
                  
                  <div className="p-6 border-t border-gray-200 flex justify-between">
                    <Button
                      variant="outline"
                      onClick={() => setStep(2)}
                    >
                      Back to Payment
                    </Button>
                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={orderLoading}
                    >
                      Place Order
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm overflow-hidden sticky top-24">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Order Summary</h2>
              </div>
              
              <div className="p-6 space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal ({cart.items.length} items)</span>
                  <span className="text-gray-900 font-medium">{formatPrice(cart.subtotal_amount)}</span>
                </div>
                
                {cart.discount_amount > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Discount</span>
                    <span className="text-green-600 font-medium">-{formatPrice(cart.discount_amount)}</span>
                  </div>
                )}
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Shipping</span>
                  <span className="text-gray-900 font-medium">
                    {shippingMethod === 'standard' && formatPrice(5.99)}
                    {shippingMethod === 'express' && formatPrice(12.99)}
                    {shippingMethod === 'overnight' && formatPrice(24.99)}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax</span>
                  <span className="text-gray-900 font-medium">{formatPrice(cart.tax_amount)}</span>
                </div>
                
                <div className="border-t border-gray-200 pt-4 flex justify-between">
                  <span className="text-lg font-medium text-gray-900">Total</span>
                  <span className="text-lg font-bold text-gray-900">
                    {formatPrice(
                      cart.total_amount +
                        (shippingMethod === 'standard'
                          ? 5.99
                          : shippingMethod === 'express'
                          ? 12.99
                          : 24.99)
                    )}
                  </span>
                </div>
                
                {/* Promo Code */}
                <div className="mt-6">
                  <label htmlFor="promo-code" className="block text-sm font-medium text-gray-700 mb-1">
                    Promo Code
                  </label>
                  <div className="flex">
                    <input
                      type="text"
                      id="promo-code"
                      className="flex-1 min-w-0 block w-full px-3 py-2 rounded-l-md border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="Enter code"
                    />
                    <button
                      type="button"
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-r-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Apply
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
};

export default CheckoutPage;
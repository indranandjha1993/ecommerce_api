import React from 'react';

interface PaymentMethodSelectorProps {
  selectedMethod: string;
  onSelect: (method: string) => void;
}

const PaymentMethodSelector: React.FC<PaymentMethodSelectorProps> = ({
  selectedMethod,
  onSelect,
}) => {
  const paymentMethods = [
    {
      id: 'credit_card',
      name: 'Credit Card',
      description: 'Pay with Visa, Mastercard, American Express, or Discover',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      ),
    },
    {
      id: 'paypal',
      name: 'PayPal',
      description: 'Pay with your PayPal account',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2z" />
        </svg>
      ),
    },
    {
      id: 'bank_transfer',
      name: 'Bank Transfer',
      description: 'Pay directly from your bank account',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z" />
        </svg>
      ),
    },
    {
      id: 'cash_on_delivery',
      name: 'Cash on Delivery',
      description: 'Pay when you receive your order',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2z" />
        </svg>
      ),
    },
  ];

  return (
    <div>
      <h3 className="text-lg font-medium text-gray-900 mb-4">Payment Method</h3>
      <div className="space-y-4">
        {paymentMethods.map((method) => (
          <div
            key={method.id}
            className={`border rounded-lg p-4 cursor-pointer transition-colors ${
              selectedMethod === method.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-blue-300'
            }`}
            onClick={() => onSelect(method.id)}
          >
            <div className="flex items-center">
              <div className="flex-shrink-0 mr-4 text-gray-500">
                {method.icon}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="text-base font-medium text-gray-900">{method.name}</h4>
                  <div className="ml-2">
                    <div
                      className={`w-5 h-5 rounded-full border flex items-center justify-center ${
                        selectedMethod === method.id
                          ? 'border-blue-500'
                          : 'border-gray-300'
                      }`}
                    >
                      {selectedMethod === method.id && (
                        <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                      )}
                    </div>
                  </div>
                </div>
                <p className="text-sm text-gray-500 mt-1">{method.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PaymentMethodSelector;
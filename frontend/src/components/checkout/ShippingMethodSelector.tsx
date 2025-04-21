import React from 'react';

interface ShippingMethodSelectorProps {
  selectedMethod: string;
  onSelect: (method: string) => void;
}

const ShippingMethodSelector: React.FC<ShippingMethodSelectorProps> = ({
  selectedMethod,
  onSelect,
}) => {
  const shippingMethods = [
    {
      id: 'standard',
      name: 'Standard Shipping',
      description: 'Delivery in 3-5 business days',
      price: 5.99,
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0" />
        </svg>
      ),
    },
    {
      id: 'express',
      name: 'Express Shipping',
      description: 'Delivery in 1-2 business days',
      price: 12.99,
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
    },
    {
      id: 'overnight',
      name: 'Overnight Shipping',
      description: 'Delivery next business day',
      price: 19.99,
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
  ];

  return (
    <div>
      <h3 className="text-lg font-medium text-gray-900 mb-4">Shipping Method</h3>
      <div className="space-y-4">
        {shippingMethods.map((method) => (
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
                  <div className="flex items-center">
                    <span className="text-base font-medium text-gray-900 mr-3">
                      ${method.price.toFixed(2)}
                    </span>
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

export default ShippingMethodSelector;
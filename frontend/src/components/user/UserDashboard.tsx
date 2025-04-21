import React, { useState } from 'react';
import { twMerge } from 'tailwind-merge';
import UserProfile from './UserProfile';
import UserAddresses from './UserAddresses';
import UserOrders from './UserOrders';
import UserWishlist from './UserWishlist';
import Card from '../ui/Card';
import { User, Address, Order, Product } from '../../types';

export interface UserDashboardProps {
  user: User;
  addresses: Address[];
  orders: Order[];
  wishlist: Product[];
  onUpdateProfile: (data: Partial<User>) => Promise<void>;
  onAddAddress: (address: Omit<Address, 'id'>) => Promise<void>;
  onUpdateAddress: (id: string, address: Partial<Address>) => Promise<void>;
  onDeleteAddress: (id: string) => Promise<void>;
  onSetDefaultAddress: (id: string) => Promise<void>;
  onRemoveFromWishlist: (productId: string) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

type DashboardTab = 'profile' | 'orders' | 'addresses' | 'wishlist';

const UserDashboard: React.FC<UserDashboardProps> = ({
  user,
  addresses,
  orders,
  wishlist,
  onUpdateProfile,
  onAddAddress,
  onUpdateAddress,
  onDeleteAddress,
  onSetDefaultAddress,
  onRemoveFromWishlist,
  isLoading = false,
  error = null,
  className,
}) => {
  const [activeTab, setActiveTab] = useState<DashboardTab>('profile');

  // Tab navigation items
  const tabs = [
    { id: 'profile', label: 'Profile', icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
      </svg>
    )},
    { id: 'orders', label: 'Orders', icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M10 2a4 4 0 00-4 4v1H5a1 1 0 00-.994.89l-1 9A1 1 0 004 18h12a1 1 0 00.994-1.11l-1-9A1 1 0 0015 7h-1V6a4 4 0 00-4-4zm2 5V6a2 2 0 10-4 0v1h4zm-6 3a1 1 0 112 0 1 1 0 01-2 0zm7-1a1 1 0 100 2 1 1 0 000-2z" clipRule="evenodd" />
      </svg>
    )},
    { id: 'addresses', label: 'Addresses', icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
      </svg>
    )},
    { id: 'wishlist', label: 'Wishlist', icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
      </svg>
    )},
  ];

  // Render active tab content
  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return (
          <UserProfile
            user={user}
            onUpdateProfile={onUpdateProfile}
            isLoading={isLoading}
            error={error}
          />
        );
      case 'orders':
        return (
          <UserOrders
            orders={orders}
            isLoading={isLoading}
          />
        );
      case 'addresses':
        return (
          <UserAddresses
            addresses={addresses}
            onAddAddress={onAddAddress}
            onUpdateAddress={onUpdateAddress}
            onDeleteAddress={onDeleteAddress}
            onSetDefaultAddress={onSetDefaultAddress}
            isLoading={isLoading}
            error={error}
          />
        );
      case 'wishlist':
        return (
          <UserWishlist
            products={wishlist}
            onRemoveFromWishlist={onRemoveFromWishlist}
            isLoading={isLoading}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className={twMerge('flex flex-col md:flex-row gap-6', className)}>
      {/* Sidebar navigation */}
      <div className="w-full md:w-64 flex-shrink-0">
        <Card padding="md" shadow="sm">
          <div className="flex flex-col space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  activeTab === tab.id
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-neutral-700 hover:bg-neutral-100'
                }`}
                onClick={() => setActiveTab(tab.id as DashboardTab)}
              >
                <span className={activeTab === tab.id ? 'text-primary-600' : 'text-neutral-500'}>
                  {tab.icon}
                </span>
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </div>
        </Card>
      </div>

      {/* Main content */}
      <div className="flex-1">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default UserDashboard;
import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import UserDashboard from '../../components/user/UserDashboard';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../utils/api';
import { Address, Order, Product } from '../../types';

const AccountPage: React.FC = () => {
  const { user, isAuthenticated, isLoading: authLoading, updateProfile } = useAuth();
  
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [wishlist, setWishlist] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Redirect if not authenticated
  if (!isAuthenticated && !authLoading) {
    return <Navigate to="/login" replace />;
  }

  // Fetch user data
  useEffect(() => {
    const fetchUserData = async () => {
      if (!isAuthenticated) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        // Fetch addresses
        const addressesResponse = await apiService.addresses.getAll();
        setAddresses(addressesResponse.data);
        
        // Fetch orders
        const ordersResponse = await apiService.orders.getAll();
        setOrders(ordersResponse.data);
        
        // Fetch wishlist
        const wishlistResponse = await apiService.wishlist.get();
        setWishlist(wishlistResponse.data);
      } catch (err: any) {
        console.error('Failed to fetch user data:', err);
        setError('Failed to load your account data. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchUserData();
  }, [isAuthenticated]);

  // Handle address operations
  const handleAddAddress = async (address: Omit<Address, 'id'>) => {
    try {
      await apiService.addresses.create(address);
      const response = await apiService.addresses.getAll();
      setAddresses(response.data);
    } catch (err: any) {
      console.error('Failed to add address:', err);
      throw err;
    }
  };

  const handleUpdateAddress = async (id: string, address: Partial<Address>) => {
    try {
      await apiService.addresses.update(id, address);
      const response = await apiService.addresses.getAll();
      setAddresses(response.data);
    } catch (err: any) {
      console.error('Failed to update address:', err);
      throw err;
    }
  };

  const handleDeleteAddress = async (id: string) => {
    try {
      await apiService.addresses.delete(id);
      const response = await apiService.addresses.getAll();
      setAddresses(response.data);
    } catch (err: any) {
      console.error('Failed to delete address:', err);
      throw err;
    }
  };

  const handleSetDefaultAddress = async (id: string) => {
    try {
      await apiService.addresses.setDefault(id);
      const response = await apiService.addresses.getAll();
      setAddresses(response.data);
    } catch (err: any) {
      console.error('Failed to set default address:', err);
      throw err;
    }
  };

  // Handle wishlist operations
  const handleRemoveFromWishlist = async (productId: string) => {
    try {
      await apiService.wishlist.removeItem(productId);
      const response = await apiService.wishlist.get();
      setWishlist(response.data);
    } catch (err: any) {
      console.error('Failed to remove from wishlist:', err);
      throw err;
    }
  };

  if (authLoading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-neutral-900 mb-6">My Account</h1>
      
      <UserDashboard
        user={user}
        addresses={addresses}
        orders={orders}
        wishlist={wishlist}
        onUpdateProfile={updateProfile}
        onAddAddress={handleAddAddress}
        onUpdateAddress={handleUpdateAddress}
        onDeleteAddress={handleDeleteAddress}
        onSetDefaultAddress={handleSetDefaultAddress}
        onRemoveFromWishlist={handleRemoveFromWishlist}
        isLoading={isLoading}
        error={error}
      />
    </div>
  );
};

export default AccountPage;
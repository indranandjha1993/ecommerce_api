import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Address } from '../../types';
import { useAddresses } from '../../hooks/useAddresses';
import { addNotification } from '../../store/slices/uiSlice';
import Button from '../ui/Button';
import Badge from '../ui/Badge';

interface AddressListProps {
  addresses: Address[];
  onEdit: (addressId: string) => void;
  onRefresh: () => void;
}

const AddressList: React.FC<AddressListProps> = ({
  addresses,
  onEdit,
  onRefresh,
}) => {
  const dispatch = useDispatch();
  const { setDefaultAddress, deleteAddress, loading } = useAddresses();
  const [processingId, setProcessingId] = useState<string | null>(null);
  
  const handleSetDefault = async (addressId: string) => {
    try {
      setProcessingId(addressId);
      const success = await setDefaultAddress(addressId);
      
      if (success) {
        dispatch(
          addNotification({
            type: 'success',
            message: 'Default address updated successfully!',
          })
        );
        onRefresh();
      } else {
        dispatch(
          addNotification({
            type: 'error',
            message: 'Failed to update default address. Please try again.',
          })
        );
      }
    } catch (error) {
      dispatch(
        addNotification({
          type: 'error',
          message: 'Failed to update default address. Please try again.',
        })
      );
    } finally {
      setProcessingId(null);
    }
  };
  
  const handleDelete = async (addressId: string) => {
    if (!window.confirm('Are you sure you want to delete this address?')) {
      return;
    }
    
    try {
      setProcessingId(addressId);
      const success = await deleteAddress(addressId);
      
      if (success) {
        dispatch(
          addNotification({
            type: 'success',
            message: 'Address deleted successfully!',
          })
        );
        onRefresh();
      } else {
        dispatch(
          addNotification({
            type: 'error',
            message: 'Failed to delete address. Please try again.',
          })
        );
      }
    } catch (error) {
      dispatch(
        addNotification({
          type: 'error',
          message: 'Failed to delete address. Please try again.',
        })
      );
    } finally {
      setProcessingId(null);
    }
  };
  
  if (addresses.length === 0) {
    return (
      <div className="text-center py-8">
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
            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No addresses</h3>
        <p className="mt-1 text-sm text-gray-500">
          You haven't added any addresses yet.
        </p>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {addresses.map((address) => (
        <div
          key={address.id}
          className="border border-gray-200 rounded-lg p-4 relative"
        >
          {address.is_default && (
            <div className="absolute top-4 right-4">
              <Badge variant="primary">Default</Badge>
            </div>
          )}
          
          <div className="mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              {address.full_name}
            </h3>
            <p className="text-gray-600 mt-1">
              {address.street_address}
              {address.apartment && `, ${address.apartment}`}
              <br />
              {address.city}, {address.state} {address.postal_code}
              <br />
              {address.country}
            </p>
            {address.phone && (
              <p className="text-gray-600 mt-1">{address.phone}</p>
            )}
          </div>
          
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onEdit(address.id)}
            >
              Edit
            </Button>
            
            {!address.is_default && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSetDefault(address.id)}
                isLoading={loading && processingId === address.id}
                disabled={loading && processingId === address.id}
              >
                Set as Default
              </Button>
            )}
            
            <Button
              variant="danger"
              size="sm"
              onClick={() => handleDelete(address.id)}
              isLoading={loading && processingId === address.id}
              disabled={loading && processingId === address.id}
            >
              Delete
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AddressList;
import React, { useState } from 'react';
import { twMerge } from 'tailwind-merge';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Input from '../ui/Input';
import Alert from '../ui/Alert';
import { Address } from '../../types';

export interface UserAddressesProps {
  addresses: Address[];
  onAddAddress: (address: Omit<Address, 'id'>) => Promise<void>;
  onUpdateAddress: (id: string, address: Partial<Address>) => Promise<void>;
  onDeleteAddress: (id: string) => Promise<void>;
  onSetDefaultAddress: (id: string) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

const UserAddresses: React.FC<UserAddressesProps> = ({
  addresses,
  onAddAddress,
  onUpdateAddress,
  onDeleteAddress,
  onSetDefaultAddress,
  isLoading = false,
  error = null,
  className,
}) => {
  const [isAddingAddress, setIsAddingAddress] = useState(false);
  const [editingAddressId, setEditingAddressId] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // New address form state
  const [formData, setFormData] = useState<Omit<Address, 'id'>>({
    name: '',
    street_address: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    phone: '',
    is_default: false,
  });

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  // Handle form submission for new address
  const handleAddAddress = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSuccess(null);

    try {
      await onAddAddress(formData);
      setSuccess('Address added successfully');
      setIsAddingAddress(false);
      setFormData({
        name: '',
        street_address: '',
        city: '',
        state: '',
        postal_code: '',
        country: '',
        phone: '',
        is_default: false,
      });
    } catch (err) {
      setFormError('Failed to add address');
      console.error('Add address error:', err);
    }
  };

  // Handle form submission for updating address
  const handleUpdateAddress = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSuccess(null);

    if (!editingAddressId) return;

    try {
      await onUpdateAddress(editingAddressId, formData);
      setSuccess('Address updated successfully');
      setEditingAddressId(null);
    } catch (err) {
      setFormError('Failed to update address');
      console.error('Update address error:', err);
    }
  };

  // Start editing an address
  const handleEditAddress = (address: Address) => {
    setEditingAddressId(address.id);
    setFormData({
      name: address.name,
      street_address: address.street_address,
      city: address.city,
      state: address.state,
      postal_code: address.postal_code,
      country: address.country,
      phone: address.phone || '',
      is_default: address.is_default,
    });
  };

  // Cancel editing or adding
  const handleCancel = () => {
    setIsAddingAddress(false);
    setEditingAddressId(null);
    setFormError(null);
    setFormData({
      name: '',
      street_address: '',
      city: '',
      state: '',
      postal_code: '',
      country: '',
      phone: '',
      is_default: false,
    });
  };

  // Delete address with confirmation
  const handleDeleteAddress = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this address?')) {
      try {
        await onDeleteAddress(id);
        setSuccess('Address deleted successfully');
      } catch (err) {
        setFormError('Failed to delete address');
        console.error('Delete address error:', err);
      }
    }
  };

  // Set address as default
  const handleSetDefaultAddress = async (id: string) => {
    try {
      await onSetDefaultAddress(id);
      setSuccess('Default address updated');
    } catch (err) {
      setFormError('Failed to update default address');
      console.error('Set default address error:', err);
    }
  };

  // Address form component
  const AddressForm = ({ onSubmit }: { onSubmit: (e: React.FormEvent) => Promise<void> }) => (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Full Name"
          id="name"
          name="name"
          type="text"
          value={formData.name}
          onChange={handleInputChange}
          disabled={isLoading}
          required
        />

        <Input
          label="Phone Number"
          id="phone"
          name="phone"
          type="tel"
          value={formData.phone}
          onChange={handleInputChange}
          disabled={isLoading}
        />
      </div>

      <Input
        label="Street Address"
        id="street_address"
        name="street_address"
        type="text"
        value={formData.street_address}
        onChange={handleInputChange}
        disabled={isLoading}
        required
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input
          label="City"
          id="city"
          name="city"
          type="text"
          value={formData.city}
          onChange={handleInputChange}
          disabled={isLoading}
          required
        />

        <Input
          label="State/Province"
          id="state"
          name="state"
          type="text"
          value={formData.state}
          onChange={handleInputChange}
          disabled={isLoading}
          required
        />

        <Input
          label="Postal Code"
          id="postal_code"
          name="postal_code"
          type="text"
          value={formData.postal_code}
          onChange={handleInputChange}
          disabled={isLoading}
          required
        />
      </div>

      <Input
        label="Country"
        id="country"
        name="country"
        type="text"
        value={formData.country}
        onChange={handleInputChange}
        disabled={isLoading}
        required
      />

      <div className="flex items-center">
        <input
          id="is_default"
          name="is_default"
          type="checkbox"
          checked={formData.is_default}
          onChange={handleInputChange}
          disabled={isLoading}
          className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-neutral-300 rounded"
        />
        <label htmlFor="is_default" className="ml-2 block text-sm text-neutral-700">
          Set as default address
        </label>
      </div>

      <div className="flex justify-end space-x-3 pt-2">
        <Button
          type="button"
          variant="outline"
          size="md"
          onClick={handleCancel}
          disabled={isLoading}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          variant="primary"
          size="md"
          isLoading={isLoading}
          loadingText="Saving..."
        >
          {editingAddressId ? 'Update Address' : 'Add Address'}
        </Button>
      </div>
    </form>
  );

  // Address card component
  const AddressCard = ({ address }: { address: Address }) => (
    <div className={`border rounded-lg p-4 ${address.is_default ? 'border-primary-500 bg-primary-50' : 'border-neutral-200'}`}>
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-medium text-neutral-900">{address.name}</h3>
          {address.is_default && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary-100 text-primary-800">
              Default
            </span>
          )}
        </div>
        <div className="flex space-x-2">
          <button
            type="button"
            onClick={() => handleEditAddress(address)}
            className="text-neutral-500 hover:text-neutral-700"
            disabled={isLoading}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
            </svg>
          </button>
          <button
            type="button"
            onClick={() => handleDeleteAddress(address.id)}
            className="text-neutral-500 hover:text-red-600"
            disabled={isLoading}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
      <div className="text-sm text-neutral-700 space-y-1">
        <p>{address.street_address}</p>
        <p>
          {address.city}, {address.state} {address.postal_code}
        </p>
        <p>{address.country}</p>
        {address.phone && <p>Phone: {address.phone}</p>}
      </div>
      {!address.is_default && (
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleSetDefaultAddress(address.id)}
          className="mt-3"
          disabled={isLoading}
        >
          Set as Default
        </Button>
      )}
    </div>
  );

  return (
    <Card 
      className={twMerge('w-full', className)}
      padding="lg"
      shadow="sm"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-neutral-900">Your Addresses</h2>
        {!isAddingAddress && !editingAddressId && (
          <Button
            variant="primary"
            size="sm"
            onClick={() => setIsAddingAddress(true)}
            leftIcon={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
            }
          >
            Add New Address
          </Button>
        )}
      </div>

      {(error || formError) && (
        <Alert 
          variant="error" 
          title="Error" 
          className="mb-4"
          onClose={() => setFormError(null)}
        >
          {error || formError}
        </Alert>
      )}

      {success && (
        <Alert 
          variant="success" 
          title="Success" 
          className="mb-4"
          onClose={() => setSuccess(null)}
        >
          {success}
        </Alert>
      )}

      {isAddingAddress && (
        <div className="mb-6 border border-neutral-200 rounded-lg p-4 bg-neutral-50">
          <h3 className="text-lg font-medium text-neutral-900 mb-4">Add New Address</h3>
          <AddressForm onSubmit={handleAddAddress} />
        </div>
      )}

      {editingAddressId && (
        <div className="mb-6 border border-neutral-200 rounded-lg p-4 bg-neutral-50">
          <h3 className="text-lg font-medium text-neutral-900 mb-4">Edit Address</h3>
          <AddressForm onSubmit={handleUpdateAddress} />
        </div>
      )}

      {addresses.length === 0 && !isAddingAddress ? (
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
              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-neutral-900">No addresses</h3>
          <p className="mt-1 text-sm text-neutral-500">Get started by adding a new address.</p>
          <div className="mt-6">
            <Button
              variant="primary"
              size="md"
              onClick={() => setIsAddingAddress(true)}
            >
              Add Address
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {addresses.map((address) => (
            <AddressCard key={address.id} address={address} />
          ))}
        </div>
      )}
    </Card>
  );
};

export default UserAddresses;
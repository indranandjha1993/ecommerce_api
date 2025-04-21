import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { useAddresses } from '../../hooks/useAddresses';
import { addNotification } from '../../store/slices/uiSlice';
import Button from '../ui/Button';
import Input from '../ui/Input';

interface AddressFormProps {
  addressId?: string | null;
  onSuccess: () => void;
}

const AddressForm: React.FC<AddressFormProps> = ({ addressId, onSuccess }) => {
  const dispatch = useDispatch();
  const { getAddress, addAddress, updateAddress, loading } = useAddresses();
  
  const [formData, setFormData] = useState({
    full_name: '',
    street_address: '',
    apartment: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
    phone: '',
    is_default: false,
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  
  // Fetch address data if editing
  useEffect(() => {
    const fetchAddress = async () => {
      if (!addressId) return;
      
      try {
        setIsLoading(true);
        const address = await getAddress(addressId);
        if (address) {
          setFormData({
            full_name: address.full_name || '',
            street_address: address.street_address || '',
            apartment: address.apartment || '',
            city: address.city || '',
            state: address.state || '',
            postal_code: address.postal_code || '',
            country: address.country || '',
            phone: address.phone || '',
            is_default: address.is_default || false,
          });
        }
      } catch (error) {
        console.error('Error fetching address:', error);
        dispatch(
          addNotification({
            type: 'error',
            message: 'Failed to load address data. Please try again.',
          })
        );
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchAddress();
  }, [addressId, getAddress, dispatch]);
  
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target as HTMLInputElement;
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;
    
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    
    // Clear error when field is edited
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };
  
  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required';
    }
    
    if (!formData.street_address.trim()) {
      newErrors.street_address = 'Street address is required';
    }
    
    if (!formData.city.trim()) {
      newErrors.city = 'City is required';
    }
    
    if (!formData.state.trim()) {
      newErrors.state = 'State/Province is required';
    }
    
    if (!formData.postal_code.trim()) {
      newErrors.postal_code = 'Postal code is required';
    }
    
    if (!formData.country.trim()) {
      newErrors.country = 'Country is required';
    }
    
    if (formData.phone && !/^\+?[0-9]{10,15}$/.test(formData.phone.replace(/\s+/g, ''))) {
      newErrors.phone = 'Phone number is invalid';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      setIsLoading(true);
      let success;
      
      if (addressId) {
        success = await updateAddress(addressId, formData);
      } else {
        success = await addAddress(formData);
      }
      
      if (success) {
        dispatch(
          addNotification({
            type: 'success',
            message: addressId
              ? 'Address updated successfully!'
              : 'Address added successfully!',
          })
        );
        onSuccess();
      } else {
        dispatch(
          addNotification({
            type: 'error',
            message: 'Failed to save address. Please try again.',
          })
        );
      }
    } catch (error) {
      dispatch(
        addNotification({
          type: 'error',
          message: 'Failed to save address. Please try again.',
        })
      );
    } finally {
      setIsLoading(false);
    }
  };
  
  if (isLoading && addressId) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 rounded-full border-t-transparent"></div>
      </div>
    );
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="Full Name"
          name="full_name"
          value={formData.full_name}
          onChange={handleChange}
          error={errors.full_name}
          required
          className="md:col-span-2"
        />
        
        <Input
          label="Street Address"
          name="street_address"
          value={formData.street_address}
          onChange={handleChange}
          error={errors.street_address}
          required
          className="md:col-span-2"
        />
        
        <Input
          label="Apartment, Suite, etc. (optional)"
          name="apartment"
          value={formData.apartment}
          onChange={handleChange}
          error={errors.apartment}
          className="md:col-span-2"
        />
        
        <Input
          label="City"
          name="city"
          value={formData.city}
          onChange={handleChange}
          error={errors.city}
          required
        />
        
        <Input
          label="State / Province"
          name="state"
          value={formData.state}
          onChange={handleChange}
          error={errors.state}
          required
        />
        
        <Input
          label="Postal Code"
          name="postal_code"
          value={formData.postal_code}
          onChange={handleChange}
          error={errors.postal_code}
          required
        />
        
        <Input
          label="Country"
          name="country"
          value={formData.country}
          onChange={handleChange}
          error={errors.country}
          required
        />
        
        <Input
          label="Phone Number (optional)"
          name="phone"
          type="tel"
          value={formData.phone}
          onChange={handleChange}
          error={errors.phone}
          placeholder="+1 (555) 123-4567"
          className="md:col-span-2"
        />
        
        <div className="md:col-span-2">
          <div className="flex items-center">
            <input
              id="is_default"
              name="is_default"
              type="checkbox"
              checked={formData.is_default}
              onChange={handleChange}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="is_default" className="ml-2 block text-sm text-gray-900">
              Set as default address
            </label>
          </div>
        </div>
      </div>
      
      <div className="mt-6">
        <Button
          type="submit"
          variant="primary"
          isLoading={loading || isLoading}
          disabled={loading || isLoading}
        >
          {addressId ? 'Update Address' : 'Add Address'}
        </Button>
      </div>
    </form>
  );
};

export default AddressForm;
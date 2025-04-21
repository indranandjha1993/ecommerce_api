import React, { useState } from 'react';
import { Address } from '../../types';
import Button from '../ui/Button';
import Input from '../ui/Input';
import Select from '../ui/Select';

interface AddressFormProps {
  title?: string;
  initialValues?: Partial<Address>;
  onSubmit: (data: Partial<Address>) => void;
  submitLabel?: string;
  showCancelButton?: boolean;
  onCancel?: () => void;
}

const AddressForm: React.FC<AddressFormProps> = ({
  title,
  initialValues = {},
  onSubmit,
  submitLabel = 'Save Address',
  showCancelButton = false,
  onCancel,
}) => {
  const [formData, setFormData] = useState<Partial<Address>>({
    first_name: '',
    last_name: '',
    company: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'US',
    phone_number: '',
    email: '',
    ...initialValues,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    
    // Clear error when field is edited
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    const requiredFields = [
      'first_name',
      'last_name',
      'address_line1',
      'city',
      'state',
      'postal_code',
      'country',
      'phone_number',
    ];

    requiredFields.forEach((field) => {
      if (!formData[field as keyof Address]) {
        newErrors[field] = 'This field is required';
      }
    });

    // Validate phone number format
    if (formData.phone_number && !/^\+?[0-9]{10,15}$/.test(formData.phone_number)) {
      newErrors.phone_number = 'Please enter a valid phone number';
    }

    // Validate postal code format
    if (formData.postal_code && !/^[0-9]{5}(-[0-9]{4})?$/.test(formData.postal_code)) {
      newErrors.postal_code = 'Please enter a valid postal code (e.g., 12345 or 12345-6789)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {title && <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <Input
            label="First Name"
            name="first_name"
            value={formData.first_name || ''}
            onChange={handleChange}
            error={errors.first_name}
            required
          />
        </div>
        <div>
          <Input
            label="Last Name"
            name="last_name"
            value={formData.last_name || ''}
            onChange={handleChange}
            error={errors.last_name}
            required
          />
        </div>
      </div>

      <div className="mb-4">
        <Input
          label="Company (Optional)"
          name="company"
          value={formData.company || ''}
          onChange={handleChange}
        />
      </div>

      <div className="mb-4">
        <Input
          label="Address Line 1"
          name="address_line1"
          value={formData.address_line1 || ''}
          onChange={handleChange}
          error={errors.address_line1}
          required
        />
      </div>

      <div className="mb-4">
        <Input
          label="Address Line 2 (Optional)"
          name="address_line2"
          value={formData.address_line2 || ''}
          onChange={handleChange}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <Input
            label="City"
            name="city"
            value={formData.city || ''}
            onChange={handleChange}
            error={errors.city}
            required
          />
        </div>
        <div>
          <Input
            label="State/Province"
            name="state"
            value={formData.state || ''}
            onChange={handleChange}
            error={errors.state}
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <Input
            label="Postal Code"
            name="postal_code"
            value={formData.postal_code || ''}
            onChange={handleChange}
            error={errors.postal_code}
            required
          />
        </div>
        <div>
          <Select
            label="Country"
            name="country"
            value={formData.country || 'US'}
            onChange={handleChange}
            error={errors.country}
            required
          >
            <option value="US">United States</option>
            <option value="CA">Canada</option>
            <option value="UK">United Kingdom</option>
            <option value="AU">Australia</option>
            <option value="DE">Germany</option>
            <option value="FR">France</option>
            <option value="IN">India</option>
            <option value="JP">Japan</option>
          </Select>
        </div>
      </div>

      <div className="mb-4">
        <Input
          label="Phone Number"
          name="phone_number"
          type="tel"
          value={formData.phone_number || ''}
          onChange={handleChange}
          error={errors.phone_number}
          required
        />
      </div>

      <div className="mb-4">
        <Input
          label="Email"
          name="email"
          type="email"
          value={formData.email || ''}
          onChange={handleChange}
          error={errors.email}
        />
      </div>

      <div className="flex justify-between mt-6">
        {showCancelButton && onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" variant="primary" className={!showCancelButton ? 'ml-auto' : ''}>
          {submitLabel}
        </Button>
      </div>
    </form>
  );
};

export default AddressForm;
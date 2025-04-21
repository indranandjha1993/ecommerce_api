import React, { useState } from 'react';
import { User } from '../../types';
import Button from '../ui/Button';
import Input from '../ui/Input';

interface ProfileFormProps {
  user: User | null;
  onSubmit: (data: any) => Promise<void>;
}

const ProfileForm: React.FC<ProfileFormProps> = ({ user, onSubmit }) => {
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
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
  
  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
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
      setLoading(true);
      await onSubmit(formData);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="First Name"
          name="first_name"
          value={formData.first_name}
          onChange={handleChange}
          error={errors.first_name}
          required
        />
        
        <Input
          label="Last Name"
          name="last_name"
          value={formData.last_name}
          onChange={handleChange}
          error={errors.last_name}
        />
        
        <Input
          label="Email Address"
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          error={errors.email}
          required
          className="md:col-span-2"
        />
        
        <Input
          label="Phone Number"
          type="tel"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
          error={errors.phone}
          placeholder="+1 (555) 123-4567"
          className="md:col-span-2"
        />
      </div>
      
      <div className="mt-6">
        <Button
          type="submit"
          variant="primary"
          isLoading={loading}
          disabled={loading}
        >
          Save Changes
        </Button>
      </div>
    </form>
  );
};

export default ProfileForm;
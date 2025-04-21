import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useAuth } from '../../hooks/useAuth';
import { addNotification } from '../../store/slices/uiSlice';
import Button from '../ui/Button';
import Input from '../ui/Input';

const PasswordChangeForm: React.FC = () => {
  const dispatch = useDispatch();
  const { changePassword, loading } = useAuth();
  
  const [formData, setFormData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  
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
    
    if (!formData.current_password) {
      newErrors.current_password = 'Current password is required';
    }
    
    if (!formData.new_password) {
      newErrors.new_password = 'New password is required';
    } else if (formData.new_password.length < 8) {
      newErrors.new_password = 'Password must be at least 8 characters long';
    }
    
    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Please confirm your new password';
    } else if (formData.new_password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
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
      const success = await changePassword(
        formData.current_password,
        formData.new_password
      );
      
      if (success) {
        dispatch(
          addNotification({
            type: 'success',
            message: 'Password changed successfully!',
          })
        );
        
        // Reset form
        setFormData({
          current_password: '',
          new_password: '',
          confirm_password: '',
        });
      } else {
        dispatch(
          addNotification({
            type: 'error',
            message: 'Failed to change password. Please check your current password and try again.',
          })
        );
      }
    } catch (error) {
      dispatch(
        addNotification({
          type: 'error',
          message: 'Failed to change password. Please try again.',
        })
      );
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-4">
        <Input
          label="Current Password"
          type="password"
          name="current_password"
          value={formData.current_password}
          onChange={handleChange}
          error={errors.current_password}
          required
        />
        
        <Input
          label="New Password"
          type="password"
          name="new_password"
          value={formData.new_password}
          onChange={handleChange}
          error={errors.new_password}
          required
        />
        
        <Input
          label="Confirm New Password"
          type="password"
          name="confirm_password"
          value={formData.confirm_password}
          onChange={handleChange}
          error={errors.confirm_password}
          required
        />
      </div>
      
      <div className="mt-6">
        <Button
          type="submit"
          variant="primary"
          isLoading={loading}
          disabled={loading}
        >
          Change Password
        </Button>
      </div>
      
      <div className="mt-4 text-sm text-gray-500">
        <p>Password requirements:</p>
        <ul className="list-disc pl-5 mt-1">
          <li>At least 8 characters long</li>
          <li>Include both uppercase and lowercase letters</li>
          <li>Include at least one number or special character</li>
        </ul>
      </div>
    </form>
  );
};

export default PasswordChangeForm;
import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useDispatch } from 'react-redux';
import { passwordResetSchema } from '../../utils/validation';
import { addNotification } from '../../store/slices/uiSlice';
import { authService } from '../../services/auth.service';
import Input from '../ui/Input';
import Button from '../ui/Button';

type ResetPasswordFormValues = {
  password: string;
  confirm_password: string;
};

const ResetPasswordForm: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  
  const [loading, setLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(passwordResetSchema),
  });
  
  if (!token) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-red-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          
          <h2 className="mt-4 text-2xl font-bold text-gray-900">
            Invalid Reset Link
          </h2>
          
          <p className="mt-2 text-gray-600">
            The password reset link is invalid or has expired. Please request a new one.
          </p>
          
          <div className="mt-6">
            <Link to="/forgot-password">
              <Button variant="primary" fullWidth>
                Request New Link
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }
  
  const onSubmit = async (data: ResetPasswordFormValues) => {
    setLoading(true);
    
    try {
      await authService.resetPassword({
        token,
        password: data.password,
        confirm_password: data.confirm_password,
      });
      
      dispatch(
        addNotification({
          type: 'success',
          message: 'Your password has been reset successfully. You can now log in with your new password.',
        })
      );
      
      navigate('/login');
    } catch (error) {
      dispatch(
        addNotification({
          type: 'error',
          message: 'Failed to reset password. The link may have expired.',
        })
      );
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
        Reset Your Password
      </h2>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <Input
            label="New Password"
            type="password"
            {...register('password')}
            error={errors.password?.message}
            fullWidth
          />
        </div>
        
        <div>
          <Input
            label="Confirm New Password"
            type="password"
            {...register('confirm_password')}
            error={errors.confirm_password?.message}
            fullWidth
          />
        </div>
        
        <div>
          <Button
            type="submit"
            variant="primary"
            fullWidth
            isLoading={loading}
          >
            Reset Password
          </Button>
        </div>
      </form>
      
      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          Remember your password?{' '}
          <Link
            to="/login"
            className="font-medium text-blue-600 hover:text-blue-500"
          >
            Back to login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default ResetPasswordForm;
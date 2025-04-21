import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useDispatch } from 'react-redux';
import { passwordResetRequestSchema } from '../../utils/validation';
import { addNotification } from '../../store/slices/uiSlice';
import { authService } from '../../services/auth.service';
import Input from '../ui/Input';
import Button from '../ui/Button';

type ForgotPasswordFormValues = {
  email: string;
};

const ForgotPasswordForm: React.FC = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(passwordResetRequestSchema),
  });
  
  const onSubmit = async (data: ForgotPasswordFormValues) => {
    setLoading(true);
    
    try {
      await authService.requestPasswordReset(data);
      setSubmitted(true);
      dispatch(
        addNotification({
          type: 'success',
          message: 'Password reset instructions have been sent to your email.',
        })
      );
    } catch (error) {
      dispatch(
        addNotification({
          type: 'error',
          message: 'Failed to request password reset. Please try again.',
        })
      );
    } finally {
      setLoading(false);
    }
  };
  
  if (submitted) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-green-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          
          <h2 className="mt-4 text-2xl font-bold text-gray-900">
            Check Your Email
          </h2>
          
          <p className="mt-2 text-gray-600">
            We've sent password reset instructions to your email address. Please check your inbox.
          </p>
          
          <div className="mt-6">
            <Link to="/login">
              <Button variant="primary" fullWidth>
                Back to Login
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
        Forgot Your Password?
      </h2>
      
      <p className="text-gray-600 mb-6 text-center">
        Enter your email address and we'll send you instructions to reset your password.
      </p>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <Input
            label="Email Address"
            type="email"
            {...register('email')}
            error={errors.email?.message}
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
            Send Reset Instructions
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

export default ForgotPasswordForm;
import { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { useAuth } from '../hooks/useAuth';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';

type RegisterFormData = {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
};

const RegisterPage = () => {
  const { register: registerUser } = useAuth();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>();

  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await registerUser({
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        password: data.password,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="max-w-md mx-auto my-12 p-6 bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-bold text-center mb-6">Create an Account</h1>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <Input
              label="First Name"
              {...register('firstName', { 
                required: 'First name is required',
                minLength: {
                  value: 2,
                  message: 'First name must be at least 2 characters'
                }
              })}
              error={errors.firstName?.message}
            />
          </div>
          
          <div>
            <Input
              label="Last Name"
              {...register('lastName', { 
                required: 'Last name is required',
                minLength: {
                  value: 2,
                  message: 'Last name must be at least 2 characters'
                }
              })}
              error={errors.lastName?.message}
            />
          </div>
        </div>
        
        <div className="mb-4">
          <Input
            label="Email"
            type="email"
            {...register('email', { 
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address'
              }
            })}
            error={errors.email?.message}
          />
        </div>
        
        <div className="mb-4">
          <Input
            label="Password"
            type="password"
            {...register('password', { 
              required: 'Password is required',
              minLength: {
                value: 6,
                message: 'Password must be at least 6 characters'
              }
            })}
            error={errors.password?.message}
          />
        </div>
        
        <div className="mb-6">
          <Input
            label="Confirm Password"
            type="password"
            {...register('confirmPassword', { 
              required: 'Please confirm your password',
              validate: value => 
                value === password || 'Passwords do not match'
            })}
            error={errors.confirmPassword?.message}
          />
        </div>
        
        <Button
          type="submit"
          className="w-full"
          isLoading={isLoading}
          disabled={isLoading}
        >
          Register
        </Button>
      </form>
      
      <div className="mt-4 text-center">
        <p>
          Already have an account?{' '}
          <Link to="/login" className="text-blue-600 hover:text-blue-800">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;
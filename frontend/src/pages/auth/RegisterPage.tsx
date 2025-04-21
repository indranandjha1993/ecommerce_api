import React, { useEffect } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import AuthForm from '../../components/auth/AuthForm';
import { useAuth } from '../../contexts/AuthContext';
import { GuestGuard } from '../../contexts/AuthContext';
import Card from '../../components/ui/Card';

const RegisterPage: React.FC = () => {
  const { register, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();

  // Clear any previous errors when mounting the component
  useEffect(() => {
    clearError();
  }, [clearError]);

  // Handle registration form submission
  const handleRegister = async (data: { name: string; email: string; password: string }) => {
    const success = await register(data.name, data.email, data.password);
    if (success) {
      navigate('/', { replace: true });
    }
  };

  return (
    <GuestGuard fallback={<Navigate to="/" replace />}>
      <div className="min-h-[calc(100vh-200px)] flex flex-col items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <Card className="mb-8">
            <Card.Header>
              <div className="text-center w-full">
                <Card.Title className="text-2xl font-bold text-gray-900">Create an account</Card.Title>
                <Card.Description>
                  Join us to start shopping and get personalized recommendations
                </Card.Description>
              </div>
            </Card.Header>
            
            <Card.Content>
              <AuthForm
                mode="register"
                onSubmit={handleRegister}
                isLoading={isLoading}
                error={error}
              />
            </Card.Content>
          </Card>
          
          <div className="text-center">
            <p className="text-sm text-gray-600">
              By creating an account, you agree to our{' '}
              <a href="/terms" className="text-blue-600 hover:text-blue-800 font-medium">
                Terms of Service
              </a>{' '}
              and{' '}
              <a href="/privacy" className="text-blue-600 hover:text-blue-800 font-medium">
                Privacy Policy
              </a>
            </p>
          </div>
        </div>
      </div>
    </GuestGuard>
  );
};

export default RegisterPage;
import React, { useState, useEffect } from 'react';
import { Navigate, useNavigate, useLocation } from 'react-router-dom';
import AuthForm from '../../components/auth/AuthForm';
import { useAuth } from '../../contexts/AuthContext';
import { GuestGuard } from '../../contexts/AuthContext';
import Card from '../../components/ui/Card';

const LoginPage: React.FC = () => {
  const { login, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [redirectTo, setRedirectTo] = useState<string>('/');

  // Get the redirect path from location state
  useEffect(() => {
    const state = location.state as { from?: { pathname: string } };
    if (state?.from?.pathname) {
      setRedirectTo(state.from.pathname);
    } else {
      setRedirectTo('/');
    }
    
    // Clear any previous errors when mounting the component
    clearError();
  }, [location, clearError]);

  // Handle login form submission
  const handleLogin = async (data: { email: string; password: string }) => {
    const success = await login(data.email, data.password);
    if (success) {
      navigate(redirectTo, { replace: true });
    }
  };

  return (
    <GuestGuard fallback={<Navigate to="/" replace />}>
      <div className="min-h-[calc(100vh-200px)] flex flex-col items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <Card className="mb-8">
            <Card.Header>
              <div className="text-center w-full">
                <Card.Title className="text-2xl font-bold text-gray-900">Welcome back</Card.Title>
                <Card.Description>
                  Sign in to your account to continue shopping
                </Card.Description>
              </div>
            </Card.Header>
            
            <Card.Content>
              <AuthForm
                mode="login"
                onSubmit={handleLogin}
                isLoading={isLoading}
                error={error}
              />
            </Card.Content>
          </Card>
          
          <div className="text-center">
            <p className="text-sm text-gray-600">
              By signing in, you agree to our{' '}
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

export default LoginPage;
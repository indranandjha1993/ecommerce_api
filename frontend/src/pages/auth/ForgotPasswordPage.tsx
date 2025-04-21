import React, { useState, useEffect } from 'react';
import { Link, Navigate } from 'react-router-dom';
import AuthForm from '../../components/auth/AuthForm';
import Alert from '../../components/ui/Alert';
import { useAuth } from '../../contexts/AuthContext';
import { GuestGuard } from '../../contexts/AuthContext';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

const ForgotPasswordPage: React.FC = () => {
  const { forgotPassword, isLoading, error, clearError } = useAuth();
  const [success, setSuccess] = useState<string | null>(null);

  // Clear any previous errors when mounting the component
  useEffect(() => {
    clearError();
  }, [clearError]);

  // Handle forgot password form submission
  const handleForgotPassword = async (data: { email: string }) => {
    const result = await forgotPassword(data.email);
    if (result) {
      setSuccess(
        'Password reset instructions have been sent to your email address. Please check your inbox.'
      );
    }
  };

  return (
    <GuestGuard fallback={<Navigate to="/" replace />}>
      <div className="min-h-[calc(100vh-200px)] flex flex-col items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <Card className="mb-8">
            <Card.Header>
              <div className="text-center w-full">
                <Card.Title className="text-2xl font-bold text-gray-900">Forgot your password?</Card.Title>
                <Card.Description>
                  Enter your email address and we'll send you a link to reset your password
                </Card.Description>
              </div>
            </Card.Header>
            
            <Card.Content>
              {success ? (
                <div className="space-y-6">
                  <Alert variant="success" title="Email Sent">
                    {success}
                  </Alert>
                  <div className="text-center mt-6">
                    <Button 
                      variant="primary" 
                      as={Link} 
                      to="/login"
                      fullWidth
                    >
                      Return to login
                    </Button>
                  </div>
                </div>
              ) : (
                <AuthForm
                  mode="forgot-password"
                  onSubmit={handleForgotPassword}
                  isLoading={isLoading}
                  error={error}
                />
              )}
            </Card.Content>
          </Card>
          
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Remember your password?{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-800 font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </GuestGuard>
  );
};

export default ForgotPasswordPage;
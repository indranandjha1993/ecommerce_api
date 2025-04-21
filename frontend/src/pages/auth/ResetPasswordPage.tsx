import React, { useState, useEffect } from 'react';
import { Link, Navigate, useParams, useNavigate } from 'react-router-dom';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import Alert from '../../components/ui/Alert';
import Card from '../../components/ui/Card';
import { useAuth } from '../../contexts/AuthContext';
import { GuestGuard } from '../../contexts/AuthContext';

const ResetPasswordPage: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const { resetPassword, isLoading, error, clearError } = useAuth();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [showPassword, setShowPassword] = useState(false);

  // Clear any previous errors when mounting the component
  useEffect(() => {
    clearError();
  }, [clearError]);

  // Validate form
  const validateForm = (): boolean => {
    setFormError(null);

    if (!password) {
      setFormError('Please enter a new password');
      return false;
    }

    if (password.length < 8) {
      setFormError('Password must be at least 8 characters long');
      return false;
    }

    if (password !== confirmPassword) {
      setFormError('Passwords do not match');
      return false;
    }

    return true;
  };

  // Handle reset password form submission
  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm() || !token) {
      return;
    }

    const result = await resetPassword(token, password);
    if (result) {
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    }
  };

  return (
    <GuestGuard fallback={<Navigate to="/" replace />}>
      <div className="min-h-[calc(100vh-200px)] flex flex-col items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <Card className="mb-8">
            <Card.Header>
              <div className="text-center w-full">
                <Card.Title className="text-2xl font-bold text-gray-900">Reset your password</Card.Title>
                <Card.Description>
                  Enter a new password for your account
                </Card.Description>
              </div>
            </Card.Header>
            
            <Card.Content>
              {success ? (
                <div className="space-y-6">
                  <Alert variant="success" title="Password Reset Successful">
                    Your password has been reset successfully. You will be redirected to the login page in a few seconds.
                  </Alert>
                  <div className="mt-6 text-center">
                    <Button 
                      variant="primary" 
                      as={Link} 
                      to="/login"
                      fullWidth
                    >
                      Go to login page
                    </Button>
                  </div>
                </div>
              ) : (
                <>
                  {(error || formError) && (
                    <Alert 
                      variant="error" 
                      title="Error" 
                      className="mb-4"
                    >
                      {error || formError}
                    </Alert>
                  )}

                  <form onSubmit={handleResetPassword} className="space-y-4">
                    <Input
                      label="New Password"
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      autoComplete="new-password"
                      disabled={isLoading}
                      rightElement={
                        <button
                          type="button"
                          className="text-gray-500 hover:text-gray-700 focus:outline-none"
                          onClick={() => setShowPassword(!showPassword)}
                          tabIndex={-1}
                        >
                          {showPassword ? (
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                              <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                            </svg>
                          ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                              <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                            </svg>
                          )}
                        </button>
                      }
                    />

                    <Input
                      label="Confirm Password"
                      id="confirmPassword"
                      type={showPassword ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      autoComplete="new-password"
                      disabled={isLoading}
                    />

                    <Button
                      type="submit"
                      variant="primary"
                      size="lg"
                      fullWidth
                      isLoading={isLoading}
                      loadingText="Resetting..."
                      className="mt-6"
                    >
                      Reset Password
                    </Button>
                  </form>
                </>
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

export default ResetPasswordPage;
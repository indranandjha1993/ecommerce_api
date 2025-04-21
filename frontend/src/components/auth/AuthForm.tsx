import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { twMerge } from 'tailwind-merge';
import Button from '../ui/Button';
import Input from '../ui/Input';
import Alert from '../ui/Alert';

export type AuthFormMode = 'login' | 'register' | 'forgot-password';

export interface AuthFormProps {
  mode: AuthFormMode;
  onSubmit: (data: any) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

const AuthForm: React.FC<AuthFormProps> = ({
  mode,
  onSubmit,
  isLoading = false,
  error = null,
  className,
}) => {
  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  // Form validation
  const validateForm = (): boolean => {
    setFormError(null);

    if (mode === 'forgot-password') {
      if (!email) {
        setFormError('Please enter your email address');
        return false;
      }
      return true;
    }

    if (!email) {
      setFormError('Please enter your email address');
      return false;
    }

    if (mode === 'register' && !name) {
      setFormError('Please enter your name');
      return false;
    }

    if (mode !== 'forgot-password' && !password) {
      setFormError('Please enter your password');
      return false;
    }

    if (mode === 'register') {
      if (password.length < 8) {
        setFormError('Password must be at least 8 characters long');
        return false;
      }
      
      if (password !== confirmPassword) {
        setFormError('Passwords do not match');
        return false;
      }
    }

    return true;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      const formData = {
        email,
        password,
        name: mode === 'register' ? name : undefined,
      };

      await onSubmit(formData);
    } catch (err) {
      console.error('Form submission error:', err);
    }
  };

  // Form title and description based on mode
  const getFormContent = () => {
    switch (mode) {
      case 'login':
        return {
          submitText: 'Sign In',
          footerText: "Don't have an account?",
          footerLinkText: 'Create an account',
          footerLinkUrl: '/register',
        };
      case 'register':
        return {
          submitText: 'Create Account',
          footerText: 'Already have an account?',
          footerLinkText: 'Sign in',
          footerLinkUrl: '/login',
        };
      case 'forgot-password':
        return {
          submitText: 'Send Reset Link',
          footerText: 'Remember your password?',
          footerLinkText: 'Sign in',
          footerLinkUrl: '/login',
        };
      default:
        return {
          submitText: 'Submit',
          footerText: '',
          footerLinkText: '',
          footerLinkUrl: '',
        };
    }
  };

  const content = getFormContent();

  return (
    <div className={twMerge('w-full', className)}>
      {(error || formError) && (
        <Alert 
          variant="error" 
          title="Error" 
          className="mb-6"
        >
          {error || formError}
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        {mode === 'register' && (
          <div>
            <Input
              label="Full Name"
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              required
              autoComplete="name"
              disabled={isLoading}
              fullWidth
            />
          </div>
        )}

        <div>
          <Input
            label="Email Address"
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            autoComplete="email"
            disabled={isLoading}
            fullWidth
          />
        </div>

        {mode !== 'forgot-password' && (
          <div>
            <Input
              label="Password"
              id="password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              disabled={isLoading}
              fullWidth
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
          </div>
        )}

        {mode === 'register' && (
          <div>
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
              fullWidth
            />
          </div>
        )}

        {mode === 'login' && (
          <div className="flex justify-end">
            <Link
              to="/forgot-password"
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Forgot your password?
            </Link>
          </div>
        )}

        <Button
          type="submit"
          variant="primary"
          size="lg"
          fullWidth
          isLoading={isLoading}
          loadingText={mode === 'login' ? 'Signing in...' : mode === 'register' ? 'Creating account...' : 'Sending...'}
          className="mt-6"
        >
          {content.submitText}
        </Button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          {content.footerText}{' '}
          <Link to={content.footerLinkUrl} className="text-blue-600 hover:text-blue-800 font-medium">
            {content.footerLinkText}
          </Link>
        </p>
      </div>

      {mode !== 'forgot-password' && (
        <div className="mt-8">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or continue with</span>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <Button
              type="button"
              variant="outline"
              size="md"
              fullWidth
              leftIcon={
                <svg className="h-5 w-5" aria-hidden="true" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.0003 4.75C13.7703 4.75 15.3553 5.36002 16.6053 6.54998L20.0303 3.125C17.9502 1.19 15.2353 0 12.0003 0C7.31028 0 3.25527 2.69 1.28027 6.60998L5.27028 9.70498C6.21525 6.86002 8.87028 4.75 12.0003 4.75Z" fill="#EA4335" />
                  <path d="M23.49 12.275C23.49 11.49 23.415 10.73 23.3 10H12V14.51H18.47C18.18 15.99 17.34 17.25 16.08 18.1L19.945 21.1C22.2 19.01 23.49 15.92 23.49 12.275Z" fill="#4285F4" />
                  <path d="M5.26498 14.2949C5.02498 13.5699 4.88501 12.7999 4.88501 11.9999C4.88501 11.1999 5.01998 10.4299 5.26498 9.7049L1.275 6.60986C0.46 8.22986 0 10.0599 0 11.9999C0 13.9399 0.46 15.7699 1.28 17.3899L5.26498 14.2949Z" fill="#FBBC05" />
                  <path d="M12.0004 24.0001C15.2404 24.0001 17.9654 22.935 19.9454 21.095L16.0804 18.095C15.0054 18.82 13.6204 19.245 12.0004 19.245C8.8704 19.245 6.21537 17.135 5.2654 14.29L1.27539 17.385C3.25539 21.31 7.3104 24.0001 12.0004 24.0001Z" fill="#34A853" />
                </svg>
              }
            >
              Google
            </Button>
            <Button
              type="button"
              variant="outline"
              size="md"
              fullWidth
              leftIcon={
                <svg className="h-5 w-5" aria-hidden="true" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M22.1771 11.1771C22.1771 8.95337 21.3328 6.94464 19.8771 5.48908C18.4215 4.03351 16.4128 3.18908 14.1891 3.18908C11.9653 3.18908 9.95659 4.03351 8.50103 5.48908C7.04546 6.94464 6.20103 8.95337 6.20103 11.1771C6.20103 13.4009 7.04546 15.4096 8.50103 16.8652C9.95659 18.3207 11.9653 19.1652 14.1891 19.1652C16.4128 19.1652 18.4215 18.3207 19.8771 16.8652C21.3328 15.4096 22.1771 13.4009 22.1771 11.1771Z" fill="#1877F2" />
                  <path fillRule="evenodd" clipRule="evenodd" d="M13.1771 17.1771V11.1771H15.1771L15.5 9.17712H13.1771V7.88099C13.1771 7.17712 13.3542 6.67712 14.3885 6.67712H15.5885V4.88099C15.3828 4.85337 14.6885 4.79175 13.8885 4.79175C12.1771 4.79175 11.0057 5.85337 11.0057 7.67712V9.17712H9.00568V11.1771H11.0057V17.1771H13.1771Z" fill="white" />
                </svg>
              }
            >
              Facebook
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuthForm;
import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/ui/Button';

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[calc(100vh-16rem)] flex items-center justify-center px-4 py-16">
      <div className="max-w-md w-full text-center">
        <h1 className="text-9xl font-extrabold text-gray-900">404</h1>
        <p className="text-2xl font-semibold text-gray-700 mt-4">Page Not Found</p>
        <p className="text-gray-500 mt-6">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="mt-10">
          <Link to="/">
            <Button variant="primary" size="lg">
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
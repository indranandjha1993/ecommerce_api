import React from 'react';
import { twMerge } from 'tailwind-merge';

interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'danger' | 'white' | 'gray';
  variant?: 'border' | 'dots' | 'spinner' | 'pulse';
  fullPage?: boolean;
  label?: string;
  className?: string;
  thickness?: 'thin' | 'regular' | 'thick';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  color = 'primary',
  variant = 'border',
  fullPage = false,
  label,
  className,
  thickness = 'regular'
}) => {
  const sizeClasses = {
    xs: 'w-4 h-4',
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  const colorClasses = {
    primary: 'text-blue-600',
    secondary: 'text-purple-600',
    accent: 'text-orange-500',
    success: 'text-green-600',
    warning: 'text-amber-500',
    danger: 'text-red-600',
    white: 'text-white',
    gray: 'text-gray-600',
  };

  const thicknessClasses = {
    thin: 'border',
    regular: 'border-2',
    thick: 'border-4',
  };

  const containerClasses = twMerge(
    'flex flex-col items-center justify-center',
    fullPage ? 'fixed inset-0 bg-white/80 backdrop-blur-sm z-50' : 'p-4',
    className
  );

  const renderSpinner = () => {
    switch (variant) {
      case 'border':
        return (
          <div 
            className={twMerge(
              `animate-spin rounded-full ${thicknessClasses[thickness]} border-t-transparent border-l-transparent`,
              colorClasses[color],
              sizeClasses[size]
            )}
          />
        );
      
      case 'dots':
        return (
          <div className="flex space-x-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={twMerge(
                  'rounded-full animate-pulse',
                  colorClasses[color],
                  size === 'xs' ? 'w-1 h-1' :
                  size === 'sm' ? 'w-1.5 h-1.5' :
                  size === 'md' ? 'w-2 h-2' :
                  size === 'lg' ? 'w-3 h-3' :
                  'w-4 h-4'
                )}
                style={{
                  animationDelay: `${i * 0.15}s`,
                  backgroundColor: 'currentColor'
                }}
              />
            ))}
          </div>
        );
      
      case 'spinner':
        return (
          <svg
            className={twMerge(
              'animate-spin',
              colorClasses[color],
              sizeClasses[size]
            )}
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth={thickness === 'thin' ? '2' : thickness === 'regular' ? '3' : '4'}
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        );
      
      case 'pulse':
        return (
          <div 
            className={twMerge(
              'animate-pulse rounded-full bg-current',
              colorClasses[color],
              sizeClasses[size]
            )}
          />
        );
      
      default:
        return null;
    }
  };

  return (
    <div className={containerClasses}>
      {renderSpinner()}
      {label && (
        <span className={twMerge(
          'mt-2 text-sm font-medium',
          colorClasses[color]
        )}>
          {label}
        </span>
      )}
    </div>
  );
};

export default LoadingSpinner;
import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import { twMerge } from 'tailwind-merge';
import { Link } from 'react-router-dom';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'danger' | 'outline' | 'ghost' | 'link';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  fullWidth?: boolean;
  isLoading?: boolean;
  loadingText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  rounded?: boolean;
  pill?: boolean;
  elevated?: boolean;
  animated?: boolean;
  href?: string;
  external?: boolean;
  as?: React.ElementType;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(({
  children,
  className,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  isLoading = false,
  loadingText,
  disabled,
  leftIcon,
  rightIcon,
  rounded = false,
  pill = false,
  elevated = false,
  animated = true,
  href,
  external,
  as,
  ...props
}, ref) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  
  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800 focus-visible:ring-primary-500',
    secondary: 'bg-secondary-600 text-white hover:bg-secondary-700 active:bg-secondary-800 focus-visible:ring-secondary-500',
    accent: 'bg-accent-500 text-white hover:bg-accent-600 active:bg-accent-700 focus-visible:ring-accent-400',
    success: 'bg-success text-white hover:bg-green-700 active:bg-green-800 focus-visible:ring-green-500',
    warning: 'bg-warning text-white hover:bg-amber-600 active:bg-amber-700 focus-visible:ring-amber-400',
    danger: 'bg-error text-white hover:bg-red-700 active:bg-red-800 focus-visible:ring-red-500',
    outline: 'border-2 border-current bg-transparent text-primary-600 hover:bg-primary-50 active:bg-primary-100 focus-visible:ring-primary-500',
    ghost: 'bg-transparent text-primary-600 hover:bg-primary-50 active:bg-primary-100 focus-visible:ring-primary-500',
    link: 'bg-transparent text-primary-600 hover:text-primary-800 hover:underline p-0 h-auto focus-visible:ring-primary-500',
  };
  
  const sizes = {
    xs: 'h-7 px-2 text-xs',
    sm: 'h-9 px-3 text-sm',
    md: 'h-10 px-4 text-base',
    lg: 'h-12 px-6 text-lg',
    xl: 'h-14 px-8 text-xl',
  };
  
  const radiusStyles = pill 
    ? 'rounded-full' 
    : rounded 
      ? 'rounded-xl' 
      : 'rounded-md';
  
  const elevationStyles = elevated 
    ? 'shadow-md hover:shadow-lg active:shadow-sm' 
    : '';
  
  const animationStyles = animated && variant !== 'link' 
    ? 'transform hover:-translate-y-0.5 active:translate-y-0 transition-transform' 
    : '';
  
  const classes = twMerge(
    baseStyles,
    variants[variant],
    sizes[size],
    radiusStyles,
    elevationStyles,
    animationStyles,
    fullWidth ? 'w-full' : '',
    className
  );

  // Loading spinner component
  const LoadingSpinner = () => (
    <svg
      className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
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
        strokeWidth="4"
      ></circle>
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
    </svg>
  );
  
  // Button content
  const buttonContent = (
    <>
      {isLoading && <LoadingSpinner />}
      {!isLoading && leftIcon && <span className="mr-2 flex items-center">{leftIcon}</span>}
      <span>{isLoading && loadingText ? loadingText : children}</span>
      {!isLoading && rightIcon && <span className="ml-2 flex items-center">{rightIcon}</span>}
    </>
  );

  // If href is provided, render as Link or anchor
  if (href) {
    const linkProps = {
      className: classes,
      ...props,
    };

    if (external) {
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className={classes}
          {...props}
        >
          {buttonContent}
        </a>
      );
    }

    return (
      <Link to={href} className={classes} {...linkProps}>
        {buttonContent}
      </Link>
    );
  }

  // If custom element type is provided
  if (as) {
    const Component = as;
    return (
      <Component
        className={classes}
        disabled={disabled || isLoading}
        {...props}
      >
        {buttonContent}
      </Component>
    );
  }
  
  // Default button
  return (
    <button
      ref={ref}
      className={classes}
      disabled={disabled || isLoading}
      {...props}
    >
      {buttonContent}
    </button>
  );
});

Button.displayName = 'Button';

export default Button;
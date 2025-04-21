import React, { InputHTMLAttributes, forwardRef, useState } from 'react';
import { twMerge } from 'tailwind-merge';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  rightAction?: React.ReactNode;
  fullWidth?: boolean;
  variant?: 'outlined' | 'filled' | 'underlined';
  size?: 'sm' | 'md' | 'lg';
  labelPlacement?: 'top' | 'floating';
  rounded?: boolean;
  animated?: boolean;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className, 
    label, 
    error, 
    helperText, 
    leftIcon, 
    rightIcon,
    rightAction,
    fullWidth = false,
    variant = 'outlined',
    size = 'md',
    labelPlacement = 'top',
    rounded = false,
    animated = true,
    onFocus,
    onBlur,
    value,
    defaultValue,
    ...props 
  }, ref) => {
    const [focused, setFocused] = useState(false);
    const [hasValue, setHasValue] = useState(
      value !== undefined 
        ? Boolean(value) 
        : defaultValue !== undefined 
          ? Boolean(defaultValue) 
          : false
    );

    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
      setFocused(true);
      onFocus?.(e);
    };

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setFocused(false);
      setHasValue(Boolean(e.target.value));
      onBlur?.(e);
    };

    // Base styles for different variants
    const variantStyles = {
      outlined: 'border bg-transparent',
      filled: 'border-0 bg-gray-100 focus:bg-transparent',
      underlined: 'rounded-none border-0 border-b-2 bg-transparent px-0',
    };

    // Border colors based on state
    const borderStyles = {
      default: {
        outlined: 'border-gray-300 focus:border-blue-500',
        filled: 'border-transparent',
        underlined: 'border-gray-300 focus:border-blue-500',
      },
      error: {
        outlined: 'border-red-500 focus:border-red-600',
        filled: 'border-transparent',
        underlined: 'border-red-500 focus:border-red-600',
      },
      focused: {
        outlined: 'border-blue-500',
        filled: 'border-transparent',
        underlined: 'border-blue-500',
      },
    };

    // Size styles
    const sizeStyles = {
      sm: 'h-8 text-xs',
      md: 'h-10 text-sm',
      lg: 'h-12 text-base',
    };

    // Padding styles based on icons
    const paddingStyles = {
      left: leftIcon ? 'pl-10' : 'pl-3',
      right: rightIcon || rightAction ? 'pr-10' : 'pr-3',
    };

    // Animation styles
    const animationStyles = animated 
      ? 'transition-all duration-200 ease-in-out' 
      : '';

    // Rounded styles
    const roundedStyles = rounded 
      ? 'rounded-xl' 
      : variant === 'underlined' 
        ? 'rounded-none' 
        : 'rounded-md';

    // Focus ring styles
    const focusRingStyles = variant === 'underlined'
      ? 'focus:ring-0'
      : 'focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500';

    // Combine all input styles
    const inputClasses = twMerge(
      'w-full py-2 outline-none',
      sizeStyles[size],
      variantStyles[variant],
      error 
        ? borderStyles.error[variant] 
        : focused 
          ? borderStyles.focused[variant] 
          : borderStyles.default[variant],
      paddingStyles.left,
      paddingStyles.right,
      roundedStyles,
      focusRingStyles,
      animationStyles,
      'placeholder:text-gray-400 disabled:cursor-not-allowed disabled:opacity-50',
      className
    );

    // Container styles
    const containerClasses = twMerge(
      'relative',
      fullWidth ? 'w-full' : ''
    );

    // Label styles
    const labelClasses = twMerge(
      'text-gray-700 font-medium transition-all duration-200',
      labelPlacement === 'floating' ? 'absolute pointer-events-none' : 'block mb-1',
      labelPlacement === 'floating' && (focused || hasValue) 
        ? '-translate-y-6 text-xs text-blue-600' 
        : labelPlacement === 'floating' 
          ? 'translate-y-0 left-3 text-sm' 
          : 'text-sm',
      error && 'text-red-600',
      labelPlacement === 'floating' && 'z-10 origin-[0]'
    );

    return (
      <div className={containerClasses}>
        {label && labelPlacement === 'top' && (
          <label className={labelClasses}>
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-500">
              {leftIcon}
            </div>
          )}
          
          <input 
            ref={ref} 
            className={inputClasses} 
            onFocus={handleFocus}
            onBlur={handleBlur}
            value={value}
            defaultValue={defaultValue}
            {...props} 
          />
          
          {label && labelPlacement === 'floating' && (
            <label className={labelClasses}>
              {label}
            </label>
          )}
          
          {rightIcon && !rightAction && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-gray-500">
              {rightIcon}
            </div>
          )}
          
          {rightAction && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-3">
              {rightAction}
            </div>
          )}
        </div>
        
        {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
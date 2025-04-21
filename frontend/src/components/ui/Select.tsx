import React from 'react';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  fullWidth?: boolean;
  children: React.ReactNode;
}

const Select: React.FC<SelectProps> = ({
  label,
  error,
  fullWidth = false,
  className = '',
  children,
  ...props
}) => {
  return (
    <div className={`${fullWidth ? 'w-full' : ''} ${className}`}>
      {label && (
        <label
          htmlFor={props.id || props.name}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
          {props.required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <select
        className={`
          block rounded-md shadow-sm border-gray-300 focus:ring-blue-500 focus:border-blue-500 sm:text-sm
          ${error ? 'border-red-300' : ''}
          ${fullWidth ? 'w-full' : ''}
        `}
        {...props}
      >
        {children}
      </select>
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
};

export default Select;
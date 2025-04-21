import React, { forwardRef } from 'react';
import { twMerge } from 'tailwind-merge';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'primary' | 'secondary' | 'accent' | 'success' | 'danger' | 'warning' | 'info' | 'neutral';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  shape?: 'rounded' | 'pill' | 'square';
  bordered?: boolean;
  dot?: boolean;
  dotPosition?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  dotColor?: string;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  onClick?: () => void;
  removable?: boolean;
  onRemove?: () => void;
  animated?: boolean;
  glow?: boolean;
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(({
  children,
  className,
  variant = 'primary',
  size = 'md',
  shape = 'rounded',
  bordered = false,
  dot = false,
  dotPosition = 'top-right',
  dotColor,
  icon,
  iconPosition = 'left',
  onClick,
  removable = false,
  onRemove,
  animated = false,
  glow = false,
  ...props
}, ref) => {
  // Solid variants
  const solidVariants = {
    primary: 'bg-primary-100 text-primary-800',
    secondary: 'bg-secondary-100 text-secondary-800',
    accent: 'bg-accent-100 text-accent-800',
    success: 'bg-green-100 text-green-800',
    danger: 'bg-red-100 text-red-800',
    warning: 'bg-amber-100 text-amber-800',
    info: 'bg-sky-100 text-sky-800',
    neutral: 'bg-neutral-100 text-neutral-800',
  };

  // Bordered variants
  const borderedVariants = {
    primary: 'bg-transparent text-primary-600 border border-primary-600',
    secondary: 'bg-transparent text-secondary-600 border border-secondary-600',
    accent: 'bg-transparent text-accent-600 border border-accent-600',
    success: 'bg-transparent text-green-600 border border-green-600',
    danger: 'bg-transparent text-red-600 border border-red-600',
    warning: 'bg-transparent text-amber-600 border border-amber-600',
    info: 'bg-transparent text-sky-600 border border-sky-600',
    neutral: 'bg-transparent text-neutral-600 border border-neutral-600',
  };

  // Dot colors
  const dotColors = {
    primary: 'bg-primary-600',
    secondary: 'bg-secondary-600',
    accent: 'bg-accent-500',
    success: 'bg-green-600',
    danger: 'bg-red-600',
    warning: 'bg-amber-500',
    info: 'bg-sky-600',
    neutral: 'bg-neutral-600',
  };

  // Size classes
  const sizes = {
    xs: 'text-xs px-1.5 py-0.5 leading-none',
    sm: 'text-xs px-2 py-0.5 leading-tight',
    md: 'text-sm px-2.5 py-0.5 leading-tight',
    lg: 'text-base px-3 py-1 leading-normal',
  };

  // Shape classes
  const shapes = {
    rounded: 'rounded',
    pill: 'rounded-full',
    square: 'rounded-none',
  };

  // Dot position classes
  const dotPositions = {
    'top-right': '-top-1 -right-1',
    'top-left': '-top-1 -left-1',
    'bottom-right': '-bottom-1 -right-1',
    'bottom-left': '-bottom-1 -left-1',
  };

  // Animation classes
  const animationClass = animated ? 'transition-all duration-300 hover:scale-105' : '';
  
  // Glow effect
  const glowClass = glow ? `${variant === 'primary' ? 'shadow-primary-500/50' : 
                             variant === 'secondary' ? 'shadow-secondary-500/50' :
                             variant === 'accent' ? 'shadow-accent-500/50' :
                             variant === 'success' ? 'shadow-green-500/50' :
                             variant === 'danger' ? 'shadow-red-500/50' :
                             variant === 'warning' ? 'shadow-amber-500/50' :
                             variant === 'info' ? 'shadow-sky-500/50' :
                             'shadow-neutral-500/50'} shadow-md` : '';

  // Combine all classes
  const classes = twMerge(
    'inline-flex items-center justify-center font-medium whitespace-nowrap',
    bordered ? borderedVariants[variant] : solidVariants[variant],
    sizes[size],
    shapes[shape],
    animationClass,
    glowClass,
    onClick ? 'cursor-pointer hover:opacity-90 active:opacity-100' : '',
    className
  );

  // Handle click event
  const handleClick = () => {
    if (onClick) onClick();
  };

  // Handle remove click
  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onRemove) onRemove();
  };

  return (
    <span ref={ref} className={`relative inline-flex ${dot ? 'p-0.5' : ''}`} onClick={handleClick} {...props}>
      {dot && (
        <span 
          className={twMerge(
            'absolute w-2 h-2 rounded-full',
            dotPositions[dotPosition],
            dotColor || dotColors[variant]
          )}
        />
      )}
      <span className={classes}>
        {icon && iconPosition === 'left' && (
          <span className="mr-1 flex items-center">{icon}</span>
        )}
        {children}
        {icon && iconPosition === 'right' && (
          <span className="ml-1 flex items-center">{icon}</span>
        )}
        {removable && (
          <button
            type="button"
            className="ml-1 -mr-1 h-4 w-4 rounded-full inline-flex items-center justify-center text-current opacity-60 hover:opacity-100"
            onClick={handleRemove}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-3 h-3">
              <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
            </svg>
          </button>
        )}
      </span>
    </span>
  );
});

Badge.displayName = 'Badge';

export default Badge;
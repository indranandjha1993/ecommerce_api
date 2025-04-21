import React, { useState } from 'react';
import { twMerge } from 'tailwind-merge';

export interface RatingProps {
  value: number;
  max?: number;
  precision?: 0.5 | 1;
  size?: 'sm' | 'md' | 'lg';
  readOnly?: boolean;
  onChange?: (value: number) => void;
  emptyIcon?: React.ReactNode;
  filledIcon?: React.ReactNode;
  halfFilledIcon?: React.ReactNode;
  className?: string;
  iconClassName?: string;
  showValue?: boolean;
  valueClassName?: string;
  color?: 'yellow' | 'orange' | 'red' | 'blue' | 'green' | 'purple';
  hoverColor?: string;
  label?: string;
  labelPosition?: 'top' | 'left' | 'right' | 'bottom';
}

const Rating: React.FC<RatingProps> = ({
  value,
  max = 5,
  precision = 1,
  size = 'md',
  readOnly = false,
  onChange,
  emptyIcon,
  filledIcon,
  halfFilledIcon,
  className,
  iconClassName,
  showValue = false,
  valueClassName,
  color = 'yellow',
  hoverColor,
  label,
  labelPosition = 'left',
}) => {
  const [hoverValue, setHoverValue] = useState<number | null>(null);
  const [isHovering, setIsHovering] = useState(false);

  // Size classes
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  // Color classes
  const colorClasses = {
    yellow: 'text-yellow-400',
    orange: 'text-orange-400',
    red: 'text-red-400',
    blue: 'text-blue-400',
    green: 'text-green-400',
    purple: 'text-purple-400',
  };

  // Default icons
  const defaultEmptyIcon = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={twMerge(sizeClasses[size], iconClassName)}
    >
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </svg>
  );

  const defaultFilledIcon = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className={twMerge(sizeClasses[size], iconClassName)}
    >
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </svg>
  );

  const defaultHalfFilledIcon = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className={twMerge(sizeClasses[size], iconClassName)}
    >
      <defs>
        <linearGradient id="half-fill" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="50%" stopColor="currentColor" />
          <stop offset="50%" stopColor="transparent" stopOpacity="1" />
        </linearGradient>
      </defs>
      <polygon
        points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
        fill="url(#half-fill)"
        stroke="currentColor"
        strokeWidth="1"
      />
    </svg>
  );

  // Handle mouse enter
  const handleMouseEnter = () => {
    if (!readOnly) {
      setIsHovering(true);
    }
  };

  // Handle mouse leave
  const handleMouseLeave = () => {
    if (!readOnly) {
      setIsHovering(false);
      setHoverValue(null);
    }
  };

  // Handle mouse move
  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>, index: number) => {
    if (readOnly) return;

    if (precision === 0.5) {
      const { left, width } = event.currentTarget.getBoundingClientRect();
      const percent = (event.clientX - left) / width;
      
      if (percent <= 0.5) {
        setHoverValue(index + 0.5);
      } else {
        setHoverValue(index + 1);
      }
    } else {
      setHoverValue(index + 1);
    }
  };

  // Handle click
  const handleClick = (newValue: number) => {
    if (!readOnly && onChange) {
      onChange(newValue);
    }
  };

  // Get icon for a specific index
  const getIcon = (index: number) => {
    const displayValue = isHovering && hoverValue !== null ? hoverValue : value;
    
    if (displayValue >= index + 1) {
      return filledIcon || defaultFilledIcon;
    } else if (precision === 0.5 && displayValue === index + 0.5) {
      return halfFilledIcon || defaultHalfFilledIcon;
    } else {
      return emptyIcon || defaultEmptyIcon;
    }
  };

  // Get container classes based on label position
  const getContainerClasses = () => {
    switch (labelPosition) {
      case 'top':
        return 'flex flex-col items-start';
      case 'right':
        return 'flex flex-row-reverse items-center';
      case 'bottom':
        return 'flex flex-col-reverse items-start';
      case 'left':
      default:
        return 'flex flex-row items-center';
    }
  };

  // Get label classes based on position
  const getLabelClasses = () => {
    switch (labelPosition) {
      case 'top':
        return 'mb-1';
      case 'right':
        return 'ml-2';
      case 'bottom':
        return 'mt-1';
      case 'left':
      default:
        return 'mr-2';
    }
  };

  return (
    <div className={twMerge('inline-flex', getContainerClasses(), className)}>
      {label && <span className={getLabelClasses()}>{label}</span>}
      
      <div
        className="flex"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {Array.from({ length: max }).map((_, index) => (
          <div
            key={index}
            className={twMerge(
              'cursor-default',
              !readOnly && 'cursor-pointer',
              colorClasses[color],
              isHovering && hoverValue !== null && hoverValue >= index + 1 && hoverColor
            )}
            onMouseMove={(e) => handleMouseMove(e, index)}
            onClick={() => handleClick(precision === 0.5 && hoverValue ? hoverValue : index + 1)}
            role={!readOnly ? 'button' : undefined}
            aria-label={!readOnly ? `Rate ${index + 1} out of ${max}` : undefined}
          >
            {getIcon(index)}
          </div>
        ))}
      </div>
      
      {showValue && (
        <span className={twMerge('ml-2 text-sm text-gray-600', valueClassName)}>
          {value.toFixed(precision === 0.5 ? 1 : 0)}
        </span>
      )}
    </div>
  );
};

export default Rating;
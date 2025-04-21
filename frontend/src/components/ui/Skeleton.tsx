import React from 'react';
import { twMerge } from 'tailwind-merge';

export interface SkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  width?: string | number;
  height?: string | number;
  className?: string;
  animation?: 'pulse' | 'wave' | 'none';
  count?: number;
  inline?: boolean;
}

const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  className,
  animation = 'pulse',
  count = 1,
  inline = false,
}) => {
  // Base styles
  const baseStyles = 'bg-gray-200 dark:bg-gray-700';
  
  // Animation styles
  const animationStyles = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer',
    none: '',
  };
  
  // Variant styles
  const variantStyles = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: '',
    rounded: 'rounded-lg',
  };
  
  // Default dimensions based on variant
  const getDefaultDimensions = () => {
    switch (variant) {
      case 'text':
        return { height: height || '1em', width: width || '100%' };
      case 'circular':
        return { height: height || '2.5rem', width: width || '2.5rem' };
      case 'rectangular':
      case 'rounded':
        return { height: height || '100px', width: width || '100%' };
      default:
        return { height: height || '1em', width: width || '100%' };
    }
  };
  
  const dimensions = getDefaultDimensions();
  
  // Combine all styles
  const skeletonStyles = twMerge(
    baseStyles,
    variantStyles[variant],
    animationStyles[animation],
    className
  );
  
  // Create multiple skeletons if count > 1
  const skeletons = Array.from({ length: count }, (_, index) => (
    <div
      key={index}
      className={twMerge(
        skeletonStyles,
        inline ? 'inline-block mr-2' : 'block',
        index < count - 1 && !inline ? 'mb-2' : ''
      )}
      style={{
        width: typeof dimensions.width === 'number' ? `${dimensions.width}px` : dimensions.width,
        height: typeof dimensions.height === 'number' ? `${dimensions.height}px` : dimensions.height,
      }}
      aria-hidden="true"
    />
  ));
  
  return <>{skeletons}</>;
};

// Predefined skeleton components for common use cases
export const TextSkeleton: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton variant="text" {...props} />
);

export const CircularSkeleton: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton variant="circular" {...props} />
);

export const RectangularSkeleton: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton variant="rectangular" {...props} />
);

export const RoundedSkeleton: React.FC<Omit<SkeletonProps, 'variant'>> = (props) => (
  <Skeleton variant="rounded" {...props} />
);

// Skeleton for product cards
export const ProductCardSkeleton: React.FC = () => (
  <div className="bg-white rounded-lg shadow-md overflow-hidden">
    <Skeleton variant="rectangular" height={200} />
    <div className="p-4">
      <Skeleton variant="text" height={24} className="mb-2" />
      <Skeleton variant="text" width="60%" height={16} className="mb-4" />
      <Skeleton variant="text" width="40%" height={20} />
    </div>
  </div>
);

// Skeleton for product details
export const ProductDetailSkeleton: React.FC = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
    <div>
      <Skeleton variant="rounded" height={400} className="mb-4" />
      <div className="grid grid-cols-4 gap-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} variant="rounded" height={80} />
        ))}
      </div>
    </div>
    <div>
      <Skeleton variant="text" height={32} className="mb-4" />
      <Skeleton variant="text" width="40%" height={24} className="mb-6" />
      <Skeleton variant="text" count={3} className="mb-6" />
      <Skeleton variant="rectangular" height={50} className="mb-4" />
      <Skeleton variant="rectangular" height={50} />
    </div>
  </div>
);

// Skeleton for user profile
export const ProfileSkeleton: React.FC = () => (
  <div className="space-y-6">
    <div className="flex items-center space-x-4">
      <Skeleton variant="circular" width={80} height={80} />
      <div className="flex-1">
        <Skeleton variant="text" height={28} className="mb-2" />
        <Skeleton variant="text" width="60%" height={16} />
      </div>
    </div>
    <div className="space-y-4">
      <Skeleton variant="text" height={20} />
      <Skeleton variant="text" height={20} />
      <Skeleton variant="text" height={20} />
    </div>
  </div>
);

export default Skeleton;
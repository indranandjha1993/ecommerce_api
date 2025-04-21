import React from 'react';
import { twMerge } from 'tailwind-merge';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'bordered' | 'elevated' | 'flat' | 'interactive';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  radius?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  bordered?: boolean;
  hoverEffect?: boolean;
  clickable?: boolean;
  fullWidth?: boolean;
  as?: React.ElementType;
}

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  action?: React.ReactNode;
}

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  divider?: boolean;
  align?: 'left' | 'center' | 'right' | 'between';
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      children,
      className,
      variant = 'default',
      padding = 'md',
      radius = 'lg',
      shadow = 'md',
      bordered = false,
      hoverEffect = false,
      clickable = false,
      fullWidth = true,
      as: Component = 'div',
      ...props
    },
    ref
  ) => {
    // Base classes
    const baseClasses = 'bg-white overflow-hidden';

    // Variant classes
    const variantClasses = {
      default: '',
      bordered: 'border border-neutral-200',
      elevated: 'shadow-md',
      flat: 'bg-neutral-50 border border-neutral-100',
      interactive: 'transition-all hover:shadow-md active:shadow-sm',
    };

    // Padding classes
    const paddingClasses = {
      none: 'p-0',
      sm: 'p-3',
      md: 'p-4',
      lg: 'p-6',
    };

    // Radius classes
    const radiusClasses = {
      none: 'rounded-none',
      sm: 'rounded-sm',
      md: 'rounded-md',
      lg: 'rounded-lg',
      xl: 'rounded-xl',
    };

    // Shadow classes
    const shadowClasses = {
      none: '',
      sm: 'shadow-sm',
      md: 'shadow-md',
      lg: 'shadow-lg',
      xl: 'shadow-xl',
    };

    // Additional classes
    const borderedClass = bordered && variant !== 'bordered' ? 'border border-neutral-200' : '';
    const hoverClass = hoverEffect ? 'transition-transform hover:-translate-y-1' : '';
    const clickableClass = clickable ? 'cursor-pointer' : '';
    const widthClass = fullWidth ? 'w-full' : '';

    // Combine all classes
    const classes = twMerge(
      baseClasses,
      variantClasses[variant],
      paddingClasses[padding],
      radiusClasses[radius],
      shadowClasses[shadow],
      borderedClass,
      hoverClass,
      clickableClass,
      widthClass,
      className
    );

    return (
      <Component ref={ref} className={classes} {...props}>
        {children}
      </Component>
    );
  }
);

Card.displayName = 'Card';

export const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ children, className, action, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={twMerge('flex items-start justify-between mb-4', className)}
        {...props}
      >
        <div>{children}</div>
        {action && <div>{action}</div>}
      </div>
    );
  }
);

CardHeader.displayName = 'CardHeader';

export const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ children, className, ...props }, ref) => {
  return (
    <div ref={ref} className={twMerge('', className)} {...props}>
      {children}
    </div>
  );
});

CardContent.displayName = 'CardContent';

export const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ children, className, divider = true, align = 'between', ...props }, ref) => {
    const alignClasses = {
      left: 'justify-start',
      center: 'justify-center',
      right: 'justify-end',
      between: 'justify-between',
    };

    return (
      <div
        ref={ref}
        className={twMerge(
          'flex items-center mt-4',
          divider && 'pt-4 border-t border-neutral-200',
          alignClasses[align],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardFooter.displayName = 'CardFooter';

export const CardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ children, className, ...props }, ref) => {
  return (
    <h3
      ref={ref}
      className={twMerge('text-lg font-semibold leading-none tracking-tight', className)}
      {...props}
    >
      {children}
    </h3>
  );
});

CardTitle.displayName = 'CardTitle';

export const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ children, className, ...props }, ref) => {
  return (
    <p
      ref={ref}
      className={twMerge('text-sm text-neutral-500 mt-1', className)}
      {...props}
    >
      {children}
    </p>
  );
});

CardDescription.displayName = 'CardDescription';

export const CardImage = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { src: string; alt: string; aspectRatio?: string }
>(({ className, src, alt, aspectRatio = 'aspect-video', ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={twMerge('-mx-4 -mt-4 mb-4 overflow-hidden', aspectRatio, className)}
      {...props}
    >
      <img src={src} alt={alt} className="w-full h-full object-cover" />
    </div>
  );
});

CardImage.displayName = 'CardImage';

export default Object.assign(Card, {
  Header: CardHeader,
  Content: CardContent,
  Footer: CardFooter,
  Title: CardTitle,
  Description: CardDescription,
  Image: CardImage,
});
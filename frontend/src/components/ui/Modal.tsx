import React, { Fragment, useEffect, useRef } from 'react';
import { twMerge } from 'tailwind-merge';
import Button from './Button';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closeOnClickOutside?: boolean;
  closeOnEsc?: boolean;
  showCloseButton?: boolean;
  className?: string;
  contentClassName?: string;
  centered?: boolean;
  preventScroll?: boolean;
  animation?: 'fade' | 'zoom' | 'slide-up' | 'slide-down' | 'slide-left' | 'slide-right';
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  size = 'md',
  closeOnClickOutside = true,
  closeOnEsc = true,
  showCloseButton = true,
  className,
  contentClassName,
  centered = false,
  preventScroll = true,
  animation = 'fade',
}) => {
  const modalRef = useRef<HTMLDivElement>(null);

  // Handle ESC key press
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (closeOnEsc && event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [closeOnEsc, isOpen, onClose]);

  // Handle scroll lock
  useEffect(() => {
    if (preventScroll) {
      if (isOpen) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen, preventScroll]);

  // Handle click outside
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (closeOnClickOutside && e.target === e.currentTarget) {
      onClose();
    }
  };

  // Size classes
  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-full mx-4',
  };

  // Animation classes
  const getAnimationClasses = () => {
    if (!isOpen) return 'opacity-0';

    const baseClasses = 'transition-all duration-300 ease-in-out';
    
    switch (animation) {
      case 'zoom':
        return isOpen 
          ? `${baseClasses} opacity-100 scale-100` 
          : `${baseClasses} opacity-0 scale-95`;
      case 'slide-up':
        return isOpen 
          ? `${baseClasses} opacity-100 translate-y-0` 
          : `${baseClasses} opacity-0 translate-y-4`;
      case 'slide-down':
        return isOpen 
          ? `${baseClasses} opacity-100 translate-y-0` 
          : `${baseClasses} opacity-0 -translate-y-4`;
      case 'slide-left':
        return isOpen 
          ? `${baseClasses} opacity-100 translate-x-0` 
          : `${baseClasses} opacity-0 translate-x-4`;
      case 'slide-right':
        return isOpen 
          ? `${baseClasses} opacity-100 translate-x-0` 
          : `${baseClasses} opacity-0 -translate-x-4`;
      case 'fade':
      default:
        return isOpen 
          ? `${baseClasses} opacity-100` 
          : `${baseClasses} opacity-0`;
    }
  };

  // Backdrop animation
  const backdropClasses = twMerge(
    'fixed inset-0 bg-black transition-opacity',
    isOpen ? 'bg-opacity-50' : 'bg-opacity-0 pointer-events-none'
  );

  if (!isOpen) {
    return null;
  }

  return (
    <Fragment>
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div 
          className={twMerge(
            'fixed inset-0 transition-opacity',
            backdropClasses
          )} 
          onClick={handleBackdropClick}
        />
        
        <div 
          className={twMerge(
            'flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0',
            centered ? 'items-center' : 'items-end sm:items-center'
          )}
        >
          <div
            ref={modalRef}
            className={twMerge(
              'relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl w-full',
              sizeClasses[size],
              getAnimationClasses(),
              className
            )}
          >
            {/* Header */}
            {(title || showCloseButton) && (
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
                {title && (
                  <h3 className="text-lg font-medium text-gray-900">{title}</h3>
                )}
                {showCloseButton && (
                  <button
                    type="button"
                    className="text-gray-400 hover:text-gray-500 focus:outline-none"
                    onClick={onClose}
                  >
                    <span className="sr-only">Close</span>
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
            )}
            
            {/* Content */}
            <div className={twMerge('px-6 py-4', contentClassName)}>
              {children}
            </div>
            
            {/* Footer */}
            {footer && (
              <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-2">
                {footer}
              </div>
            )}
          </div>
        </div>
      </div>
    </Fragment>
  );
};

// Predefined modal with confirm/cancel buttons
export interface ConfirmModalProps extends Omit<ModalProps, 'footer' | 'children'> {
  message: React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  confirmVariant?: 'primary' | 'danger' | 'success' | 'warning';
  onConfirm: () => void;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmVariant = 'primary',
  onConfirm,
  ...props
}) => {
  return (
    <Modal
      {...props}
      footer={
        <>
          <Button variant="outline" onClick={props.onClose}>
            {cancelText}
          </Button>
          <Button variant={confirmVariant} onClick={onConfirm}>
            {confirmText}
          </Button>
        </>
      }
    >
      <div className="py-2">{message}</div>
    </Modal>
  );
};

export default Modal;
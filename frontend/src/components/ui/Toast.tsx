import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { clearToast } from '../../store/slices/uiSlice';
import { twMerge } from 'tailwind-merge';

interface ToastProps {
  message: string;
  title?: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  action?: {
    label: string;
    onClick: () => void;
  };
  showProgress?: boolean;
}

const Toast: React.FC<ToastProps> = ({ 
  message, 
  title, 
  type, 
  duration = 5000, 
  position = 'bottom-right',
  action,
  showProgress = true
}) => {
  const dispatch = useDispatch();
  const [progress, setProgress] = useState(100);
  const [isPaused, setIsPaused] = useState(false);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (!isVisible) return;
    if (isPaused) return;
    
    const interval = setInterval(() => {
      setProgress((prev) => {
        const newProgress = prev - (100 / (duration / 100));
        return newProgress <= 0 ? 0 : newProgress;
      });
    }, 100);

    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => dispatch(clearToast()), 300); // Wait for exit animation
    }, duration);

    return () => {
      clearInterval(interval);
      clearTimeout(timer);
    };
  }, [dispatch, duration, isPaused, isVisible]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => dispatch(clearToast()), 300);
  };

  const handleMouseEnter = () => {
    setIsPaused(true);
  };

  const handleMouseLeave = () => {
    setIsPaused(false);
  };

  // Position classes
  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
  };

  // Type classes
  const typeClasses = {
    success: {
      bg: 'bg-green-50 border-green-500',
      text: 'text-green-800',
      progressBg: 'bg-green-500',
      icon: (
        <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      ),
    },
    error: {
      bg: 'bg-red-50 border-red-500',
      text: 'text-red-800',
      progressBg: 'bg-red-500',
      icon: (
        <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      ),
    },
    info: {
      bg: 'bg-blue-50 border-blue-500',
      text: 'text-blue-800',
      progressBg: 'bg-blue-500',
      icon: (
        <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    warning: {
      bg: 'bg-amber-50 border-amber-500',
      text: 'text-amber-800',
      progressBg: 'bg-amber-500',
      icon: (
        <svg className="w-6 h-6 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
    },
  };

  // Animation classes
  const getAnimationClasses = () => {
    const baseClasses = 'transition-all duration-300 ease-in-out';
    
    if (!isVisible) {
      if (position.includes('top')) return `${baseClasses} opacity-0 -translate-y-2`;
      if (position.includes('bottom')) return `${baseClasses} opacity-0 translate-y-2`;
      if (position.includes('left')) return `${baseClasses} opacity-0 -translate-x-2`;
      return `${baseClasses} opacity-0 translate-x-2`;
    }
    
    return `${baseClasses} opacity-100 translate-x-0 translate-y-0`;
  };

  return (
    <div 
      className={twMerge(
        'fixed z-50',
        positionClasses[position],
        getAnimationClasses()
      )}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div 
        className={twMerge(
          'max-w-md w-full shadow-lg rounded-lg overflow-hidden border-l-4',
          typeClasses[type].bg
        )}
      >
        <div className="p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0 mr-3">
              {typeClasses[type].icon}
            </div>
            <div className="flex-1">
              {title && (
                <p className={`text-sm font-bold ${typeClasses[type].text}`}>
                  {title}
                </p>
              )}
              <p className={`text-sm ${typeClasses[type].text} ${title ? 'mt-1' : ''}`}>
                {message}
              </p>
              
              {action && (
                <div className="mt-2">
                  <button
                    type="button"
                    onClick={action.onClick}
                    className={`text-sm font-medium focus:outline-none ${
                      type === 'success' ? 'text-green-600 hover:text-green-500' :
                      type === 'error' ? 'text-red-600 hover:text-red-500' :
                      type === 'warning' ? 'text-amber-600 hover:text-amber-500' :
                      'text-blue-600 hover:text-blue-500'
                    }`}
                  >
                    {action.label}
                  </button>
                </div>
              )}
            </div>
            <button
              onClick={handleClose}
              className="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-500 focus:outline-none"
              aria-label="Close"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        
        {showProgress && (
          <div className="h-1 w-full bg-gray-200">
            <div
              className={`h-full ${typeClasses[type].progressBg} transition-all duration-100 ease-linear`}
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Toast;
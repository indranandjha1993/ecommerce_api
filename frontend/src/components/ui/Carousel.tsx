import React, { useState, useEffect, useCallback, useRef } from 'react';
import { twMerge } from 'tailwind-merge';

export interface CarouselProps {
  children: React.ReactNode[];
  autoPlay?: boolean;
  interval?: number;
  showArrows?: boolean;
  showDots?: boolean;
  infiniteLoop?: boolean;
  className?: string;
  slideClassName?: string;
  arrowSize?: 'sm' | 'md' | 'lg';
  arrowPosition?: 'inside' | 'outside';
  dotPosition?: 'inside' | 'outside';
  dotStyle?: 'dots' | 'lines' | 'numbers';
  animation?: 'slide' | 'fade';
  animationDuration?: number;
  onSlideChange?: (index: number) => void;
  initialSlide?: number;
  pauseOnHover?: boolean;
  swipeable?: boolean;
  responsive?: boolean;
  aspectRatio?: '1:1' | '4:3' | '16:9' | '21:9';
}

const Carousel: React.FC<CarouselProps> = ({
  children,
  autoPlay = false,
  interval = 5000,
  showArrows = true,
  showDots = true,
  infiniteLoop = true,
  className,
  slideClassName,
  arrowSize = 'md',
  arrowPosition = 'inside',
  dotPosition = 'inside',
  dotStyle = 'dots',
  animation = 'slide',
  animationDuration = 500,
  onSlideChange,
  initialSlide = 0,
  pauseOnHover = true,
  swipeable = true,
  responsive = true,
  aspectRatio = '16:9',
}) => {
  const [currentSlide, setCurrentSlide] = useState(initialSlide);
  const [isPaused, setIsPaused] = useState(false);
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);
  const carouselRef = useRef<HTMLDivElement>(null);
  const slideCount = React.Children.count(children);

  // Calculate aspect ratio
  const getAspectRatio = () => {
    switch (aspectRatio) {
      case '1:1':
        return 'pb-[100%]';
      case '4:3':
        return 'pb-[75%]';
      case '16:9':
        return 'pb-[56.25%]';
      case '21:9':
        return 'pb-[42.85%]';
      default:
        return 'pb-[56.25%]';
    }
  };

  // Handle next slide
  const nextSlide = useCallback(() => {
    setCurrentSlide((prevSlide) => {
      const next = prevSlide + 1;
      return next >= slideCount ? (infiniteLoop ? 0 : prevSlide) : next;
    });
  }, [slideCount, infiniteLoop]);

  // Handle previous slide
  const prevSlide = useCallback(() => {
    setCurrentSlide((prevSlide) => {
      const prev = prevSlide - 1;
      return prev < 0 ? (infiniteLoop ? slideCount - 1 : prevSlide) : prev;
    });
  }, [slideCount, infiniteLoop]);

  // Go to specific slide
  const goToSlide = useCallback((index: number) => {
    setCurrentSlide(index);
  }, []);

  // Auto play functionality
  useEffect(() => {
    if (!autoPlay || isPaused) return;

    const interval_id = setInterval(() => {
      nextSlide();
    }, interval);

    return () => clearInterval(interval_id);
  }, [autoPlay, interval, isPaused, nextSlide]);

  // Call onSlideChange when slide changes
  useEffect(() => {
    if (onSlideChange) {
      onSlideChange(currentSlide);
    }
  }, [currentSlide, onSlideChange]);

  // Handle touch events for swipe
  const handleTouchStart = (e: React.TouchEvent) => {
    if (!swipeable) return;
    setTouchStart(e.targetTouches[0].clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!swipeable || touchStart === null) return;
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const handleTouchEnd = () => {
    if (!swipeable || touchStart === null || touchEnd === null) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > 50;
    const isRightSwipe = distance < -50;

    if (isLeftSwipe) {
      nextSlide();
    } else if (isRightSwipe) {
      prevSlide();
    }

    setTouchStart(null);
    setTouchEnd(null);
  };

  // Arrow size classes
  const arrowSizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  // Arrow position classes
  const arrowPositionClasses = {
    inside: 'absolute top-1/2 transform -translate-y-1/2',
    outside: 'absolute top-1/2 transform -translate-y-1/2',
  };

  // Dot position classes
  const dotPositionClasses = {
    inside: 'absolute bottom-4 left-0 right-0',
    outside: 'mt-4',
  };

  // Animation styles
  const getSlideStyles = (index: number) => {
    if (animation === 'fade') {
      return {
        opacity: currentSlide === index ? 1 : 0,
        transition: `opacity ${animationDuration}ms ease-in-out`,
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
      };
    }

    return {
      transform: `translateX(${(index - currentSlide) * 100}%)`,
      transition: `transform ${animationDuration}ms ease-in-out`,
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
    };
  };

  return (
    <div className={twMerge('relative', className)}>
      {/* Carousel container */}
      <div
        ref={carouselRef}
        className={twMerge(
          'relative overflow-hidden',
          responsive ? getAspectRatio() : 'h-full'
        )}
        onMouseEnter={() => pauseOnHover && setIsPaused(true)}
        onMouseLeave={() => pauseOnHover && setIsPaused(false)}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Slides */}
        {React.Children.map(children, (child, index) => (
          <div
            className={twMerge(
              'w-full h-full',
              animation === 'fade' ? 'transition-opacity' : 'transition-transform',
              slideClassName
            )}
            style={getSlideStyles(index)}
            aria-hidden={currentSlide !== index}
          >
            {child}
          </div>
        ))}

        {/* Navigation arrows */}
        {showArrows && slideCount > 1 && (
          <>
            <button
              type="button"
              className={twMerge(
                'bg-white/80 rounded-full flex items-center justify-center shadow-md text-gray-800 hover:bg-white focus:outline-none z-10',
                arrowSizeClasses[arrowSize],
                arrowPositionClasses[arrowPosition],
                arrowPosition === 'inside' ? 'left-4' : '-left-16'
              )}
              onClick={prevSlide}
              aria-label="Previous slide"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6">
                <polyline points="15 18 9 12 15 6"></polyline>
              </svg>
            </button>
            <button
              type="button"
              className={twMerge(
                'bg-white/80 rounded-full flex items-center justify-center shadow-md text-gray-800 hover:bg-white focus:outline-none z-10',
                arrowSizeClasses[arrowSize],
                arrowPositionClasses[arrowPosition],
                arrowPosition === 'inside' ? 'right-4' : '-right-16'
              )}
              onClick={nextSlide}
              aria-label="Next slide"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
            </button>
          </>
        )}
      </div>

      {/* Dots navigation */}
      {showDots && slideCount > 1 && (
        <div
          className={twMerge(
            'flex justify-center z-10',
            dotPositionClasses[dotPosition]
          )}
        >
          {Array.from({ length: slideCount }).map((_, index) => (
            <button
              key={index}
              type="button"
              onClick={() => goToSlide(index)}
              aria-label={`Go to slide ${index + 1}`}
              className={twMerge(
                'mx-1 focus:outline-none transition-all',
                dotStyle === 'dots'
                  ? `h-3 w-3 rounded-full ${
                      currentSlide === index
                        ? 'bg-blue-600 transform scale-110'
                        : 'bg-gray-300 hover:bg-gray-400'
                    }`
                  : dotStyle === 'lines'
                  ? `h-1 w-6 ${
                      currentSlide === index
                        ? 'bg-blue-600'
                        : 'bg-gray-300 hover:bg-gray-400'
                    }`
                  : `h-6 w-6 rounded-full flex items-center justify-center text-xs font-medium ${
                      currentSlide === index
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    }`
              )}
            >
              {dotStyle === 'numbers' && index + 1}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default Carousel;
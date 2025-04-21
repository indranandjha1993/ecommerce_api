import React from 'react';
import { twMerge } from 'tailwind-merge';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  className?: string;
  siblingCount?: number;
  showFirstLastButtons?: boolean;
  showPrevNextButtons?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'rounded' | 'outline' | 'minimal';
  pageClassName?: string;
  activeClassName?: string;
  disabledClassName?: string;
  showTotalItems?: boolean;
  totalItems?: number;
  itemsPerPage?: number;
  showItemsPerPageSelect?: boolean;
  itemsPerPageOptions?: number[];
  onItemsPerPageChange?: (itemsPerPage: number) => void;
  hideOnSinglePage?: boolean;
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  className,
  siblingCount = 1,
  showFirstLastButtons = false,
  showPrevNextButtons = true,
  size = 'md',
  variant = 'default',
  pageClassName,
  activeClassName,
  disabledClassName,
  showTotalItems = false,
  totalItems = 0,
  itemsPerPage = 10,
  showItemsPerPageSelect = false,
  itemsPerPageOptions = [10, 25, 50, 100],
  onItemsPerPageChange,
  hideOnSinglePage = true,
}) => {
  // Don't render pagination if there's only one page and hideOnSinglePage is true
  if (totalPages <= 1 && hideOnSinglePage) {
    return null;
  }

  // Generate page numbers to display
  const getPageNumbers = () => {
    const totalNumbers = siblingCount * 2 + 3; // siblings + current + first + last
    const totalButtons = Math.min(totalNumbers, totalPages);

    if (totalPages <= totalButtons) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const leftSiblingIndex = Math.max(currentPage - siblingCount, 1);
    const rightSiblingIndex = Math.min(currentPage + siblingCount, totalPages);

    const shouldShowLeftDots = leftSiblingIndex > 2;
    const shouldShowRightDots = rightSiblingIndex < totalPages - 1;

    if (!shouldShowLeftDots && shouldShowRightDots) {
      const leftItemCount = 1 + 2 * siblingCount;
      return [
        ...Array.from({ length: leftItemCount }, (_, i) => i + 1),
        '...',
        totalPages,
      ];
    }

    if (shouldShowLeftDots && !shouldShowRightDots) {
      const rightItemCount = 1 + 2 * siblingCount;
      return [
        1,
        '...',
        ...Array.from(
          { length: rightItemCount },
          (_, i) => totalPages - rightItemCount + i + 1
        ),
      ];
    }

    if (shouldShowLeftDots && shouldShowRightDots) {
      return [
        1,
        '...',
        ...Array.from(
          { length: rightSiblingIndex - leftSiblingIndex + 1 },
          (_, i) => leftSiblingIndex + i
        ),
        '...',
        totalPages,
      ];
    }

    return [];
  };

  // Size classes
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base',
  };

  // Variant classes
  const getVariantClasses = (isActive: boolean) => {
    switch (variant) {
      case 'rounded':
        return isActive
          ? 'text-white bg-blue-600 border border-blue-600 rounded-full'
          : 'text-gray-500 bg-white border border-gray-300 rounded-full hover:bg-gray-100 hover:text-gray-700';
      case 'outline':
        return isActive
          ? 'text-blue-600 bg-white border-2 border-blue-600'
          : 'text-gray-500 bg-white border border-gray-300 hover:border-blue-600 hover:text-blue-600';
      case 'minimal':
        return isActive
          ? 'text-blue-600 font-medium'
          : 'text-gray-500 hover:text-blue-600';
      default:
        return isActive
          ? 'text-white bg-blue-600 border border-blue-600'
          : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-100 hover:text-gray-700';
    }
  };

  // Get button classes based on variant and size
  const getButtonClasses = (isActive: boolean, isDisabled: boolean = false) => {
    return twMerge(
      'leading-tight focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-opacity-50 transition-colors',
      sizeClasses[size],
      isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
      getVariantClasses(isActive),
      isActive && activeClassName,
      isDisabled && disabledClassName,
      pageClassName
    );
  };

  // Get first/last button classes
  const getFirstLastButtonClasses = (isDisabled: boolean) => {
    return twMerge(
      'leading-tight focus:outline-none focus:ring-2 focus:ring-blue-300 focus:ring-opacity-50 transition-colors',
      sizeClasses[size],
      isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
      'text-gray-500 bg-white border border-gray-300 hover:bg-gray-100 hover:text-gray-700',
      variant === 'rounded' && 'rounded-full',
      isDisabled && disabledClassName,
      pageClassName
    );
  };

  // Handle items per page change
  const handleItemsPerPageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (onItemsPerPageChange) {
      onItemsPerPageChange(Number(e.target.value));
    }
  };

  // Calculate item range
  const getItemRange = () => {
    const start = (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(currentPage * itemsPerPage, totalItems);
    return `${start}-${end} of ${totalItems}`;
  };

  const pageNumbers = getPageNumbers();

  return (
    <div className={twMerge('flex flex-wrap items-center justify-between gap-4', className)}>
      {/* Items per page selector */}
      {showItemsPerPageSelect && onItemsPerPageChange && (
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Items per page:</span>
          <select
            value={itemsPerPage}
            onChange={handleItemsPerPageChange}
            className="h-8 rounded border border-gray-300 bg-white px-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {itemsPerPageOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Item count */}
      {showTotalItems && (
        <div className="text-sm text-gray-600">
          {getItemRange()}
        </div>
      )}

      {/* Pagination */}
      <nav className="flex justify-center" aria-label="Pagination">
        <ul className={`inline-flex items-center ${variant !== 'minimal' ? '-space-x-px' : 'space-x-1'}`}>
          {/* First page button */}
          {showFirstLastButtons && (
            <li>
              <button
                onClick={() => onPageChange(1)}
                disabled={currentPage === 1}
                className={twMerge(
                  getFirstLastButtonClasses(currentPage === 1),
                  variant === 'default' && 'rounded-l-lg'
                )}
                aria-label="Go to first page"
              >
                <span className="sr-only">First</span>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                  <path fillRule="evenodd" d="M15.79 14.77a.75.75 0 01-1.06.02l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 111.04 1.08L11.832 10l3.938 3.71a.75.75 0 01.02 1.06zm-6 0a.75.75 0 01-1.06.02l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 111.04 1.08L5.832 10l3.938 3.71a.75.75 0 01.02 1.06z" clipRule="evenodd" />
                </svg>
              </button>
            </li>
          )}

          {/* Previous button */}
          {showPrevNextButtons && (
            <li>
              <button
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className={twMerge(
                  getFirstLastButtonClasses(currentPage === 1),
                  !showFirstLastButtons && variant === 'default' && 'rounded-l-lg'
                )}
                aria-label="Previous page"
              >
                <span className="sr-only">Previous</span>
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fillRule="evenodd"
                    d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </li>
          )}
          
          {/* Page numbers */}
          {pageNumbers.map((page, index) => (
            <li key={index}>
              {page === '...' ? (
                <span className={twMerge(
                  'px-3 py-2 leading-tight text-gray-500 bg-white',
                  variant !== 'minimal' && 'border border-gray-300'
                )}>
                  ...
                </span>
              ) : (
                <button
                  onClick={() => onPageChange(page as number)}
                  className={getButtonClasses(currentPage === page)}
                  aria-current={currentPage === page ? 'page' : undefined}
                >
                  {page}
                </button>
              )}
            </li>
          ))}
          
          {/* Next button */}
          {showPrevNextButtons && (
            <li>
              <button
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={twMerge(
                  getFirstLastButtonClasses(currentPage === totalPages),
                  !showFirstLastButtons && variant === 'default' && 'rounded-r-lg'
                )}
                aria-label="Next page"
              >
                <span className="sr-only">Next</span>
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    fillRule="evenodd"
                    d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </li>
          )}

          {/* Last page button */}
          {showFirstLastButtons && (
            <li>
              <button
                onClick={() => onPageChange(totalPages)}
                disabled={currentPage === totalPages}
                className={twMerge(
                  getFirstLastButtonClasses(currentPage === totalPages),
                  variant === 'default' && 'rounded-r-lg'
                )}
                aria-label="Go to last page"
              >
                <span className="sr-only">Last</span>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                  <path fillRule="evenodd" d="M4.21 14.77a.75.75 0 01.02-1.06L8.168 10 4.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02zm6 0a.75.75 0 01.02-1.06L14.168 10 10.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clipRule="evenodd" />
                </svg>
              </button>
            </li>
          )}
        </ul>
      </nav>
    </div>
  );
};

export default Pagination;
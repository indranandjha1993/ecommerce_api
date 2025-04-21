import React, { useState, useEffect } from 'react';
import { twMerge } from 'tailwind-merge';

export interface TabItem {
  id: string;
  label: React.ReactNode;
  content: React.ReactNode;
  disabled?: boolean;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
}

export interface TabsProps {
  items: TabItem[];
  defaultActiveTab?: string;
  onChange?: (tabId: string) => void;
  variant?: 'default' | 'pills' | 'underline' | 'enclosed' | 'vertical';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  className?: string;
  tabClassName?: string;
  contentClassName?: string;
  animated?: boolean;
  centered?: boolean;
  scrollable?: boolean;
  iconPosition?: 'left' | 'top';
}

const Tabs: React.FC<TabsProps> = ({
  items,
  defaultActiveTab,
  onChange,
  variant = 'default',
  size = 'md',
  fullWidth = false,
  className,
  tabClassName,
  contentClassName,
  animated = true,
  centered = false,
  scrollable = false,
  iconPosition = 'left',
}) => {
  const [activeTab, setActiveTab] = useState<string>(
    defaultActiveTab || (items.length > 0 ? items[0].id : '')
  );

  useEffect(() => {
    if (defaultActiveTab) {
      setActiveTab(defaultActiveTab);
    }
  }, [defaultActiveTab]);

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId);
    if (onChange) {
      onChange(tabId);
    }
  };

  // Size classes
  const sizeClasses = {
    sm: 'text-sm py-1 px-2',
    md: 'text-base py-2 px-4',
    lg: 'text-lg py-3 px-6',
  };

  // Variant classes
  const getVariantClasses = (isActive: boolean, isDisabled: boolean) => {
    if (isDisabled) {
      return 'text-gray-400 cursor-not-allowed';
    }

    switch (variant) {
      case 'pills':
        return isActive
          ? 'bg-blue-600 text-white rounded-full shadow-sm'
          : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-full';
      case 'underline':
        return isActive
          ? 'text-blue-600 border-b-2 border-blue-600'
          : 'text-gray-600 hover:text-gray-800 border-b-2 border-transparent hover:border-gray-300';
      case 'enclosed':
        return isActive
          ? 'bg-white text-blue-600 border-t border-l border-r rounded-t-lg -mb-px'
          : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-t-lg';
      case 'vertical':
        return isActive
          ? 'bg-blue-50 text-blue-600 border-l-4 border-blue-600'
          : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50 border-l-4 border-transparent';
      default:
        return isActive
          ? 'text-blue-600 font-medium'
          : 'text-gray-600 hover:text-gray-800';
    }
  };

  // Tab list classes
  const tabListClasses = twMerge(
    'flex',
    variant === 'vertical' ? 'flex-col' : 'flex-row',
    variant === 'enclosed' ? 'border-b' : '',
    variant === 'underline' ? 'border-b' : '',
    scrollable && variant !== 'vertical' ? 'overflow-x-auto' : '',
    centered && variant !== 'vertical' ? 'justify-center' : '',
    fullWidth && variant !== 'vertical' ? 'w-full' : '',
    className
  );

  // Tab classes
  const getTabClasses = (item: TabItem) => {
    const isActive = activeTab === item.id;
    const isDisabled = !!item.disabled;

    return twMerge(
      'flex items-center transition-all duration-200 focus:outline-none whitespace-nowrap',
      sizeClasses[size],
      getVariantClasses(isActive, isDisabled),
      fullWidth && variant !== 'vertical' ? 'flex-1 justify-center' : '',
      iconPosition === 'top' ? 'flex-col' : '',
      tabClassName
    );
  };

  // Content animation classes
  const contentAnimationClasses = animated
    ? 'transition-opacity duration-300 ease-in-out'
    : '';

  return (
    <div className={variant === 'vertical' ? 'flex flex-row' : 'flex flex-col'}>
      {/* Tab list */}
      <div
        className={tabListClasses}
        role="tablist"
        aria-orientation={variant === 'vertical' ? 'vertical' : 'horizontal'}
      >
        {items.map((item) => (
          <button
            key={item.id}
            role="tab"
            aria-selected={activeTab === item.id}
            aria-controls={`panel-${item.id}`}
            id={`tab-${item.id}`}
            className={getTabClasses(item)}
            onClick={() => !item.disabled && handleTabClick(item.id)}
            disabled={item.disabled}
            tabIndex={activeTab === item.id ? 0 : -1}
          >
            {item.icon && iconPosition === 'left' && (
              <span className="mr-2">{item.icon}</span>
            )}
            {item.icon && iconPosition === 'top' && (
              <span className="mb-1">{item.icon}</span>
            )}
            <span>{item.label}</span>
            {item.badge && <span className="ml-2">{item.badge}</span>}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div
        className={twMerge(
          'mt-4',
          variant === 'vertical' ? 'flex-1 ml-4' : '',
          contentClassName
        )}
      >
        {items.map((item) => (
          <div
            key={item.id}
            role="tabpanel"
            id={`panel-${item.id}`}
            aria-labelledby={`tab-${item.id}`}
            className={twMerge(
              contentAnimationClasses,
              activeTab === item.id ? 'opacity-100' : 'hidden opacity-0'
            )}
            tabIndex={0}
          >
            {item.content}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Tabs;
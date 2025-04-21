import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useUI } from '../../hooks/useUI';
import { useCategories } from '../../contexts/CategoryContext';
import { useBrands } from '../../contexts/BrandContext';
import { twMerge } from 'tailwind-merge';

interface SidebarSectionProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

const SidebarSection: React.FC<SidebarSectionProps> = ({ title, children, defaultOpen = true }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  return (
    <div className="border-b border-gray-200 py-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full text-left"
      >
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{title}</h3>
        <svg 
          className={`h-5 w-5 text-gray-400 transition-transform duration-200 ${isOpen ? 'transform rotate-180' : ''}`} 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      <div className={`mt-3 space-y-1 ${isOpen ? 'block' : 'hidden'}`}>
        {children}
      </div>
    </div>
  );
};

const Sidebar: React.FC = () => {
  const location = useLocation();
  const { sidebarOpen, setSidebarOpen } = useUI();
  const { topCategories, fetchTopCategories } = useCategories();
  const { topBrands, fetchTopBrands } = useBrands();
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    fetchTopCategories(6);
    fetchTopBrands(6);
    
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, [fetchTopCategories, fetchTopBrands]);

  // Close sidebar on mobile when route changes
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  }, [location.pathname, setSidebarOpen, isMobile]);

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  // Navigation items
  const mainNavItems = [
    { path: '/', label: 'Home' },
    { path: '/products', label: 'All Products' },
    { path: '/products/new', label: 'New Arrivals' },
    { path: '/products/featured', label: 'Featured Products' },
    { path: '/sale', label: 'Sale & Clearance' },
  ];
  
  const customerServiceItems = [
    { path: '/contact', label: 'Contact Us' },
    { path: '/faq', label: 'FAQ' },
    { path: '/shipping', label: 'Shipping & Returns' },
    { path: '/terms', label: 'Terms & Conditions' },
    { path: '/privacy', label: 'Privacy Policy' },
  ];

  return (
    <aside 
      className={twMerge(
        'w-72 shrink-0 bg-white h-full overflow-y-auto transition-all duration-300 ease-in-out',
        isMobile 
          ? 'fixed top-0 bottom-0 left-0 z-40 shadow-xl transform' + (sidebarOpen ? ' translate-x-0' : ' -translate-x-full')
          : 'sticky top-[calc(4rem+2.5rem)] h-[calc(100vh-4rem-2.5rem)] border-r border-gray-200'
      )}
    >
      {/* Mobile header */}
      {isMobile && (
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-5 flex items-center justify-between">
          <div className="flex items-center">
            <svg className="h-8 w-8 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
            </svg>
            <span className="ml-2 text-xl font-bold text-gray-900">ShopSmart</span>
          </div>
          <button 
            onClick={() => setSidebarOpen(false)}
            className="text-gray-500 hover:text-gray-700 focus:outline-none"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      <div className="px-4 py-2 overflow-y-auto">
        {/* Main Navigation */}
        <SidebarSection title="Shop" defaultOpen={true}>
          {mainNavItems.map((item) => (
            <Link 
              key={item.path}
              to={item.path} 
              className={twMerge(
                'flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors',
                isActive(item.path) 
                  ? 'bg-blue-50 text-blue-700' 
                  : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'
              )}
              onClick={() => isMobile && setSidebarOpen(false)}
            >
              {item.label}
            </Link>
          ))}
        </SidebarSection>

        {/* Categories */}
        <SidebarSection title="Categories" defaultOpen={true}>
          {topCategories.length > 0 ? (
            <>
              {topCategories.map(category => (
                <Link 
                  key={category.id}
                  to={`/categories/${category.slug}`} 
                  className={twMerge(
                    'flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive(`/categories/${category.slug}`) 
                      ? 'bg-blue-50 text-blue-700' 
                      : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'
                  )}
                  onClick={() => isMobile && setSidebarOpen(false)}
                >
                  {category.name}
                </Link>
              ))}
              <Link 
                to="/categories" 
                className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-blue-600 hover:bg-gray-50"
                onClick={() => isMobile && setSidebarOpen(false)}
              >
                View All Categories
                <svg className="ml-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </>
          ) : (
            <div className="px-3 py-2 text-sm text-gray-500">Loading categories...</div>
          )}
        </SidebarSection>

        {/* Brands */}
        <SidebarSection title="Popular Brands" defaultOpen={false}>
          {topBrands.length > 0 ? (
            <>
              {topBrands.map(brand => (
                <Link 
                  key={brand.id}
                  to={`/brands/${brand.slug}`} 
                  className={twMerge(
                    'flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    isActive(`/brands/${brand.slug}`) 
                      ? 'bg-blue-50 text-blue-700' 
                      : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'
                  )}
                  onClick={() => isMobile && setSidebarOpen(false)}
                >
                  {brand.name}
                </Link>
              ))}
              <Link 
                to="/brands" 
                className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-blue-600 hover:bg-gray-50"
                onClick={() => isMobile && setSidebarOpen(false)}
              >
                View All Brands
                <svg className="ml-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </>
          ) : (
            <div className="px-3 py-2 text-sm text-gray-500">Loading brands...</div>
          )}
        </SidebarSection>

        {/* Customer Service */}
        <SidebarSection title="Customer Service" defaultOpen={false}>
          {customerServiceItems.map((item) => (
            <Link 
              key={item.path}
              to={item.path} 
              className={twMerge(
                'flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors',
                isActive(item.path) 
                  ? 'bg-blue-50 text-blue-700' 
                  : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'
              )}
              onClick={() => isMobile && setSidebarOpen(false)}
            >
              {item.label}
            </Link>
          ))}
        </SidebarSection>
        
        {/* Mobile account links */}
        {isMobile && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <Link 
              to="/account" 
              className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-blue-600"
              onClick={() => setSidebarOpen(false)}
            >
              <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              My Account
            </Link>
            <Link 
              to="/orders" 
              className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-blue-600"
              onClick={() => setSidebarOpen(false)}
            >
              <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
              </svg>
              My Orders
            </Link>
            <Link 
              to="/wishlist" 
              className="flex items-center px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-blue-600"
              onClick={() => setSidebarOpen(false)}
            >
              <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              My Wishlist
            </Link>
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;
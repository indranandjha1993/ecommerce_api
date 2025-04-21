import React, { useState, useEffect, useCallback } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';
import CartDrawer from '../cart/CartDrawer';
import Notifications from '../ui/Notifications';
import CategoryMenu from './CategoryMenu';
import LoadingSpinner from '../ui/LoadingSpinner';

// Create a context for UI state
export const UIContext = React.createContext<{
  cartDrawerOpen: boolean;
  setCartDrawerOpen: React.Dispatch<React.SetStateAction<boolean>>;
  categoryMenuOpen: boolean;
  setCategoryMenuOpen: React.Dispatch<React.SetStateAction<boolean>>;
  filterDrawerOpen: boolean;
  setFilterDrawerOpen: React.Dispatch<React.SetStateAction<boolean>>;
  toggleCategoryMenu: () => void;
  toggleCartDrawer: () => void;
  toggleFilterDrawer: () => void;
  isMobileView: boolean;
}>({
  cartDrawerOpen: false,
  setCartDrawerOpen: () => {},
  categoryMenuOpen: false,
  setCategoryMenuOpen: () => {},
  filterDrawerOpen: false,
  setFilterDrawerOpen: () => {},
  toggleCategoryMenu: () => {},
  toggleCartDrawer: () => {},
  toggleFilterDrawer: () => {},
  isMobileView: false,
});

const MainLayout: React.FC = () => {
  const location = useLocation();
  const [cartDrawerOpen, setCartDrawerOpen] = useState(false);
  const [categoryMenuOpen, setCategoryMenuOpen] = useState(false);
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);
  const [pageLoading, setPageLoading] = useState(false);
  const [isMobileView, setIsMobileView] = useState(false);

  // Check if we're on mobile view
  const checkMobileView = useCallback(() => {
    setIsMobileView(window.innerWidth < 1024);
  }, []);

  // Initialize mobile view check
  useEffect(() => {
    checkMobileView();
    window.addEventListener('resize', checkMobileView);
    return () => window.removeEventListener('resize', checkMobileView);
  }, [checkMobileView]);

  // Toggle functions
  const toggleCategoryMenu = useCallback(() => {
    setCategoryMenuOpen(prev => !prev);
  }, []);
  
  const toggleCartDrawer = useCallback(() => {
    setCartDrawerOpen(prev => !prev);
  }, []);
  
  const toggleFilterDrawer = useCallback(() => {
    setFilterDrawerOpen(prev => !prev);
  }, []);

  // Close category menu and drawers on route change
  useEffect(() => {
    setCategoryMenuOpen(false);
    setFilterDrawerOpen(false);
    
    // Simulate page loading
    setPageLoading(true);
    const timer = setTimeout(() => {
      setPageLoading(false);
    }, 300);
    
    // Scroll to top on route change
    window.scrollTo(0, 0);
    
    return () => clearTimeout(timer);
  }, [location.pathname]);

  // Prevent body scroll when drawers are open
  useEffect(() => {
    if (cartDrawerOpen || categoryMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
    
    return () => {
      document.body.style.overflow = 'auto';
    };
  }, [cartDrawerOpen, categoryMenuOpen]);

  return (
    <UIContext.Provider value={{ 
      cartDrawerOpen, 
      setCartDrawerOpen,
      categoryMenuOpen,
      setCategoryMenuOpen,
      filterDrawerOpen,
      setFilterDrawerOpen,
      toggleCategoryMenu,
      toggleCartDrawer,
      toggleFilterDrawer,
      isMobileView
    }}>
      <div className="flex flex-col min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
        {/* Fixed header */}
        <div className="sticky top-0 z-50">
          <Header />
        </div>
        
        {/* Main content with page transitions */}
        <main className="container mx-auto px-4 py-4 relative">
          {pageLoading ? (
            <div className="flex justify-center items-center py-20">
              <LoadingSpinner size="md" color="primary" variant="spinner" />
            </div>
          ) : (
            <div className="mx-auto w-full animate-fadeIn">
              <Outlet />
            </div>
          )}
          
          {/* Decorative elements - only visible on desktop and positioned properly */}
          <div className="hidden lg:block fixed bottom-0 left-0 w-96 h-96 bg-indigo-50 rounded-full -z-10 opacity-70 blur-3xl transform -translate-x-1/3 translate-y-1/3"></div>
          
          {/* Additional decorative elements - only visible on desktop */}
          <div className="hidden lg:block fixed top-1/3 left-1/4 w-32 h-32 bg-blue-100 rounded-full -z-10 opacity-50 blur-2xl"></div>
          <div className="hidden lg:block fixed bottom-1/4 right-1/4 w-48 h-48 bg-indigo-100 rounded-full -z-10 opacity-50 blur-2xl"></div>
          
          {/* Animated dots - only visible on desktop */}
          <div className="hidden lg:block fixed top-1/2 left-16 w-3 h-3 bg-blue-400 rounded-full -z-10 opacity-70 animate-pulse"></div>
          <div className="hidden lg:block fixed bottom-1/3 right-24 w-2 h-2 bg-indigo-500 rounded-full -z-10 opacity-70 animate-pulse animation-delay-300"></div>
          <div className="hidden lg:block fixed top-1/4 right-1/3 w-4 h-4 bg-blue-300 rounded-full -z-10 opacity-50 animate-pulse animation-delay-500"></div>
        </main>
        
        {/* Footer with full width */}
        <div className="w-full mt-auto">
          <Footer />
        </div>
        
        {/* Cart drawer with improved animation */}
        {cartDrawerOpen && (
          <>
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 z-40 backdrop-blur-sm transition-opacity duration-300 animate-fade-in"
              onClick={() => setCartDrawerOpen(false)}
            />
            <CartDrawer onClose={() => setCartDrawerOpen(false)} />
          </>
        )}
        
        {/* Category menu overlay with improved animation - only on mobile */}
        {categoryMenuOpen && (
          <>
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm transition-opacity duration-300 animate-fadeIn"
              onClick={() => setCategoryMenuOpen(false)}
              style={{ zIndex: 9998 }}
            />
            <CategoryMenu onClose={() => setCategoryMenuOpen(false)} />
          </>
        )}
        
        {/* Notifications with improved positioning */}
        <div className="fixed bottom-4 right-4 z-50">
          <Notifications />
        </div>
      </div>
    </UIContext.Provider>
  );
};

export default MainLayout;
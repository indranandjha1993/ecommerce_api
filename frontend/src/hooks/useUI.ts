import { useContext } from 'react';
import { UIContext } from '../components/layout/MainLayout';

export const useUI = () => {
  const context = useContext(UIContext);
  
  if (context === undefined) {
    throw new Error('useUI must be used within a UIProvider');
  }
  
  const { 
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
  } = context;
  
  return {
    // State
    cartDrawerOpen,
    categoryMenuOpen,
    filterDrawerOpen,
    isMobileView,
    
    // Setters
    setCartDrawerOpen,
    setCategoryMenuOpen,
    setFilterDrawerOpen,
    
    // Toggle functions
    toggleCategoryMenu,
    toggleCartDrawer,
    toggleFilterDrawer
  };
};
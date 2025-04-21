import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useCart } from '../../contexts/CartContext';
import { useUI } from '../../hooks/useUI';
import Button from '../ui/Button';
import Input from '../ui/Input';
import { twMerge } from 'tailwind-merge';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();
  const { items, refreshCart, itemCount } = useCart();
  const { toggleCategoryMenu, cartDrawerOpen, setCartDrawerOpen, categoryMenuOpen, setCategoryMenuOpen, isMobileView } = useUI();

  const [searchQuery, setSearchQuery] = useState('');
  const [scrolled, setScrolled] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const userMenuRef = useRef<HTMLDivElement>(null);

  // Fetch cart on component mount if authenticated
  useEffect(() => {
    if (isAuthenticated) {
      refreshCart();
    }
  }, [isAuthenticated, refreshCart]);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setUserMenuOpen(false);
  }, [location.pathname]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
      setSearchOpen(false);
      setSearchQuery('');
    }
  };

  const toggleSearch = () => {
    setSearchOpen(!searchOpen);
  };

  const toggleUserMenu = () => {
    setUserMenuOpen(!userMenuOpen);
  };

  // UI toggles
  const handleToggleCartDrawer = () => {
    setCartDrawerOpen(!cartDrawerOpen);
  };

  const handleLogout = () => {
    logout();
    setUserMenuOpen(false);
    navigate('/');
  };

  return (
    <header
      className={twMerge(
        'fixed top-0 left-0 right-0 z-40 transition-all duration-300',
        scrolled ? 'bg-blue-600 shadow-md' : 'bg-blue-600'
      )}
    >
      {/* Announcement bar */}
      <div className="bg-blue-700 text-white py-1.5 text-center text-xs md:text-sm font-medium w-full">
        <div className="max-w-7xl mx-auto px-4">
          Free shipping on orders over $50 | Use code WELCOME10 for 10% off your first order
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 w-full">
        <div className="flex items-center justify-between h-14 md:h-16">
          {/* Logo */}
          <div className="flex-shrink-0 flex items-center">
            <Link to="/" className="flex items-center">
              <svg className="h-7 w-7 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
              </svg>
              <span className="ml-2 text-xl font-bold text-white italic">ShopSmart</span>
            </Link>
          </div>

          {/* Desktop Navigation - only visible on desktop */}
          {!isMobileView && (
            <div className="hidden lg:flex items-center space-x-8 ml-8">
              <Link to="/" className="text-white hover:text-blue-100 font-medium">Home</Link>
              
              {/* Desktop Categories Dropdown */}
              <div className="relative group">
                <button className="flex items-center text-white hover:text-blue-100 font-medium focus:outline-none">
                  <span>Categories</span>
                  <svg className="ml-1 h-4 w-4 transition-transform group-hover:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                {/* Dropdown Menu */}
                <div className="absolute left-0 mt-2 w-56 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform origin-top-left z-50">
                  <div className="bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 py-1">
                    <Link to="/categories/electronics" className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700">
                      Electronics
                    </Link>
                    <Link to="/categories/fashion" className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700">
                      Fashion
                    </Link>
                    <Link to="/categories/home-kitchen" className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700">
                      Home & Kitchen
                    </Link>
                    <Link to="/categories/beauty-personal-care" className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700">
                      Beauty & Personal Care
                    </Link>
                    <Link to="/categories" className="block px-4 py-2 text-sm font-medium text-blue-600 border-t border-gray-100 mt-1 pt-1">
                      View All Categories
                    </Link>
                  </div>
                </div>
              </div>
              
              <Link to="/deals" className="text-white hover:text-blue-100 font-medium">Deals</Link>
              <Link to="/new-arrivals" className="text-white hover:text-blue-100 font-medium">New Arrivals</Link>
              <Link to="/contact" className="text-white hover:text-blue-100 font-medium">Contact</Link>
            </div>
          )}

          {/* Search bar */}
          <div className="hidden md:flex flex-1 mx-8 sm:px-6 lg:px-8">
            <div className="relative w-full max-w-xl">
              <input
                type="text"
                placeholder="Search for products, brands and more"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && searchQuery.trim() && navigate(`/search?q=${encodeURIComponent(searchQuery)}`)}
                className="w-full py-2 pl-4 pr-10 rounded-sm bg-white text-gray-800 focus:outline-none"
              />
              <button
                onClick={() => searchQuery.trim() && navigate(`/search?q=${encodeURIComponent(searchQuery)}`)}
                className="absolute right-0 top-0 h-full px-3 text-blue-600 hover:text-blue-800"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </div>

          {/* Right side icons */}
          <div className="flex items-center space-x-4">
            {/* Mobile search button */}
              <button
                onClick={toggleSearch}
                className="md:hidden p-2 text-white hover:text-blue-100 transition-colors"
                aria-label="Search"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </button>
            {/* Mobile menu toggle button - only visible on mobile */}
            {isMobileView && (
              <button
                onClick={toggleCategoryMenu}
                className="p-2 text-white hover:text-blue-100 focus:outline-none"
                aria-label="Toggle category menu"
              >
                <div className="flex flex-col items-center">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 6h16M4 12h16M4 18h16"
                    />
                  </svg>
                  <span className="text-xs mt-0.5">Menu</span>
                </div>
              </button>
            )}
            


            {/* User menu - only visible on desktop */}
            {!isMobileView && (isAuthenticated ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={toggleUserMenu}
                  className="flex flex-col items-center p-2 text-white hover:text-blue-100 transition-colors"
                  aria-label="User menu"
                  aria-expanded={userMenuOpen}
                >
                  <div className="h-5 w-5 text-white">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <span className="text-xs mt-0.5 hidden sm:block">
                    {user?.name?.split(' ')[0] || 'Account'}
                  </span>
                </button>

                {/* Dropdown menu */}
                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg py-2 z-50 border border-gray-200">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-900">{user?.name || 'User'}</p>
                      <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                    </div>
                    <Link
                      to="/account"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      My Account
                    </Link>
                    <Link
                      to="/orders"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                      </svg>
                      Orders
                    </Link>
                    <Link
                      to="/wishlist"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                      Wishlist
                    </Link>
                    <div className="border-t border-gray-100 my-1"></div>
                    <button
                      onClick={handleLogout}
                      className="flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                    >
                      <svg className="mr-3 h-5 w-5 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Logout
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center p-2">
                <Link to="/login" className="text-white hover:text-blue-100">
                  <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </Link>
                <span className="text-xs mt-0.5 hidden sm:block text-white">Login</span>
              </div>
            ))}

            {/* Cart button - only visible on desktop */}
            {!isMobileView && (
              <button
                onClick={handleToggleCartDrawer}
                className="flex flex-col items-center p-2 text-white hover:text-blue-100 transition-colors relative"
                aria-label="Cart"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"
                  />
                </svg>
                <span className="text-xs mt-0.5 hidden sm:block">Cart</span>
                {itemCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-yellow-400 text-blue-800 text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
                    {itemCount}
                  </span>
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Search overlay */}
      {searchOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-start justify-center pt-20">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-2xl mx-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">Search Products</h2>
              <button
                onClick={() => setSearchOpen(false)}
                className="text-gray-500 hover:text-gray-700 focus:outline-none"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
            <form onSubmit={handleSearch}>
              <Input
                type="text"
                placeholder="Search for products, brands, categories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                fullWidth
                autoFocus
                leftIcon={
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                }
              />
              <div className="mt-4">
                <Button type="submit" variant="primary" fullWidth>
                  Search
                </Button>
              </div>
            </form>

            {/* Quick links */}
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Popular Searches</h3>
              <div className="flex flex-wrap gap-2">
                {['Smartphones', 'Laptops', 'Headphones', 'Smartwatches', 'Cameras'].map((term) => (
                  <button
                    key={term}
                    className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700"
                    onClick={() => {
                      setSearchQuery(term);
                      navigate(`/search?q=${encodeURIComponent(term)}`);
                      setSearchOpen(false);
                    }}
                  >
                    {term}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;

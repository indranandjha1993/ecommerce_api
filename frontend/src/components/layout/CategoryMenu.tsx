import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { twMerge } from 'tailwind-merge';
import { useUI } from '../../hooks/useUI';
import { useAuth } from '../../contexts/AuthContext';
import { useCart } from '../../contexts/CartContext';

interface CategoryMenuProps {
  onClose: () => void;
}

interface Category {
  id: string;
  name: string;
  slug: string;
  subcategories?: Category[];
}

const CategoryMenu: React.FC<CategoryMenuProps> = ({ onClose }) => {
  const navigate = useNavigate();
  const { isMobileView, toggleCartDrawer } = useUI();
  const { isAuthenticated, user, logout } = useAuth();
  const { itemCount } = useCart();
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [activeSectionId, setActiveSectionId] = useState<string>('categories');
  const [isVisible, setIsVisible] = useState(false);

  // Animation effect - slide in after mount
  useEffect(() => {
    // Small delay to ensure the animation works
    const timer = setTimeout(() => {
      setIsVisible(true);
    }, 10);
    
    return () => clearTimeout(timer);
  }, []);

  // Sample categories data - in a real app, this would come from an API
  const categories: Category[] = [
    {
      id: '1',
      name: 'Electronics',
      slug: 'electronics',
      subcategories: [
        {
          id: '1-1',
          name: 'Smartphones',
          slug: 'smartphones',
          subcategories: [
            { id: '1-1-1', name: 'Apple', slug: 'apple' },
            { id: '1-1-2', name: 'Samsung', slug: 'samsung' },
            { id: '1-1-3', name: 'Google', slug: 'google' },
            { id: '1-1-4', name: 'OnePlus', slug: 'oneplus' },
            { id: '1-1-5', name: 'Xiaomi', slug: 'xiaomi' },
          ]
        },
        {
          id: '1-2',
          name: 'Laptops',
          slug: 'laptops',
          subcategories: [
            { id: '1-2-1', name: 'Gaming', slug: 'gaming-laptops' },
            { id: '1-2-2', name: 'Business', slug: 'business-laptops' },
            { id: '1-2-3', name: 'Ultrabooks', slug: 'ultrabooks' },
            { id: '1-2-4', name: 'Chromebooks', slug: 'chromebooks' },
          ]
        },
        {
          id: '1-3',
          name: 'Audio',
          slug: 'audio',
          subcategories: [
            { id: '1-3-1', name: 'Headphones', slug: 'headphones' },
            { id: '1-3-2', name: 'Earbuds', slug: 'earbuds' },
            { id: '1-3-3', name: 'Speakers', slug: 'speakers' },
            { id: '1-3-4', name: 'Microphones', slug: 'microphones' },
          ]
        },
        { id: '1-4', name: 'Cameras', slug: 'cameras' },
        { id: '1-5', name: 'Wearables', slug: 'wearables' },
        { id: '1-6', name: 'Accessories', slug: 'electronics-accessories' },
      ]
    },
    {
      id: '2',
      name: 'Fashion',
      slug: 'fashion',
      subcategories: [
        {
          id: '2-1',
          name: 'Men',
          slug: 'men',
          subcategories: [
            { id: '2-1-1', name: 'T-shirts', slug: 'men-tshirts' },
            { id: '2-1-2', name: 'Shirts', slug: 'men-shirts' },
            { id: '2-1-3', name: 'Jeans', slug: 'men-jeans' },
            { id: '2-1-4', name: 'Trousers', slug: 'men-trousers' },
            { id: '2-1-5', name: 'Jackets', slug: 'men-jackets' },
          ]
        },
        {
          id: '2-2',
          name: 'Women',
          slug: 'women',
          subcategories: [
            { id: '2-2-1', name: 'Tops', slug: 'women-tops' },
            { id: '2-2-2', name: 'Dresses', slug: 'women-dresses' },
            { id: '2-2-3', name: 'Jeans', slug: 'women-jeans' },
            { id: '2-2-4', name: 'Skirts', slug: 'women-skirts' },
            { id: '2-2-5', name: 'Jackets', slug: 'women-jackets' },
          ]
        },
        { id: '2-3', name: 'Kids', slug: 'kids' },
        { id: '2-4', name: 'Footwear', slug: 'footwear' },
        { id: '2-5', name: 'Accessories', slug: 'fashion-accessories' },
      ]
    },
    {
      id: '3',
      name: 'Home & Kitchen',
      slug: 'home-kitchen',
      subcategories: [
        { id: '3-1', name: 'Furniture', slug: 'furniture' },
        { id: '3-2', name: 'Kitchen Appliances', slug: 'kitchen-appliances' },
        { id: '3-3', name: 'Cookware', slug: 'cookware' },
        { id: '3-4', name: 'Home Decor', slug: 'home-decor' },
        { id: '3-5', name: 'Bedding', slug: 'bedding' },
        { id: '3-6', name: 'Bath', slug: 'bath' },
      ]
    },
    {
      id: '4',
      name: 'Beauty & Personal Care',
      slug: 'beauty-personal-care',
      subcategories: [
        { id: '4-1', name: 'Skincare', slug: 'skincare' },
        { id: '4-2', name: 'Makeup', slug: 'makeup' },
        { id: '4-3', name: 'Hair Care', slug: 'hair-care' },
        { id: '4-4', name: 'Fragrances', slug: 'fragrances' },
        { id: '4-5', name: 'Men\'s Grooming', slug: 'mens-grooming' },
      ]
    },
    {
      id: '5',
      name: 'Sports & Outdoors',
      slug: 'sports-outdoors',
      subcategories: [
        { id: '5-1', name: 'Exercise & Fitness', slug: 'exercise-fitness' },
        { id: '5-2', name: 'Outdoor Recreation', slug: 'outdoor-recreation' },
        { id: '5-3', name: 'Team Sports', slug: 'team-sports' },
        { id: '5-4', name: 'Camping & Hiking', slug: 'camping-hiking' },
      ]
    },
    {
      id: '6',
      name: 'Books & Media',
      slug: 'books-media',
      subcategories: [
        { id: '6-1', name: 'Books', slug: 'books' },
        { id: '6-2', name: 'eBooks', slug: 'ebooks' },
        { id: '6-3', name: 'Movies & TV', slug: 'movies-tv' },
        { id: '6-4', name: 'Music', slug: 'music' },
        { id: '6-5', name: 'Video Games', slug: 'video-games' },
      ]
    },
    {
      id: '7',
      name: 'Toys & Games',
      slug: 'toys-games',
      subcategories: [
        { id: '7-1', name: 'Action Figures', slug: 'action-figures' },
        { id: '7-2', name: 'Board Games', slug: 'board-games' },
        { id: '7-3', name: 'Puzzles', slug: 'puzzles' },
        { id: '7-4', name: 'Dolls & Accessories', slug: 'dolls-accessories' },
        { id: '7-5', name: 'Educational Toys', slug: 'educational-toys' },
      ]
    },
    {
      id: '8',
      name: 'Grocery & Gourmet',
      slug: 'grocery-gourmet',
      subcategories: [
        { id: '8-1', name: 'Snacks', slug: 'snacks' },
        { id: '8-2', name: 'Beverages', slug: 'beverages' },
        { id: '8-3', name: 'Breakfast Foods', slug: 'breakfast-foods' },
        { id: '8-4', name: 'Organic Foods', slug: 'organic-foods' },
      ]
    },
  ];

  const handleCategoryClick = (categoryId: string) => {
    setActiveCategory(prev => prev === categoryId ? null : categoryId);
  };

  const handleLinkClick = () => {
    onClose();
  };

  const handleLogout = () => {
    logout();
    onClose();
    navigate('/');
  };

  const handleCartClick = () => {
    onClose();
    toggleCartDrawer();
  };

  // Only render for mobile devices
  if (!isMobileView) return null;

  return (
    <div 
      className={twMerge(
        "fixed top-0 left-0 h-full bg-white shadow-xl z-50 transition-all duration-300 transform",
        "w-full max-w-sm",
        isVisible ? "translate-x-0" : "-translate-x-full"
      )}
      style={{ 
        top: '0', 
        height: '100%',
        maxHeight: '100vh',
        overflowY: 'auto',
        zIndex: 9999
      }}
    >
      {/* Header with gradient background */}
      <div className="sticky top-0 z-10 bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-md">
        <div className="flex items-center justify-between p-4">
          <h2 className="text-lg font-semibold">Menu</h2>
          <button 
            onClick={onClose}
            className="text-white hover:text-blue-100 focus:outline-none"
            aria-label="Close menu"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* User info section */}
      <div className="p-4 border-b border-gray-200">
        {isAuthenticated ? (
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-lg">
              {user?.name?.charAt(0) || 'U'}
            </div>
            <div>
              <p className="font-medium text-gray-900">{user?.name || 'User'}</p>
              <p className="text-sm text-gray-500 truncate">{user?.email}</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col space-y-2">
            <p className="text-gray-700 mb-2">Sign in for a personalized experience</p>
            <div className="flex space-x-2">
              <Link 
                to="/login" 
                className="flex-1 py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white text-center font-medium rounded-md transition-colors"
                onClick={handleLinkClick}
              >
                Sign In
              </Link>
              <Link 
                to="/register" 
                className="flex-1 py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-800 text-center font-medium rounded-md transition-colors"
                onClick={handleLinkClick}
              >
                Register
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Navigation tabs */}
      <div className="flex border-b border-gray-200">
        <button 
          className={twMerge(
            "flex-1 py-3 text-center font-medium text-sm transition-colors",
            activeSectionId === 'categories' 
              ? "text-blue-600 border-b-2 border-blue-600" 
              : "text-gray-600 hover:text-blue-600"
          )}
          onClick={() => setActiveSectionId('categories')}
        >
          Categories
        </button>
        <button 
          className={twMerge(
            "flex-1 py-3 text-center font-medium text-sm transition-colors",
            activeSectionId === 'account' 
              ? "text-blue-600 border-b-2 border-blue-600" 
              : "text-gray-600 hover:text-blue-600"
          )}
          onClick={() => setActiveSectionId('account')}
        >
          Account
        </button>
      </div>

      {/* Categories section */}
      {activeSectionId === 'categories' && (
        <div className="pb-20">
          <ul className="py-2">
            {categories.map(category => (
              <li key={category.id} className="border-b border-gray-100 last:border-b-0">
                <button
                  className={twMerge(
                    "w-full text-left px-4 py-3 flex items-center justify-between hover:bg-blue-50 transition-colors",
                    activeCategory === category.id ? "bg-blue-50 text-blue-600 font-medium" : "text-gray-700"
                  )}
                  onClick={() => handleCategoryClick(category.id)}
                >
                  <span>{category.name}</span>
                  {category.subcategories && (
                    <svg 
                      className={twMerge(
                        "h-4 w-4 transition-transform duration-200",
                        activeCategory === category.id ? "rotate-90" : ""
                      )} 
                      fill="none" 
                      viewBox="0 0 24 24" 
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                    </svg>
                  )}
                </button>
                
                {/* Mobile subcategories (accordion style) */}
                {activeCategory === category.id && category.subcategories && (
                  <div className="bg-gray-50 border-l-2 border-blue-500 ml-4 animate-fadeIn">
                    {category.subcategories.map(subcat => (
                      <div key={subcat.id}>
                        {subcat.subcategories ? (
                          <div className="py-2">
                            <div className="px-4 py-2 font-medium text-blue-800">{subcat.name}</div>
                            <div className="pl-4">
                              {subcat.subcategories.map(item => (
                                <Link
                                  key={item.id}
                                  to={`/categories/${category.slug}/${subcat.slug}/${item.slug}`}
                                  className="block px-4 py-2 text-gray-700 hover:bg-blue-100 hover:text-blue-700 rounded-md mx-2 my-1"
                                  onClick={handleLinkClick}
                                >
                                  {item.name}
                                </Link>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <Link
                            to={`/categories/${category.slug}/${subcat.slug}`}
                            className="block px-4 py-2 text-gray-700 hover:bg-blue-100 hover:text-blue-700 rounded-md mx-2 my-1"
                            onClick={handleLinkClick}
                          >
                            {subcat.name}
                          </Link>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Account section */}
      {activeSectionId === 'account' && (
        <div className="pb-20">
          <div className="py-2">
            {isAuthenticated ? (
              <ul>
                <li>
                  <Link
                    to="/account"
                    className="flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                    onClick={handleLinkClick}
                  >
                    <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    My Account
                  </Link>
                </li>
                <li>
                  <Link
                    to="/orders"
                    className="flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                    onClick={handleLinkClick}
                  >
                    <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                    </svg>
                    Orders
                  </Link>
                </li>
                <li>
                  <Link
                    to="/wishlist"
                    className="flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                    onClick={handleLinkClick}
                  >
                    <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    Wishlist
                  </Link>
                </li>
                <li>
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center px-4 py-3 text-red-600 hover:bg-red-50"
                  >
                    <svg className="mr-3 h-5 w-5 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Logout
                  </button>
                </li>
              </ul>
            ) : (
              <div className="px-4 py-6 text-center">
                <p className="text-gray-500 mb-4">Please sign in to view your account details</p>
                <Link 
                  to="/login" 
                  className="inline-block py-2 px-6 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors"
                  onClick={handleLinkClick}
                >
                  Sign In
                </Link>
              </div>
            )}
          </div>

          <div className="border-t border-gray-200 pt-2">
            <h3 className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">Help & Settings</h3>
            <ul>
              <li>
                <Link
                  to="/contact"
                  className="flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={handleLinkClick}
                >
                  <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Contact Us
                </Link>
              </li>
              <li>
                <Link
                  to="/faq"
                  className="flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600"
                  onClick={handleLinkClick}
                >
                  <svg className="mr-3 h-5 w-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  FAQ
                </Link>
              </li>
            </ul>
          </div>
        </div>
      )}
      
      {/* Bottom action buttons */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 shadow-lg" style={{ maxWidth: '20rem' }}>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={handleCartClick}
            className="flex items-center justify-center py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors"
          >
            <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            Cart {itemCount > 0 && <span className="ml-1">({itemCount})</span>}
          </button>
          <Link 
            to="/categories"
            className="flex items-center justify-center py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-md transition-colors"
            onClick={handleLinkClick}
          >
            <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h7" />
            </svg>
            All Categories
          </Link>
        </div>
      </div>
    </div>
  );
};

export default CategoryMenu;
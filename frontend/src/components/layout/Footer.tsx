import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Button from '../ui/Button';
import Input from '../ui/Input';

const Footer: React.FC = () => {
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      // In a real app, you would call an API to subscribe the user
      setSubscribed(true);
      setEmail('');
      setTimeout(() => setSubscribed(false), 5000);
    }
  };

  // Footer links organized by section
  const footerLinks = {
    shop: [
      { label: 'All Products', path: '/products' },
      { label: 'New Arrivals', path: '/products/new' },
      { label: 'Featured', path: '/products/featured' },
      { label: 'Categories', path: '/categories' },
      { label: 'Brands', path: '/brands' },
      { label: 'Sale', path: '/sale' },
    ],
    account: [
      { label: 'My Account', path: '/account' },
      { label: 'Orders', path: '/orders' },
      { label: 'Wishlist', path: '/wishlist' },
      { label: 'Cart', path: '/cart' },
      { label: 'Track Order', path: '/track-order' },
    ],
    support: [
      { label: 'Contact Us', path: '/contact' },
      { label: 'FAQ', path: '/faq' },
      { label: 'Shipping & Returns', path: '/shipping' },
      { label: 'Terms & Conditions', path: '/terms' },
      { label: 'Privacy Policy', path: '/privacy' },
    ],
  };

  // Payment methods
  const paymentMethods = [
    { name: 'Visa', icon: 'visa.svg' },
    { name: 'Mastercard', icon: 'mastercard.svg' },
    { name: 'American Express', icon: 'amex.svg' },
    { name: 'PayPal', icon: 'paypal.svg' },
    { name: 'Apple Pay', icon: 'apple-pay.svg' },
  ];

  return (
    <div className="bg-gradient-to-b from-gray-800 to-gray-900 text-white pt-16 pb-8 w-full relative">
      {/* Wave decoration */}
      <div className="absolute top-0 left-0 right-0 h-16 overflow-hidden -translate-y-full">
        <svg className="absolute bottom-0 w-full h-16 text-gray-800" preserveAspectRatio="none" viewBox="0 0 1440 54">
          <path fill="currentColor" d="M0 22L60 16.7C120 11 240 1 360 0C480 -1 600 7 720 12.3C840 17 960 21 1080 19.2C1200 17 1320 11 1380 7.7L1440 5V54H1380C1320 54 1200 54 1080 54C960 54 840 54 720 54C600 54 480 54 360 54C240 54 120 54 60 54H0V22Z"></path>
        </svg>
      </div>
      
      {/* Newsletter section with enhanced design */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
        <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 rounded-2xl p-6 md:p-10 lg:p-12 relative overflow-hidden shadow-xl transform hover:scale-[1.01] transition-transform duration-300">
          {/* Decorative elements */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-10 rounded-full transform translate-x-1/3 -translate-y-1/2"></div>
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-white opacity-10 rounded-full transform -translate-x-1/3 translate-y-1/2"></div>
          
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="max-w-lg">
              <h2 className="text-2xl md:text-3xl font-bold mb-3 text-white">Subscribe to our newsletter</h2>
              <p className="text-blue-100 text-base md:text-lg">
                Get the latest updates, deals and exclusive offers directly to your inbox.
              </p>
            </div>
            <div className="w-full md:w-auto">
              <form onSubmit={handleSubscribe} className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Your email address"
                  required
                  className="bg-white/20 border-white/30 text-white placeholder:text-blue-100 w-full sm:w-64 focus:ring-2 focus:ring-white/50"
                />
                <Button 
                  type="submit" 
                  variant="secondary" 
                  size="md"
                  className="whitespace-nowrap bg-white text-blue-700 hover:bg-blue-50 transition-colors"
                >
                  {subscribed ? '✓ Subscribed!' : 'Subscribe'}
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-12 mb-12">
          {/* Company Info */}
          <div className="lg:col-span-2">
            <div className="flex items-center mb-6">
              <svg className="h-8 w-8 text-blue-500" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
              </svg>
              <span className="ml-2 text-xl font-bold text-white">ShopSmart</span>
            </div>
            <p className="text-gray-400 mb-6 max-w-md">
              Your one-stop shop for all your shopping needs. Quality products, competitive prices, and excellent customer service.
              We're committed to providing the best shopping experience.
            </p>
            <div className="flex space-x-5 mb-8">
              <a 
                href="#" 
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="Facebook"
              >
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clipRule="evenodd" />
                </svg>
              </a>
              <a 
                href="#" 
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="Instagram"
              >
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" d="M12.315 2c2.43 0 2.784.013 3.808.06 1.064.049 1.791.218 2.427.465a4.902 4.902 0 011.772 1.153 4.902 4.902 0 011.153 1.772c.247.636.416 1.363.465 2.427.048 1.067.06 1.407.06 4.123v.08c0 2.643-.012 2.987-.06 4.043-.049 1.064-.218 1.791-.465 2.427a4.902 4.902 0 01-1.153 1.772 4.902 4.902 0 01-1.772 1.153c-.636.247-1.363.416-2.427.465-1.067.048-1.407.06-4.123.06h-.08c-2.643 0-2.987-.012-4.043-.06-1.064-.049-1.791-.218-2.427-.465a4.902 4.902 0 01-1.772-1.153 4.902 4.902 0 01-1.153-1.772c-.247-.636-.416-1.363-.465-2.427-.047-1.024-.06-1.379-.06-3.808v-.63c0-2.43.013-2.784.06-3.808.049-1.064.218-1.791.465-2.427a4.902 4.902 0 011.153-1.772A4.902 4.902 0 015.45 2.525c.636-.247 1.363-.416 2.427-.465C8.901 2.013 9.256 2 11.685 2h.63zm-.081 1.802h-.468c-2.456 0-2.784.011-3.807.058-.975.045-1.504.207-1.857.344-.467.182-.8.398-1.15.748-.35.35-.566.683-.748 1.15-.137.353-.3.882-.344 1.857-.047 1.023-.058 1.351-.058 3.807v.468c0 2.456.011 2.784.058 3.807.045.975.207 1.504.344 1.857.182.466.399.8.748 1.15.35.35.683.566 1.15.748.353.137.882.3 1.857.344 1.054.048 1.37.058 4.041.058h.08c2.597 0 2.917-.01 3.96-.058.976-.045 1.505-.207 1.858-.344.466-.182.8-.398 1.15-.748.35-.35.566-.683.748-1.15.137-.353.3-.882.344-1.857.048-1.055.058-1.37.058-4.041v-.08c0-2.597-.01-2.917-.058-3.96-.045-.976-.207-1.505-.344-1.858a3.097 3.097 0 00-.748-1.15 3.098 3.098 0 00-1.15-.748c-.353-.137-.882-.3-1.857-.344-1.023-.047-1.351-.058-3.807-.058zM12 6.865a5.135 5.135 0 110 10.27 5.135 5.135 0 010-10.27zm0 1.802a3.333 3.333 0 100 6.666 3.333 3.333 0 000-6.666zm5.338-3.205a1.2 1.2 0 110 2.4 1.2 1.2 0 010-2.4z" clipRule="evenodd" />
                </svg>
              </a>
              <a 
                href="#" 
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="Twitter"
              >
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
              </a>
              <a 
                href="#" 
                className="text-gray-400 hover:text-white transition-colors"
                aria-label="YouTube"
              >
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" d="M19.812 5.418c.861.23 1.538.907 1.768 1.768C21.998 8.746 22 12 22 12s0 3.255-.418 4.814a2.504 2.504 0 0 1-1.768 1.768c-1.56.419-7.814.419-7.814.419s-6.255 0-7.814-.419a2.505 2.505 0 0 1-1.768-1.768C2 15.255 2 12 2 12s0-3.255.417-4.814a2.507 2.507 0 0 1 1.768-1.768C5.744 5 11.998 5 11.998 5s6.255 0 7.814.418ZM15.194 12 10 15V9l5.194 3Z" clipRule="evenodd" />
                </svg>
              </a>
            </div>
            
            {/* Contact info */}
            <div className="space-y-3">
              <div className="flex items-start">
                <svg className="h-5 w-5 text-gray-400 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <p className="text-gray-400">123 Commerce St, New York, NY 10001</p>
              </div>
              <div className="flex items-start">
                <svg className="h-5 w-5 text-gray-400 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <p className="text-gray-400">support@shopsmart.com</p>
              </div>
              <div className="flex items-start">
                <svg className="h-5 w-5 text-gray-400 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <p className="text-gray-400">(123) 456-7890</p>
              </div>
            </div>
          </div>
          
          {/* Shop Links */}
          <div>
            <h3 className="text-lg font-semibold mb-6 text-white">Shop</h3>
            <ul className="space-y-3">
              {footerLinks.shop.map((link) => (
                <li key={link.path}>
                  <Link 
                    to={link.path} 
                    className="text-gray-400 hover:text-white transition-colors inline-block"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Account Links */}
          <div>
            <h3 className="text-lg font-semibold mb-6 text-white">Account</h3>
            <ul className="space-y-3">
              {footerLinks.account.map((link) => (
                <li key={link.path}>
                  <Link 
                    to={link.path} 
                    className="text-gray-400 hover:text-white transition-colors inline-block"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Support Links */}
          <div>
            <h3 className="text-lg font-semibold mb-6 text-white">Support</h3>
            <ul className="space-y-3">
              {footerLinks.support.map((link) => (
                <li key={link.path}>
                  <Link 
                    to={link.path} 
                    className="text-gray-400 hover:text-white transition-colors inline-block"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
        
        {/* Payment methods */}
        <div className="border-t border-gray-800 pt-8 pb-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex flex-wrap items-center space-x-4">
              <span className="text-gray-400 text-sm">We accept:</span>
              <div className="flex flex-wrap gap-2">
                <div className="h-8 w-12 bg-white rounded px-1 flex items-center justify-center">
                  <svg className="h-5" viewBox="0 0 48 48" fill="none">
                    <path d="M44 24C44 35.046 35.046 44 24 44C12.954 44 4 35.046 4 24C4 12.954 12.954 4 24 4C35.046 4 44 12.954 44 24Z" fill="#2566AF"/>
                    <path d="M20.5 30.3333H16.6667L19.1667 17.6667H23L20.5 30.3333Z" fill="white"/>
                    <path d="M33.3333 18C32.5 17.6667 31.3333 17.3333 30 17.3333C26.6667 17.3333 24.3333 19 24.3333 21.3333C24.3333 23 26 24 27.3333 24.6667C28.6667 25.3333 29.1667 25.6667 29.1667 26.3333C29.1667 27.3333 28 27.6667 26.8333 27.6667C25.5 27.6667 24.8333 27.3333 23.6667 27L23.1667 26.6667L22.6667 29.6667C23.6667 30.3333 25.3333 30.6667 27 30.6667C30.6667 30.6667 32.8333 29 32.8333 26.6667C32.8333 25.3333 31.8333 24.3333 30 23.3333C28.8333 22.6667 28.1667 22.3333 28.1667 21.6667C28.1667 21 28.8333 20.3333 30.3333 20.3333C31.5 20.3333 32.3333 20.6667 33 21L33.3333 21.3333L34 18.3333L33.3333 18Z" fill="white"/>
                    <path d="M36.6667 30.3333H39.6667L37.3333 17.6667H34.6667C33.6667 17.6667 33 18 32.6667 19L27.6667 30.3333H31.3333L32 28.6667H36.3333L36.6667 30.3333ZM33 26L34.6667 21.6667L35.6667 26H33Z" fill="white"/>
                    <path d="M24.6667 17.6667L21.3333 26.3333L21 25L19.6667 18.6667C19.6667 18 19 17.6667 18.3333 17.6667H12.3333L12 18C13.3333 18.3333 14.6667 18.6667 15.6667 19.3333C16 19.3333 16.3333 19.6667 16.3333 20L19.3333 30.3333H23L28.3333 17.6667H24.6667Z" fill="white"/>
                  </svg>
                </div>
                <div className="h-8 w-12 bg-white rounded px-1 flex items-center justify-center">
                  <svg className="h-5" viewBox="0 0 48 48" fill="none">
                    <path d="M4 24C4 12.954 12.954 4 24 4C35.046 4 44 12.954 44 24C44 35.046 35.046 44 24 44C12.954 44 4 35.046 4 24Z" fill="#FFB600"/>
                    <path d="M24 34.5C29.799 34.5 34.5 29.799 34.5 24C34.5 18.201 29.799 13.5 24 13.5C18.201 13.5 13.5 18.201 13.5 24C13.5 29.799 18.201 34.5 24 34.5Z" fill="#F7981D"/>
                    <path d="M24 34.5C28.142 34.5 31.5 29.799 31.5 24C31.5 18.201 28.142 13.5 24 13.5C19.858 13.5 16.5 18.201 16.5 24C16.5 29.799 19.858 34.5 24 34.5Z" fill="#FF8500"/>
                    <path d="M19.5 20.25V27.75L24 24L19.5 20.25Z" fill="#FF5050"/>
                    <path d="M28.5 20.25V27.75L24 24L28.5 20.25Z" fill="#E52836"/>
                    <path d="M28.5 20.25L19.5 27.75V20.25H28.5Z" fill="#CB2026"/>
                    <path d="M19.5 27.75L28.5 20.25V27.75H19.5Z" fill="#CB2026"/>
                    <path d="M19.5 20.25L28.5 27.75H19.5V20.25Z" fill="#FF5050"/>
                    <path d="M28.5 20.25L19.5 27.75H28.5V20.25Z" fill="#E52836"/>
                  </svg>
                </div>
                <div className="h-8 w-12 bg-white rounded px-1 flex items-center justify-center">
                  <svg className="h-5" viewBox="0 0 48 48" fill="none">
                    <path d="M4 24C4 12.954 12.954 4 24 4C35.046 4 44 12.954 44 24C44 35.046 35.046 44 24 44C12.954 44 4 35.046 4 24Z" fill="#016FD0"/>
                    <path d="M24.5 13H18L12 35H18.5L19.5 31H25.5L26.5 35H33L27 13H24.5ZM20.5 26L22.5 18L24.5 26H20.5Z" fill="white"/>
                    <path d="M33.5 24L36 19.5H31L28 13H25L31.5 24H33.5Z" fill="#D4E1F4"/>
                    <path d="M33.5 24L31.5 24H25L28 35H31L33.5 29.5L36 24H33.5Z" fill="#D4E1F4"/>
                  </svg>
                </div>
                <div className="h-8 w-12 bg-white rounded px-1 flex items-center justify-center">
                  <svg className="h-5" viewBox="0 0 48 48" fill="none">
                    <path d="M44 24C44 35.046 35.046 44 24 44C12.954 44 4 35.046 4 24C4 12.954 12.954 4 24 4C35.046 4 44 12.954 44 24Z" fill="#F3F3F3"/>
                    <path d="M13 19.5C13 18.672 13.672 18 14.5 18H33.5C34.328 18 35 18.672 35 19.5V28.5C35 29.328 34.328 30 33.5 30H14.5C13.672 30 13 29.328 13 28.5V19.5Z" fill="#249BE9"/>
                    <path d="M20 26.5C21.933 26.5 23.5 24.933 23.5 23C23.5 21.067 21.933 19.5 20 19.5C18.067 19.5 16.5 21.067 16.5 23C16.5 24.933 18.067 26.5 20 26.5Z" fill="#F3F3F3"/>
                    <path d="M28 26.5C29.933 26.5 31.5 24.933 31.5 23C31.5 21.067 29.933 19.5 28 19.5C26.067 19.5 24.5 21.067 24.5 23C24.5 24.933 26.067 26.5 28 26.5Z" fill="#F3F3F3"/>
                    <path d="M26.5 23C26.5 21.067 24.933 19.5 23 19.5C21.067 19.5 19.5 21.067 19.5 23C19.5 24.933 21.067 26.5 23 26.5C24.933 26.5 26.5 24.933 26.5 23Z" fill="#249BE9"/>
                  </svg>
                </div>
                <div className="h-8 w-12 bg-white rounded px-1 flex items-center justify-center">
                  <svg className="h-5" viewBox="0 0 48 48" fill="none">
                    <path d="M44 24C44 35.046 35.046 44 24 44C12.954 44 4 35.046 4 24C4 12.954 12.954 4 24 4C35.046 4 44 12.954 44 24Z" fill="black"/>
                    <path d="M24 16C20.5 16 17.5 18 17.5 21C17.5 24.5 21 26 21 26C21 26 20.5 28 18.5 28C16.5 28 15 26.5 15 26.5C15 26.5 17 30 20.5 30C24 30 26 27.5 26 25C26 22 23 20.5 23 20.5C23 20.5 23.5 18.5 25.5 18.5C27.5 18.5 29 20 29 20C29 20 27 16 24 16Z" fill="white"/>
                    <path d="M31 22H29V18H27V22H25V24H27V28H29V24H31V22Z" fill="white"/>
                  </svg>
                </div>
              </div>
            </div>
            <div className="text-gray-400 text-sm">
              © {new Date().getFullYear()} ShopSmart. All rights reserved.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Footer;
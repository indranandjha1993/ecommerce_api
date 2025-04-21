# ShopSmart E-commerce Frontend

This is the frontend implementation for the ShopSmart e-commerce platform. It's built with React, Redux, and Tailwind CSS, providing a modern and responsive user interface for the e-commerce API.

## Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Product Browsing**: Browse products by category, brand, or search
- **Product Details**: View detailed product information, images, and variants
- **Shopping Cart**: Add products to cart, update quantities, and remove items
- **Checkout Process**: Complete purchases with shipping and payment information
- **User Authentication**: Register, login, and manage user profile
- **Order Management**: View order history and details
- **Wishlist**: Save products for later

## Tech Stack

- **React**: UI library for building the user interface
- **Redux**: State management for the application
- **React Router**: Navigation and routing
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Axios**: HTTP client for API requests
- **React Hook Form**: Form validation and handling
- **Zod**: Schema validation
- **TypeScript**: Type safety and better developer experience

## Project Structure

```
frontend/
├── public/              # Static files
├── src/                 # Source code
│   ├── components/      # Reusable UI components
│   │   ├── auth/        # Authentication components
│   │   ├── cart/        # Cart components
│   │   ├── checkout/    # Checkout components
│   │   ├── layout/      # Layout components (header, footer)
│   │   ├── product/     # Product components
│   │   └── ui/          # UI components (buttons, inputs)
│   ├── hooks/           # Custom React hooks
│   ├── pages/           # Page components
│   ├── services/        # API services
│   ├── store/           # Redux store
│   │   ├── slices/      # Redux slices
│   │   └── index.ts     # Store configuration
│   ├── types/           # TypeScript types
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Main App component
│   ├── index.tsx        # Entry point
│   └── router/          # Routing configuration
├── package.json         # Dependencies and scripts
└── tsconfig.json        # TypeScript configuration
```

## Pages

1. **HomePage**: Landing page with featured products, categories, and promotions
2. **ProductsPage**: Browse and filter products
3. **ProductDetailPage**: View detailed product information
4. **CartPage**: View and manage cart items
5. **CheckoutPage**: Complete the purchase process
6. **OrderSuccessPage**: Confirmation after successful order
7. **OrdersPage**: View order history
8. **OrderDetailPage**: View detailed order information
9. **LoginPage**: User login
10. **RegisterPage**: User registration
11. **ProfilePage**: User profile management
12. **NotFoundPage**: 404 page

## Components

### Layout Components
- **MainLayout**: Main layout with header and footer
- **Header**: Navigation and user menu
- **Footer**: Site information and links

### Product Components
- **ProductGrid**: Display products in a grid
- **ProductCard**: Individual product card
- **ProductDetail**: Detailed product view
- **ProductFilter**: Filter products by various criteria

### Cart Components
- **CartItem**: Individual cart item
- **CartDrawer**: Slide-in cart view

### Checkout Components
- **AddressForm**: Form for shipping/billing address
- **ShippingMethodSelector**: Select shipping method
- **PaymentMethodSelector**: Select payment method
- **OrderSummary**: Order summary with pricing

### UI Components
- **Button**: Reusable button component
- **Input**: Form input component
- **Select**: Dropdown select component
- **Badge**: Status badge component
- **LoadingSpinner**: Loading indicator
- **Notifications**: Toast notifications

## State Management

The application uses Redux for state management with the following slices:

- **authSlice**: User authentication state
- **cartSlice**: Shopping cart state
- **productSlice**: Product data state
- **categorySlice**: Category data state
- **brandSlice**: Brand data state
- **orderSlice**: Order data state
- **addressSlice**: User addresses state
- **uiSlice**: UI state (modals, drawers, notifications)

## Getting Started

1. Install dependencies: `npm install`
2. Start the development server: `npm run dev`
3. Build for production: `npm run build`

## API Integration

The frontend integrates with the ShopSmart API for all data operations. API services are organized in the `services` directory, with separate modules for different resource types:

- **auth.service.ts**: Authentication operations
- **product.service.ts**: Product operations
- **cart.service.ts**: Cart operations
- **order.service.ts**: Order operations
- **category.service.ts**: Category operations
- **brand.service.ts**: Brand operations

## Responsive Design

The UI is fully responsive and works on:
- Mobile devices (< 640px)
- Tablets (640px - 1024px)
- Desktops (> 1024px)

Tailwind CSS is used for responsive design with utility classes.

## Accessibility

The application follows accessibility best practices:
- Semantic HTML
- ARIA attributes
- Keyboard navigation
- Focus management
- Color contrast

## Performance Optimization

- Code splitting with React.lazy and Suspense
- Memoization with React.memo and useMemo
- Lazy loading of images
- Optimized bundle size

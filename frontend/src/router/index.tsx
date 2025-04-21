import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import MainLayout from '../components/layout/MainLayout';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ProtectedRoute from './ProtectedRoute';

// Lazy-loaded pages
const HomePage = lazy(() => import('../pages/HomePage'));
const ProductsPage = lazy(() => import('../pages/ProductsPage'));
const ProductDetailPage = lazy(() => import('../pages/ProductDetailPage'));
const CartPage = lazy(() => import('../pages/CartPage'));
const CheckoutPage = lazy(() => import('../pages/CheckoutPage'));
const OrderSuccessPage = lazy(() => import('../pages/OrderSuccessPage'));
const OrderDetailPage = lazy(() => import('../pages/OrderDetailPage'));
const OrdersPage = lazy(() => import('../pages/OrdersPage'));

// Auth pages
const LoginPage = lazy(() => import('../pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('../pages/auth/RegisterPage'));
const ForgotPasswordPage = lazy(() => import('../pages/auth/ForgotPasswordPage'));
const ResetPasswordPage = lazy(() => import('../pages/auth/ResetPasswordPage'));

// Account pages
const AccountPage = lazy(() => import('../pages/account/AccountPage'));
const NotFoundPage = lazy(() => import('../pages/NotFoundPage'));

const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <HomePage />
          </Suspense>
        ),
      },
      {
        path: 'products',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <ProductsPage />
          </Suspense>
        ),
      },
      {
        path: 'products/:slug',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <ProductDetailPage />
          </Suspense>
        ),
      },
      {
        path: 'cart',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <CartPage />
          </Suspense>
        ),
      },
      {
        path: 'checkout',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <ProtectedRoute>
              <CheckoutPage />
            </ProtectedRoute>
          </Suspense>
        ),
      },
      {
        path: 'order-success/:orderId',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <ProtectedRoute>
              <OrderSuccessPage />
            </ProtectedRoute>
          </Suspense>
        ),
      },
      {
        path: 'orders',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <ProtectedRoute>
              <OrdersPage />
            </ProtectedRoute>
          </Suspense>
        ),
      },
      {
        path: 'orders/:orderId',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <ProtectedRoute>
              <OrderDetailPage />
            </ProtectedRoute>
          </Suspense>
        ),
      },
      {
        path: 'login',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <LoginPage />
          </Suspense>
        ),
      },
      {
        path: 'register',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <RegisterPage />
          </Suspense>
        ),
      },
      {
        path: 'forgot-password',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <ForgotPasswordPage />
          </Suspense>
        ),
      },
      {
        path: 'reset-password/:token',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <ResetPasswordPage />
          </Suspense>
        ),
      },
      {
        path: 'account',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <ProtectedRoute>
              <AccountPage />
            </ProtectedRoute>
          </Suspense>
        ),
      },
      {
        path: '*',
        element: (
          <Suspense fallback={<LoadingSpinner />}>
            <NotFoundPage />
          </Suspense>
        ),
      },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}

export default router;
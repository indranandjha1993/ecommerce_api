import { AppRouter } from './router';
import { AuthProvider } from './contexts/AuthContext';
import { CartProvider } from './contexts/CartContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { ProductProvider } from './contexts/ProductContext';
import { CategoryProvider } from './contexts/CategoryContext';
import { BrandProvider } from './contexts/BrandContext';
import './App.css';

function App() {
  return (
    <NotificationProvider>
      <AuthProvider>
        <CartProvider>
          <ProductProvider>
            <CategoryProvider>
              <BrandProvider>
                <AppRouter />
              </BrandProvider>
            </CategoryProvider>
          </ProductProvider>
        </CartProvider>
      </AuthProvider>
    </NotificationProvider>
  );
}

export default App;

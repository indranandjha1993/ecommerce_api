import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import cartReducer from './slices/cartSlice';
import productReducer from './slices/productSlice';
import categoryReducer from './slices/categorySlice';
import brandReducer from './slices/brandSlice';
import uiReducer from './slices/uiSlice';
import orderReducer from './slices/orderSlice';
import addressReducer from './slices/addressSlice';
import checkoutReducer from './slices/checkoutSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    cart: cartReducer,
    product: productReducer,
    category: categoryReducer,
    brand: brandReducer,
    ui: uiReducer,
    order: orderReducer,
    address: addressReducer,
    checkout: checkoutReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
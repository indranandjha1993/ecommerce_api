import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '..';

interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
}

interface UIState {
  notifications: Notification[];
  mobileMenuOpen: boolean;
  searchOpen: boolean;
  cartDrawerOpen: boolean;
  filterDrawerOpen: boolean;
}

const initialState: UIState = {
  notifications: [],
  mobileMenuOpen: false,
  searchOpen: false,
  cartDrawerOpen: false,
  filterDrawerOpen: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id'>>) => {
      const id = Date.now().toString();
      state.notifications.push({
        id,
        ...action.payload,
      });
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    setMobileMenuOpen: (state, action: PayloadAction<boolean>) => {
      state.mobileMenuOpen = action.payload;
    },
    setSearchOpen: (state, action: PayloadAction<boolean>) => {
      state.searchOpen = action.payload;
    },
    setCartDrawerOpen: (state, action: PayloadAction<boolean>) => {
      state.cartDrawerOpen = action.payload;
    },
    setFilterDrawerOpen: (state, action: PayloadAction<boolean>) => {
      state.filterDrawerOpen = action.payload;
    },
  },
});

export const {
  addNotification,
  removeNotification,
  clearNotifications,
  setMobileMenuOpen,
  setSearchOpen,
  setCartDrawerOpen,
  setFilterDrawerOpen,
} = uiSlice.actions;

export const selectNotifications = (state: RootState) => state.ui.notifications;
export const selectMobileMenuOpen = (state: RootState) => state.ui.mobileMenuOpen;
export const selectSearchOpen = (state: RootState) => state.ui.searchOpen;
export const selectCartDrawerOpen = (state: RootState) => state.ui.cartDrawerOpen;
export const selectFilterDrawerOpen = (state: RootState) => state.ui.filterDrawerOpen;

export default uiSlice.reducer;
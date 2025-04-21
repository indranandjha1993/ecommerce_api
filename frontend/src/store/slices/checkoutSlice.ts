import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { orderService } from '../../services/order.service';
import { RootState } from '..';
import { CheckoutData } from '../../hooks/useCheckout';

interface CheckoutState {
  loading: boolean;
  error: string | null;
}

const initialState: CheckoutState = {
  loading: false,
  error: null,
};

export const createOrder = createAsyncThunk(
  'checkout/createOrder',
  async (checkoutData: CheckoutData, { rejectWithValue }) => {
    try {
      const response = await orderService.createOrder(checkoutData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create order');
    }
  }
);

const checkoutSlice = createSlice({
  name: 'checkout',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(createOrder.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createOrder.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(createOrder.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError } = checkoutSlice.actions;

export const selectCheckoutLoading = (state: RootState) => state.checkout.loading;
export const selectCheckoutError = (state: RootState) => state.checkout.error;

export default checkoutSlice.reducer;
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Order } from '../../types';
import { orderService } from '../../services/order.service';
import { RootState } from '..';

interface OrderState {
  orders: { items: Order[], total: number, page: number, size: number, pages: number } | null;
  currentOrder: Order | null;
  loading: boolean;
  error: string | null;
}

const initialState: OrderState = {
  orders: null,
  currentOrder: null,
  loading: false,
  error: null,
};

export const fetchOrders = createAsyncThunk(
  'order/fetchOrders',
  async ({ page = 1, size = 10 }: { page?: number, size?: number } = {}, { rejectWithValue }) => {
    try {
      const response = await orderService.getOrders(page, size);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch orders');
    }
  }
);

export const fetchOrderById = createAsyncThunk(
  'order/fetchOrderById',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await orderService.getOrderById(id);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch order');
    }
  }
);

export const fetchOrderByNumber = createAsyncThunk(
  'order/fetchOrderByNumber',
  async (orderNumber: string, { rejectWithValue }) => {
    try {
      const response = await orderService.getOrderByNumber(orderNumber);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch order');
    }
  }
);

export const createOrder = createAsyncThunk(
  'order/createOrder',
  async (orderData: any, { rejectWithValue }) => {
    try {
      const response = await orderService.createOrder(orderData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create order');
    }
  }
);

export const cancelOrder = createAsyncThunk(
  'order/cancelOrder',
  async ({ id, reason }: { id: string, reason?: string }, { rejectWithValue }) => {
    try {
      const response = await orderService.cancelOrder(id, reason);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to cancel order');
    }
  }
);

const orderSlice = createSlice({
  name: 'order',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentOrder: (state) => {
      state.currentOrder = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch orders
      .addCase(fetchOrders.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.loading = false;
        state.orders = action.payload;
      })
      .addCase(fetchOrders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch order by ID
      .addCase(fetchOrderById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrderById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentOrder = action.payload;
      })
      .addCase(fetchOrderById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch order by number
      .addCase(fetchOrderByNumber.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrderByNumber.fulfilled, (state, action) => {
        state.loading = false;
        state.currentOrder = action.payload;
      })
      .addCase(fetchOrderByNumber.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Create order
      .addCase(createOrder.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createOrder.fulfilled, (state, action) => {
        state.loading = false;
        state.currentOrder = action.payload;
      })
      .addCase(createOrder.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Cancel order
      .addCase(cancelOrder.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(cancelOrder.fulfilled, (state, action) => {
        state.loading = false;
        state.currentOrder = action.payload;
        
        // Update the order in the orders list if it exists
        if (state.orders) {
          const index = state.orders.items.findIndex(order => order.id === action.payload.id);
          if (index !== -1) {
            state.orders.items[index] = action.payload;
          }
        }
      })
      .addCase(cancelOrder.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, clearCurrentOrder } = orderSlice.actions;

export const selectOrders = (state: RootState) => state.order.orders;
export const selectCurrentOrder = (state: RootState) => state.order.currentOrder;
export const selectOrderLoading = (state: RootState) => state.order.loading;
export const selectOrderError = (state: RootState) => state.order.error;

export default orderSlice.reducer;
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Address } from '../../types';
import { apiService } from '../../services/api';
import { RootState } from '..';

interface AddressState {
  addresses: Address[] | null;
  loading: boolean;
  error: string | null;
}

const initialState: AddressState = {
  addresses: null,
  loading: false,
  error: null,
};

// Address service functions
const addressService = {
  getAddresses: (): Promise<Address[]> => 
    apiService.get<Address[]>('/addresses'),
    
  getAddressById: (id: string): Promise<Address> => 
    apiService.get<Address>(`/addresses/${id}`),
    
  createAddress: (data: Partial<Address>): Promise<Address> => 
    apiService.post<Address>('/addresses', data),
    
  updateAddress: (id: string, data: Partial<Address>): Promise<Address> => 
    apiService.put<Address>(`/addresses/${id}`, data),
    
  deleteAddress: (id: string): Promise<{ message: string }> => 
    apiService.delete<{ message: string }>(`/addresses/${id}`),
    
  setDefaultAddress: (id: string): Promise<Address> => 
    apiService.post<Address>(`/addresses/${id}/set-default`, {}),
};

export const fetchAddresses = createAsyncThunk(
  'address/fetchAddresses',
  async (_, { rejectWithValue }) => {
    try {
      const response = await addressService.getAddresses();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch addresses');
    }
  }
);

export const fetchAddressById = createAsyncThunk(
  'address/fetchAddressById',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await addressService.getAddressById(id);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch address');
    }
  }
);

export const addAddress = createAsyncThunk(
  'address/addAddress',
  async (addressData: Partial<Address>, { rejectWithValue }) => {
    try {
      const response = await addressService.createAddress(addressData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to add address');
    }
  }
);

export const updateAddress = createAsyncThunk(
  'address/updateAddress',
  async ({ id, ...addressData }: Partial<Address> & { id: string }, { rejectWithValue }) => {
    try {
      const response = await addressService.updateAddress(id, addressData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update address');
    }
  }
);

export const deleteAddress = createAsyncThunk(
  'address/deleteAddress',
  async (id: string, { rejectWithValue }) => {
    try {
      await addressService.deleteAddress(id);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete address');
    }
  }
);

export const setDefaultAddress = createAsyncThunk(
  'address/setDefaultAddress',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await addressService.setDefaultAddress(id);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to set default address');
    }
  }
);

const addressSlice = createSlice({
  name: 'address',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch addresses
      .addCase(fetchAddresses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAddresses.fulfilled, (state, action) => {
        state.loading = false;
        state.addresses = action.payload;
      })
      .addCase(fetchAddresses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Add address
      .addCase(addAddress.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(addAddress.fulfilled, (state, action) => {
        state.loading = false;
        if (state.addresses) {
          state.addresses.push(action.payload);
        } else {
          state.addresses = [action.payload];
        }
      })
      .addCase(addAddress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Update address
      .addCase(updateAddress.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateAddress.fulfilled, (state, action) => {
        state.loading = false;
        if (state.addresses) {
          const index = state.addresses.findIndex(addr => addr.id === action.payload.id);
          if (index !== -1) {
            state.addresses[index] = action.payload;
          }
        }
      })
      .addCase(updateAddress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Delete address
      .addCase(deleteAddress.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteAddress.fulfilled, (state, action) => {
        state.loading = false;
        if (state.addresses) {
          state.addresses = state.addresses.filter(addr => addr.id !== action.payload);
        }
      })
      .addCase(deleteAddress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Set default address
      .addCase(setDefaultAddress.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(setDefaultAddress.fulfilled, (state, action) => {
        state.loading = false;
        if (state.addresses) {
          // Update the is_default flag for all addresses
          state.addresses = state.addresses.map(addr => ({
            ...addr,
            is_default: addr.id === action.payload.id
          }));
        }
      })
      .addCase(setDefaultAddress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError } = addressSlice.actions;

export const selectAddresses = (state: RootState) => state.address.addresses;
export const selectAddressLoading = (state: RootState) => state.address.loading;
export const selectAddressError = (state: RootState) => state.address.error;

export default addressSlice.reducer;
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Brand } from '../../types';
import { brandService } from '../../services/brand.service';
import { RootState } from '..';

interface BrandState {
  brands: Brand[];
  topBrands: Brand[];
  currentBrand: Brand | null;
  loading: boolean;
  error: string | null;
}

const initialState: BrandState = {
  brands: [],
  topBrands: [],
  currentBrand: null,
  loading: false,
  error: null,
};

export const fetchBrands = createAsyncThunk(
  'brand/fetchBrands',
  async (includeInactive: boolean = false, { rejectWithValue }) => {
    try {
      const response = await brandService.getBrands(includeInactive);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch brands');
    }
  }
);

export const fetchTopBrands = createAsyncThunk(
  'brand/fetchTopBrands',
  async (limit: number = 10, { rejectWithValue }) => {
    try {
      const response = await brandService.getTopBrands(limit);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch top brands');
    }
  }
);

export const fetchBrandById = createAsyncThunk(
  'brand/fetchBrandById',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await brandService.getBrandById(id);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch brand');
    }
  }
);

export const fetchBrandBySlug = createAsyncThunk(
  'brand/fetchBrandBySlug',
  async (slug: string, { rejectWithValue }) => {
    try {
      const response = await brandService.getBrandBySlug(slug);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch brand');
    }
  }
);

const brandSlice = createSlice({
  name: 'brand',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentBrand: (state) => {
      state.currentBrand = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch brands
      .addCase(fetchBrands.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBrands.fulfilled, (state, action) => {
        state.loading = false;
        state.brands = action.payload;
      })
      .addCase(fetchBrands.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch top brands
      .addCase(fetchTopBrands.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTopBrands.fulfilled, (state, action) => {
        state.loading = false;
        state.topBrands = action.payload;
      })
      .addCase(fetchTopBrands.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch brand by ID
      .addCase(fetchBrandById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBrandById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentBrand = action.payload;
      })
      .addCase(fetchBrandById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch brand by slug
      .addCase(fetchBrandBySlug.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBrandBySlug.fulfilled, (state, action) => {
        state.loading = false;
        state.currentBrand = action.payload;
      })
      .addCase(fetchBrandBySlug.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, clearCurrentBrand } = brandSlice.actions;

export const selectBrands = (state: RootState) => state.brand.brands;
export const selectTopBrands = (state: RootState) => state.brand.topBrands;
export const selectCurrentBrand = (state: RootState) => state.brand.currentBrand;
export const selectBrandLoading = (state: RootState) => state.brand.loading;
export const selectBrandError = (state: RootState) => state.brand.error;

export default brandSlice.reducer;
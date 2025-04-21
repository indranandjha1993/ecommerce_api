import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Product, ProductList, ProductListItem, ProductSearchQuery, ProductWithRelations } from '../../types';
import { productService } from '../../services/product.service';
import { RootState } from '..';

interface ProductState {
  products: ProductList | null;
  featuredProducts: ProductListItem[];
  newArrivals: ProductListItem[];
  bestsellers: ProductListItem[];
  currentProduct: ProductWithRelations | null;
  searchResults: ProductListItem[];
  loading: boolean;
  error: string | null;
}

const initialState: ProductState = {
  products: null,
  featuredProducts: [],
  newArrivals: [],
  bestsellers: [],
  currentProduct: null,
  searchResults: [],
  loading: false,
  error: null,
};

export const fetchProducts = createAsyncThunk(
  'product/fetchProducts',
  async (params: ProductSearchQuery = {}, { rejectWithValue }) => {
    try {
      const response = await productService.getProducts(params);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch products');
    }
  }
);

export const fetchProductById = createAsyncThunk(
  'product/fetchProductById',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await productService.getProductById(id);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch product');
    }
  }
);

export const fetchProductBySlug = createAsyncThunk(
  'product/fetchProductBySlug',
  async (slug: string, { rejectWithValue }) => {
    try {
      const response = await productService.getProductBySlug(slug);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch product');
    }
  }
);

export const fetchFeaturedProducts = createAsyncThunk(
  'product/fetchFeaturedProducts',
  async (limit: number = 10, { rejectWithValue }) => {
    try {
      const response = await productService.getFeaturedProducts(limit);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch featured products');
    }
  }
);

export const fetchNewArrivals = createAsyncThunk(
  'product/fetchNewArrivals',
  async ({ limit = 10, days = 30 }: { limit?: number; days?: number } = {}, { rejectWithValue }) => {
    try {
      const response = await productService.getNewArrivals(limit, days);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch new arrivals');
    }
  }
);

export const fetchBestsellers = createAsyncThunk(
  'product/fetchBestsellers',
  async (
    { limit = 10, period = 'month' }: { limit?: number; period?: 'week' | 'month' | 'year' | 'all' } = {},
    { rejectWithValue }
  ) => {
    try {
      const response = await productService.getBestsellers(limit, period);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch bestsellers');
    }
  }
);

export const searchProducts = createAsyncThunk(
  'product/searchProducts',
  async ({ query, limit = 10 }: { query: string; limit?: number }, { rejectWithValue }) => {
    try {
      const response = await productService.searchProducts(query, limit);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to search products');
    }
  }
);

const productSlice = createSlice({
  name: 'product',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentProduct: (state) => {
      state.currentProduct = null;
    },
    clearSearchResults: (state) => {
      state.searchResults = [];
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch products
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.products = action.payload;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch product by ID
      .addCase(fetchProductById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProductById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentProduct = action.payload;
      })
      .addCase(fetchProductById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch product by slug
      .addCase(fetchProductBySlug.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProductBySlug.fulfilled, (state, action) => {
        state.loading = false;
        state.currentProduct = action.payload;
      })
      .addCase(fetchProductBySlug.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch featured products
      .addCase(fetchFeaturedProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFeaturedProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.featuredProducts = action.payload;
      })
      .addCase(fetchFeaturedProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch new arrivals
      .addCase(fetchNewArrivals.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchNewArrivals.fulfilled, (state, action) => {
        state.loading = false;
        state.newArrivals = action.payload;
      })
      .addCase(fetchNewArrivals.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch bestsellers
      .addCase(fetchBestsellers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBestsellers.fulfilled, (state, action) => {
        state.loading = false;
        state.bestsellers = action.payload;
      })
      .addCase(fetchBestsellers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Search products
      .addCase(searchProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.searchResults = action.payload;
      })
      .addCase(searchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, clearCurrentProduct, clearSearchResults } = productSlice.actions;

export const selectProducts = (state: RootState) => state.product.products;
export const selectFeaturedProducts = (state: RootState) => state.product.featuredProducts;
export const selectNewArrivals = (state: RootState) => state.product.newArrivals;
export const selectBestsellers = (state: RootState) => state.product.bestsellers;
export const selectCurrentProduct = (state: RootState) => state.product.currentProduct;
export const selectSearchResults = (state: RootState) => state.product.searchResults;
export const selectProductLoading = (state: RootState) => state.product.loading;
export const selectProductError = (state: RootState) => state.product.error;

export default productSlice.reducer;
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Category } from '../../types';
import { categoryService } from '../../services/category.service';
import { RootState } from '..';

interface CategoryState {
  categories: Category[];
  topCategories: Category[];
  currentCategory: Category | null;
  subcategories: Record<string, Category[]>;
  loading: boolean;
  error: string | null;
}

const initialState: CategoryState = {
  categories: [],
  topCategories: [],
  currentCategory: null,
  subcategories: {},
  loading: false,
  error: null,
};

export const fetchCategories = createAsyncThunk(
  'category/fetchCategories',
  async (includeInactive: boolean = false, { rejectWithValue }) => {
    try {
      const response = await categoryService.getCategories(includeInactive);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch categories');
    }
  }
);

export const fetchTopCategories = createAsyncThunk(
  'category/fetchTopCategories',
  async (limit: number = 10, { rejectWithValue }) => {
    try {
      const response = await categoryService.getTopCategories(limit);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch top categories');
    }
  }
);

export const fetchCategoryById = createAsyncThunk(
  'category/fetchCategoryById',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await categoryService.getCategoryById(id);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch category');
    }
  }
);

export const fetchCategoryBySlug = createAsyncThunk(
  'category/fetchCategoryBySlug',
  async (slug: string, { rejectWithValue }) => {
    try {
      const response = await categoryService.getCategoryBySlug(slug);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch category');
    }
  }
);

export const fetchSubcategories = createAsyncThunk(
  'category/fetchSubcategories',
  async ({ parentId, includeInactive = false }: { parentId: string; includeInactive?: boolean }, { rejectWithValue }) => {
    try {
      const response = await categoryService.getSubcategories(parentId, includeInactive);
      return { parentId, subcategories: response };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch subcategories');
    }
  }
);

const categorySlice = createSlice({
  name: 'category',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentCategory: (state) => {
      state.currentCategory = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch categories
      .addCase(fetchCategories.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.loading = false;
        state.categories = action.payload;
      })
      .addCase(fetchCategories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch top categories
      .addCase(fetchTopCategories.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTopCategories.fulfilled, (state, action) => {
        state.loading = false;
        state.topCategories = action.payload;
      })
      .addCase(fetchTopCategories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch category by ID
      .addCase(fetchCategoryById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCategoryById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentCategory = action.payload;
      })
      .addCase(fetchCategoryById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch category by slug
      .addCase(fetchCategoryBySlug.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCategoryBySlug.fulfilled, (state, action) => {
        state.loading = false;
        state.currentCategory = action.payload;
      })
      .addCase(fetchCategoryBySlug.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch subcategories
      .addCase(fetchSubcategories.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSubcategories.fulfilled, (state, action) => {
        state.loading = false;
        state.subcategories = {
          ...state.subcategories,
          [action.payload.parentId]: action.payload.subcategories,
        };
      })
      .addCase(fetchSubcategories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, clearCurrentCategory } = categorySlice.actions;

export const selectCategories = (state: RootState) => state.category.categories;
export const selectTopCategories = (state: RootState) => state.category.topCategories;
export const selectCurrentCategory = (state: RootState) => state.category.currentCategory;
export const selectSubcategories = (parentId: string) => (state: RootState) => 
  state.category.subcategories[parentId] || [];
export const selectCategoryLoading = (state: RootState) => state.category.loading;
export const selectCategoryError = (state: RootState) => state.category.error;

export default categorySlice.reducer;
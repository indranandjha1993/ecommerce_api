import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { User, UserCreate, UserLogin } from '../../types';
import { authService } from '../../services/auth.service';
import { RootState } from '..';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: authService.getCurrentUser(),
  isAuthenticated: authService.isAuthenticated(),
  loading: false,
  error: null,
};

export const register = createAsyncThunk(
  'auth/register',
  async (userData: UserCreate, { rejectWithValue }) => {
    try {
      const response = await authService.register(userData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Registration failed');
    }
  }
);

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: UserLogin, { rejectWithValue }) => {
    try {
      const tokenResponse = await authService.login(credentials);
      
      // Store tokens in localStorage
      localStorage.setItem('access_token', tokenResponse.access_token);
      localStorage.setItem('refresh_token', tokenResponse.refresh_token);
      
      // Get user profile (this would be a separate API call in a real app)
      // For now, we'll just create a mock user object
      const user: User = {
        id: 'user-id', // This would come from decoding the JWT or a separate API call
        email: credentials.email,
        first_name: null,
        last_name: null,
        phone_number: null,
        is_active: true,
        is_superuser: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_login: new Date().toISOString(),
      };
      
      // Store user in localStorage
      authService.setCurrentUser(user);
      
      return user;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Login failed');
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async () => {
    authService.logout();
    return null;
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
      authService.setCurrentUser(action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      // Register
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false;
        // Note: User is not authenticated yet after registration
        // They need to verify email and then login
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.isAuthenticated = false;
      });
  },
});

export const { clearError, setUser } = authSlice.actions;

export const selectAuth = (state: RootState) => state.auth;
export const selectUser = (state: RootState) => state.auth.user;
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated;

export default authSlice.reducer;
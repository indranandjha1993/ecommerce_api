import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { 
  login as loginAction, 
  logout as logoutAction,
  register as registerAction,
  selectAuth,
  selectIsAuthenticated,
  selectUser
} from '../store/slices/authSlice';
import { UserCreate, UserLogin } from '../types';
import { AppDispatch } from '../store';

export const useAuth = () => {
  const dispatch = useDispatch<AppDispatch>();
  const auth = useSelector(selectAuth);
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const user = useSelector(selectUser);

  const login = useCallback(
    async (credentials: UserLogin) => {
      try {
        const resultAction = await dispatch(loginAction(credentials));
        if (loginAction.fulfilled.match(resultAction)) {
          return { success: true };
        } else {
          return { 
            success: false, 
            error: resultAction.payload || 'Login failed' 
          };
        }
      } catch (error) {
        return { success: false, error: 'Login failed' };
      }
    },
    [dispatch]
  );

  const register = useCallback(
    async (userData: UserCreate) => {
      try {
        const resultAction = await dispatch(registerAction(userData));
        if (registerAction.fulfilled.match(resultAction)) {
          return { success: true };
        } else {
          return { 
            success: false, 
            error: resultAction.payload || 'Registration failed' 
          };
        }
      } catch (error) {
        return { success: false, error: 'Registration failed' };
      }
    },
    [dispatch]
  );

  const logout = useCallback(() => {
    dispatch(logoutAction());
  }, [dispatch]);

  return {
    user,
    isAuthenticated,
    login,
    register,
    logout,
    loading: auth.loading,
    error: auth.error,
  };
};
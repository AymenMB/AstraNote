import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, Token, UserLogin, UserCreate } from '@/types';
import { apiClient } from '@/utils/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (credentials: UserLogin) => Promise<void>;
  register: (userData: UserCreate) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  updateUser: (userData: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials: UserLogin) => {
        set({ isLoading: true, error: null });
        
        try {
          // Create form data for OAuth2PasswordRequestForm
          const formData = new FormData();
          formData.append('username', credentials.username);
          formData.append('password', credentials.password);

          const tokenResponse: Token = await apiClient.post('/api/v1/auth/login', formData, {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            },
          });

          // Set auth token
          apiClient.setAuthToken(tokenResponse.access_token);
          
          // Get user info
          const user: User = await apiClient.get('/api/v1/auth/me');

          // Store refresh token in localStorage
          if (typeof window !== 'undefined') {
            localStorage.setItem('refresh_token', tokenResponse.refresh_token);
          }

          set({
            user,
            token: tokenResponse.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });

        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Login failed';
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      register: async (userData: UserCreate) => {
        set({ isLoading: true, error: null });
        
        try {
          const user: User = await apiClient.post('/api/v1/auth/register', userData);
          
          // After successful registration, log the user in
          await get().login({
            username: userData.username,
            password: userData.password,
          });

        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 'Registration failed';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw error;
        }
      },

      logout: () => {
        // Clear API auth
        apiClient.clearAuth();
        
        // Clear local storage
        if (typeof window !== 'undefined') {
          localStorage.removeItem('refresh_token');
        }

        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      },

      checkAuth: async () => {
        const { token } = get();
        
        if (!token) {
          set({ isAuthenticated: false, user: null });
          return;
        }

        set({ isLoading: true });

        try {
          const user: User = await apiClient.get('/api/v1/auth/me');
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          // Token is invalid, logout
          get().logout();
        }
      },

      clearError: () => {
        set({ error: null });
      },

      updateUser: (userData: Partial<User>) => {
        const { user } = get();
        if (user) {
          set({
            user: { ...user, ...userData },
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

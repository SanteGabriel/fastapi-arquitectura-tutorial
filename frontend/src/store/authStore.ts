import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, AuthState, LoginRequest, RegisterRequest } from '@/types';
import axios from 'axios';

interface AuthActions {
  login: (credentials: LoginRequest) => Promise<boolean>;
  register: (data: RegisterRequest) => Promise<boolean>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  updateUser: (user: Partial<User>) => void;
  setLoading: (loading: boolean) => void;
  checkAuth: () => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

const API_BASE_URL = process.env.NEXT_PUBLIC_AUTH_SERVICE_URL || 'http://localhost:8001';

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,

      // Actions
      login: async (credentials: LoginRequest): Promise<boolean> => {
        try {
          set({ loading: true });
          
          const response = await axios.post(`${API_BASE_URL}/login`, credentials);
          const { access_token, user } = response.data;
          
          set({
            token: access_token,
            user,
            isAuthenticated: true,
            loading: false,
          });
          
          // Set axios default header
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          
          return true;
        } catch (error) {
          console.error('Login error:', error);
          set({ loading: false });
          return false;
        }
      },

      register: async (data: RegisterRequest): Promise<boolean> => {
        try {
          set({ loading: true });
          
          const response = await axios.post(`${API_BASE_URL}/register`, data);
          
          if (response.status === 201) {
            set({ loading: false });
            return true;
          }
          
          set({ loading: false });
          return false;
        } catch (error) {
          console.error('Register error:', error);
          set({ loading: false });
          return false;
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          loading: false,
        });
        
        // Remove axios default header
        delete axios.defaults.headers.common['Authorization'];
        
        // Clear localStorage
        localStorage.removeItem('auth-store');
      },

      refreshToken: async (): Promise<boolean> => {
        try {
          const { token } = get();
          if (!token) return false;

          const response = await axios.post(`${API_BASE_URL}/refresh`, {}, {
            headers: { Authorization: `Bearer ${token}` }
          });
          
          const { access_token } = response.data;
          
          set({ token: access_token });
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
          
          return true;
        } catch (error) {
          console.error('Refresh token error:', error);
          get().logout();
          return false;
        }
      },

      updateUser: (userData: Partial<User>) => {
        const { user } = get();
        if (user) {
          set({ user: { ...user, ...userData } });
        }
      },

      setLoading: (loading: boolean) => {
        set({ loading });
      },

      checkAuth: async () => {
        try {
          const { token } = get();
          if (!token) return;

          set({ loading: true });
          
          const response = await axios.get(`${API_BASE_URL}/me`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          
          set({
            user: response.data,
            isAuthenticated: true,
            loading: false,
          });
          
          // Set axios default header
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } catch (error) {
          console.error('Check auth error:', error);
          get().logout();
        }
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

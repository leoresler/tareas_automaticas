import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "./types";
import { authApi } from "./api";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (username_or_email: string, password: string) => Promise<void>;
  register: (
    email: string,
    username: string,
    password: string,
    full_name?: string,
  ) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  setUser: (user: User | null) => void;
  setError: (error: string | null) => void;
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      loading: false,
      error: null,

      setUser: (user) => set({ user, isAuthenticated: !!user }),

      setError: (error) => set({ error }),

      login: async (username_or_email, password) => {
        set({ loading: true, error: null });
        try {
          const response = await authApi.login({ username_or_email, password });
          set({ user: response.user, isAuthenticated: true, loading: false });
        } catch (err: unknown) {
          let errorMessage = "Error al iniciar sesión";
          
          if (err && typeof err === 'object' && 'response' in err) {
            const response = err.response as any;
            
            if (response?.status === 422 && response?.data?.details?.errors) {
              // Errores de validación específicos
              const validationErrors = response.data.details.errors;
              errorMessage = validationErrors.map((e: any) => e.message).join(', ');
            } else if (response?.data?.detail) {
              errorMessage = response.data.detail;
            }
          }
          
          set({ error: errorMessage, loading: false });
          throw err;
        }
      },

      register: async (email, username, password, full_name) => {
        set({ loading: true, error: null });
        try {
          const user = await authApi.register({
            email,
            username,
            password,
            full_name,
          });
          set({ user, isAuthenticated: true, loading: false });
        } catch (err: unknown) {
          let errorMessage = "Error al registrar usuario";
          
          if (err && typeof err === 'object' && 'response' in err) {
            const response = err.response as any;
            
            if (response?.status === 422 && response?.data?.details?.errors) {
              // Errores de validación específicos
              const validationErrors = response.data.details.errors;
              errorMessage = validationErrors.map((e: any) => e.message).join(', ');
            } else if (response?.data?.detail) {
              errorMessage = response.data.detail;
            }
          }
          
          set({ error: errorMessage, loading: false });
          throw err;
        }
      },

      logout: async () => {
        set({ loading: true });
        try {
          await authApi.logout();
        } finally {
          set({ user: null, isAuthenticated: false, loading: false });
        }
      },

      checkAuth: async () => {
        set({ loading: true });
        try {
          const user = await authApi.getCurrentUser();
          set({ user, isAuthenticated: true, loading: false });
        } catch (error) {
          set({ user: null, isAuthenticated: false, loading: false });
          
          localStorage.removeItem("auth-storage");
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);

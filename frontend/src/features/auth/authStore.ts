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
          const errorMessage =
            (err as { response?: { data?: { detail?: string } } })?.response
              ?.data?.detail || "Error al iniciar sesión";
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
          const errorMessage =
            (err as { response?: { data?: { detail?: string } } })?.response
              ?.data?.detail || "Error al registrar usuario";
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

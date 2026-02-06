import axios from 'axios'
import type { User, LoginRequest, RegisterRequest, LoginResponse } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
})

let isRedirecting = false
let isRefreshing = false

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    const isAuthEndpoint = originalRequest.url?.includes('/auth/')
    
    if (error.response?.status === 401 && !isRedirecting && !originalRequest._retry && !isAuthEndpoint) {
      if (!isRefreshing) {
        isRefreshing = true
        originalRequest._retry = true

        try {
          await axios.post(`${API_BASE_URL}/auth/refresh`, {}, { withCredentials: true })
          isRefreshing = false
          return api(originalRequest)
        } catch (refreshError) {
          isRefreshing = false
          isRedirecting = true
          
          localStorage.removeItem('auth-storage')
          
          window.location.href = '/login'
          setTimeout(() => {
            isRedirecting = false
          }, 1000)
          return Promise.reject(refreshError)
        }
      }
    }

    return Promise.reject(error)
  }
)

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', data)
    return response.data
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post<User>('/auth/register', data)
    return response.data
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout')
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  refreshToken: async (): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/refresh')
    return response.data
  },
}

export default api

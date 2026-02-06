import api from '../auth/api'
import type { Task, TaskCreate, TaskUpdate, TaskFilters, TaskHistory } from './types'

export const tasksApi = {
  getAll: async (filters?: TaskFilters): Promise<Task[]> => {
    const params = new URLSearchParams()
    if (filters?.skip) params.append('skip', filters.skip.toString())
    if (filters?.limit) params.append('limit', filters.limit.toString())
    if (filters?.status) params.append('status', filters.status)
    if (filters?.is_sent !== undefined) params.append('is_sent', filters.is_sent.toString())
    if (filters?.tags) params.append('tags', filters.tags)
    if (filters?.date_from) params.append('date_from', filters.date_from)
    if (filters?.date_to) params.append('date_to', filters.date_to)

    const response = await api.get<Task[]>(`/tasks?${params.toString()}`)
    return response.data
  },

  getById: async (id: number): Promise<Task> => {
    const response = await api.get<Task>(`/tasks/${id}`)
    return response.data
  },

  create: async (data: TaskCreate): Promise<Task> => {
    const response = await api.post<Task>('/tasks', data)
    return response.data
  },

  update: async (id: number, data: TaskUpdate): Promise<Task> => {
    const response = await api.put<Task>(`/tasks/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/tasks/${id}`)
  },

  updateStatus: async (id: number, status: Task['status']): Promise<Task> => {
    const response = await api.put<Task>(`/tasks/${id}/status`, { status })
    return response.data
  },

  search: async (query: string): Promise<Task[]> => {
    const response = await api.get<Task[]>(`/tasks/search?q=${encodeURIComponent(query)}`)
    return response.data
  },

  getHistory: async (id: number): Promise<TaskHistory[]> => {
    const response = await api.get<TaskHistory[]>(`/tasks/${id}/history`)
    return response.data
  },
}

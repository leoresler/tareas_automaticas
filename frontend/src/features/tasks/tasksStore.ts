import { create } from 'zustand'
import type { Task, TaskCreate, TaskUpdate, TaskFilters } from './types'
import { tasksApi } from './api'

interface TaskState {
  tasks: Task[]
  currentTask: Task | null
  loading: boolean
  error: string | null
  filters: TaskFilters

  fetchTasks: (filters?: TaskFilters) => Promise<void>
  fetchTaskById: (id: number) => Promise<void>
  createTask: (data: TaskCreate) => Promise<void>
  updateTask: (id: number, data: TaskUpdate) => Promise<void>
  deleteTask: (id: number) => Promise<void>
  updateTaskStatus: (id: number, status: Task['status']) => Promise<void>
  setCurrentTask: (task: Task | null) => void
  setFilters: (filters: TaskFilters) => void
  clearError: () => void
}

export const useTaskStore = create<TaskState>((set) => ({
  tasks: [],
  currentTask: null,
  loading: false,
  error: null,
  filters: { limit: 100 },

  setCurrentTask: (task) => set({ currentTask: task }),

  setFilters: (filters) => set({ filters }),

  clearError: () => set({ error: null }),

  fetchTasks: async (filters) => {
    set({ loading: true, error: null })
    try {
      const tasks = await tasksApi.getAll(filters)
      set({ tasks, loading: false })
    } catch (err: unknown) {
      const error = err as { response?: { status?: number } }
      if (error.response?.status === 401) {
        set({ loading: false })
        throw err
      }
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar tareas'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },

  fetchTaskById: async (id) => {
    set({ loading: true, error: null })
    try {
      const task = await tasksApi.getById(id)
      set({ currentTask: task, loading: false })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al cargar tarea'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },

  createTask: async (data) => {
    set({ loading: true, error: null })
    try {
      const newTask = await tasksApi.create(data)
      set((state) => ({
        tasks: [...state.tasks, newTask],
        loading: false,
      }))
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al crear tarea'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },

  updateTask: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const updatedTask = await tasksApi.update(id, data)
      set((state) => ({
        tasks: state.tasks.map((t) => (t.id === id ? updatedTask : t)),
        currentTask: state.currentTask?.id === id ? updatedTask : state.currentTask,
        loading: false,
      }))
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al actualizar tarea'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },

  deleteTask: async (id) => {
    set({ loading: true, error: null })
    try {
      await tasksApi.delete(id)
      set((state) => ({
        tasks: state.tasks.filter((t) => t.id !== id),
        currentTask: state.currentTask?.id === id ? null : state.currentTask,
        loading: false,
      }))
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al eliminar tarea'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },

  updateTaskStatus: async (id, status) => {
    set({ loading: true, error: null })
    try {
      const updatedTask = await tasksApi.updateStatus(id, status)
      set((state) => ({
        tasks: state.tasks.map((t) => (t.id === id ? updatedTask : t)),
        currentTask: state.currentTask?.id === id ? updatedTask : state.currentTask,
        loading: false,
      }))
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al actualizar estado'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },
}))

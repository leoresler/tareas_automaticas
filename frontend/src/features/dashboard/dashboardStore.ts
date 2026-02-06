import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { dashboardApi } from './dashboardApi'
import type { 
  DashboardStats, 
  TaskStatusData, 
  TaskMonthData, 
  DashboardTask 
} from './dashboardApi'

// ============================================
// INTERFACES
// ============================================
interface DashboardState {
  // Estado
  loading: boolean
  error: string | null
  
  // Datos
  stats: DashboardStats | null
  tasksByStatus: TaskStatusData[]
  tasksByMonth: TaskMonthData[]
  recentTasks: DashboardTask[]
  todayTasks: DashboardTask[]
  
  // Última actualización
  lastFetched: number | null
}

interface DashboardActions {
  // Acciones de carga
  fetchStats: () => Promise<void>
  fetchTasksByStatus: () => Promise<void>
  fetchTasksByMonth: (months?: number) => Promise<void>
  fetchRecentTasks: (limit?: number) => Promise<void>
  fetchTodayTasks: () => Promise<void>
  
  // Cargar todos los datos
  fetchAllDashboardData: () => Promise<void>
  
  // Reset
  resetDashboard: () => void
  
  // Acciones de estado
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

// ============================================
// STORE
// ============================================
type DashboardStore = DashboardState & DashboardActions

const initialState: DashboardState = {
  loading: false,
  error: null,
  stats: null,
  tasksByStatus: [],
  tasksByMonth: [],
  recentTasks: [],
  todayTasks: [],
  lastFetched: null,
}

export const useDashboardStore = create<DashboardStore>()(
  devtools(
    (set) => ({
      ...initialState,
      
      // ============================================
      // ACCIONES DE CARGA
      // ============================================
      fetchStats: async () => {
        try {
          set({ loading: true, error: null })
          console.log('🔄 Fetching dashboard stats...')
          const stats = await dashboardApi.getStats()
          console.log('✅ Dashboard stats loaded:', stats)
          set({ stats, loading: false })
        } catch (error) {
          console.error('❌ Error fetching dashboard stats:', error)
          const errorMessage = error instanceof Error ? error.message : 'Error al cargar estadísticas'
          set({ error: errorMessage, loading: false })
        }
      },
      
      fetchTasksByStatus: async () => {
        try {
          set({ loading: true, error: null })
          const tasksByStatus = await dashboardApi.getTasksByStatus()
          set({ tasksByStatus, loading: false })
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Error al cargar tareas por estado'
          set({ error: errorMessage, loading: false })
        }
      },
      
      fetchTasksByMonth: async (months = 6) => {
        try {
          set({ loading: true, error: null })
          const tasksByMonth = await dashboardApi.getTasksByMonth(months)
          set({ tasksByMonth, loading: false })
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Error al cargar tareas por mes'
          set({ error: errorMessage, loading: false })
        }
      },
      
      fetchRecentTasks: async (limit = 10) => {
        try {
          set({ loading: true, error: null })
          const recentTasks = await dashboardApi.getRecentTasks(limit)
          set({ recentTasks, loading: false })
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Error al cargar tareas recientes'
          set({ error: errorMessage, loading: false })
        }
      },
      
      fetchTodayTasks: async () => {
        try {
          set({ loading: true, error: null })
          const todayTasks = await dashboardApi.getTodayTasks()
          set({ todayTasks, loading: false })
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Error al cargar tareas de hoy'
          set({ error: errorMessage, loading: false })
        }
      },
      
      // ============================================
      // CARGAR TODOS LOS DATOS
      // ============================================
      fetchAllDashboardData: async () => {
        try {
          set({ loading: true, error: null })
          console.log('🔄 Fetching all dashboard data...')
          
          // Ejecutar todas las peticiones en paralelo
          const [
            stats,
            tasksByStatus,
            tasksByMonth,
            recentTasks,
            todayTasks
          ] = await Promise.all([
            dashboardApi.getStats(),
            dashboardApi.getTasksByStatus(),
            dashboardApi.getTasksByMonth(6),
            dashboardApi.getRecentTasks(10),
            dashboardApi.getTodayTasks()
          ])
          
          console.log('✅ All dashboard data loaded:', { stats, tasksByStatus, tasksByMonth })
          set({
            stats,
            tasksByStatus,
            tasksByMonth,
            recentTasks,
            todayTasks,
            loading: false,
            lastFetched: Date.now()
          })
        } catch (error) {
          console.error('❌ Error fetching all dashboard data:', error)
          const errorMessage = error instanceof Error ? error.message : 'Error al cargar datos del dashboard'
          set({ error: errorMessage, loading: false })
        }
      },
      
      // ============================================
      // RESET
      // ============================================
      resetDashboard: () => {
        set(initialState)
      },
      
      // ============================================
      // ACCIONES DE ESTADO
      // ============================================
      setLoading: (loading: boolean) => {
        set({ loading })
      },
      
      setError: (error: string | null) => {
        set({ error })
      }
    }),
    {
      name: 'dashboard-store'
    }
  )
)

// ============================================
// SELECTORS
// ============================================
export const useDashboardStats = () => useDashboardStore((state) => state.stats)
export const useDashboardLoading = () => useDashboardStore((state) => state.loading)
export const useDashboardError = () => useDashboardStore((state) => state.error)
export const useTasksByStatus = () => useDashboardStore((state) => state.tasksByStatus)
export const useTasksByMonth = () => useDashboardStore((state) => state.tasksByMonth)
export const useRecentTasks = () => useDashboardStore((state) => state.recentTasks)
export const useTodayTasks = () => useDashboardStore((state) => state.todayTasks)
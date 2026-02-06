import api from '../auth/api'

// ============================================
// TYPES
// ============================================
export interface DashboardStats {
  total_tasks: number
  pending_count: number
  in_progress_count: number
  completed_count: number
  today_tasks: number
  overdue_count: number
  week_completed: number
  completion_rate: number
}

export interface TaskStatusData {
  status: string
  count: number
  color: string
}

export interface TaskMonthData {
  month: string
  count: number
}

export interface DashboardTask {
  id: number
  user_id: number
  title: string
  description: string | null
  scheduled_datetime: string
  status: 'pendiente' | 'en_progreso' | 'finalizado' | 'enviada' | 'cancelada'
  tags: string | null
  tags_list: string[]
  is_sent: boolean
  sent_at: string | null
  is_active: boolean
  created_by_ai: boolean
  created_at: string
  updated_at: string | null
  history_count: number
  is_overdue?: boolean
}

// ============================================
// API FUNCTIONS
// ============================================
export const dashboardApi = {
  // Obtener estadísticas generales
  async getStats(): Promise<DashboardStats> {
    const response = await api.get('/dashboard/stats')
    return response.data.data
  },

  // Obtener distribución de tareas por estado
  async getTasksByStatus(): Promise<TaskStatusData[]> {
    const response = await api.get('/dashboard/tasks-by-status')
    return response.data.data
  },

  // Obtener distribución de tareas por mes
  async getTasksByMonth(months = 6): Promise<TaskMonthData[]> {
    const response = await api.get('/dashboard/tasks-by-month', {
      params: { months }
    })
    return response.data.data
  },

  // Obtener tareas recientes
  async getRecentTasks(limit: number): Promise<DashboardTask[]> {
    const res = await api.get(`/dashboard/recent-tasks?limit=${limit}`)
    return res.data.data ?? []
  },
  // async getRecentTasks(limit = 10): Promise<DashboardTask[]> {
  //   const response = await api.get('/dashboard/recent-tasks', {
  //     params: { limit }
  //   })
  //   return response.data
  // },

  // Obtener tareas de hoy
  async getTodayTasks(): Promise<DashboardTask[]> {
    const response = await api.get('/dashboard/today-tasks')
    return response.data.data
  }
}
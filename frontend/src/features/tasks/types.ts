export interface Task {
  id: number
  user_id: number
  title: string
  description: string | null
  scheduled_datetime: string
  status: TaskStatus
  tags: string | null
  tags_list: string[]
  is_sent: boolean
  sent_at: string | null
  is_active: boolean
  created_by_ai: boolean
  created_at: string
  updated_at: string | null
  history_count: number
  contacts?: Contact[]
}

export type TaskStatus = 'pendiente' | 'en_progreso' | 'finalizado' | 'enviada' | 'cancelada'

export interface Contact {
  id: number
  user_id: number
  name: string
  channel_type: string
  channel_value: string
  is_active: boolean
  created_at: string
  updated_at: string | null
}

export interface TaskCreate {
  title: string
  description?: string
  scheduled_datetime: string
  tags?: string[]
  contact_ids: number[]
}

export interface TaskUpdate {
  title?: string
  description?: string
  scheduled_datetime?: string
  status?: TaskStatus
  tags?: string
  is_sent?: boolean
}

export interface TaskFilters {
  skip?: number
  limit?: number
  status?: TaskStatus
  is_sent?: boolean
  tags?: string
  date_from?: string
  date_to?: string
}

export interface TaskHistory {
  id: number
  task_id: number
  field: string
  old_value: string | null
  new_value: string | null
  changed_at: string
  changed_by_user_id: number | null
}

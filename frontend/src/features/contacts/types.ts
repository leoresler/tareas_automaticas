export interface Contact {
  id: number
  user_id: number
  name: string
  channel_type: 'whatsapp' | 'email' | 'telegram'
  channel_value: string
  is_active: boolean
  created_at: string
  updated_at: string | null
}

export interface ContactCreate {
  name: string
  channel_type: 'whatsapp' | 'email' | 'telegram'
  channel_value: string
  is_active?: boolean
}

export interface ContactUpdate {
  name?: string
  channel_type?: 'whatsapp' | 'email' | 'telegram'
  channel_value?: string
  is_active?: boolean
}

export interface ContactFilters {
  search?: string
  channel_type?: string
  status?: string
  limit?: number
  offset?: number
}
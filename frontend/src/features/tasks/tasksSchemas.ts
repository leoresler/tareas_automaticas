export const taskCreateSchema = {
  title: { label: 'Título', required: true, minLength: 3, maxLength: 200 },
  description: { label: 'Descripción', maxLength: 2000, optional: true },
  scheduled_datetime: { label: 'Fecha y hora', required: true },
  tags: { label: 'Etiquetas', type: 'array', items: { type: 'string' }, optional: true },
  contact_ids: { label: 'Contactos', required: true, type: 'array', items: { type: 'number' }, minItems: 1 },
}

export const taskUpdateSchema = {
  title: { label: 'Título', required: false, minLength: 3, maxLength: 200 },
  description: { label: 'Descripción', maxLength: 2000, optional: true },
  scheduled_datetime: { label: 'Fecha y hora', required: false },
  status: { enum: ['pendiente', 'en_progreso', 'finalizado', 'enviada', 'cancelada'], optional: true },
  tags: { label: 'Etiquetas', type: 'array', items: { type: 'string' }, optional: true },
  is_sent: { label: 'Enviada', type: 'boolean', optional: true },
}

export type TaskCreateInput = {
  title: string
  description?: string
  scheduled_datetime: string
  tags?: string[]
  contact_ids: number[]
}

export type TaskUpdateInput = {
  title?: string
  description?: string
  scheduled_datetime?: string
  status?: 'pendiente' | 'en_progreso' | 'finalizado' | 'enviada' | 'cancelada'
  tags?: string[]
  is_sent?: boolean
}
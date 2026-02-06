import api from '../auth/api'
import type { Contact, ContactCreate, ContactUpdate } from './types'

export const contactsApi = {
  // Obtener todos los contactos del usuario
  async getAll(): Promise<Contact[]> {
    const response = await api.get<Contact[]>('/contacts')
    return response.data
  },

  // Obtener contacto por ID
  async getById(id: number): Promise<Contact> {
    const response = await api.get<Contact>(`/contacts/${id}`)
    return response.data
  },

  // Crear nuevo contacto
  async create(data: ContactCreate): Promise<Contact> {
    const response = await api.post<Contact>('/contacts', data)
    return response.data
  },

  // Actualizar contacto existente
  async update(id: number, data: ContactUpdate): Promise<Contact> {
    const response = await api.put<Contact>(`/contacts/${id}`, data)
    return response.data
  },

  // Eliminar contacto (soft delete)
  async delete(id: number): Promise<void> {
    await api.delete(`/contacts/${id}`)
  },

  // Buscar contactos
  async search(query: string): Promise<Contact[]> {
    const response = await api.get<Contact[]>('/contacts', {
      params: { search: query }
    })
    return response.data
  }
}

export default contactsApi
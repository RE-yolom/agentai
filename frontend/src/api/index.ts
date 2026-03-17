import axios from 'axios'
import type { Message, Document, Session, ChatResponse } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

export const chatApi = {
  sendMessage(message: string, sessionId?: string): Promise<ChatResponse> {
    return api.post('/chat', { message, session_id: sessionId }).then(res => res.data)
  },

  getSessions(): Promise<Session[]> {
    return api.get('/sessions').then(res => res.data.data || [])
  },

  getSession(id: string): Promise<Session> {
    return api.get(`/sessions/${id}`).then(res => res.data.data)
  },

  deleteSession(id: string): Promise<void> {
    return api.delete(`/sessions/${id}`)
  },

  createSession(name: string): Promise<Session> {
    return api.post('/sessions', { name }).then(res => res.data.data)
  }
}

export const documentApi = {
  getDocuments(): Promise<Document[]> {
    return api.get('/documents').then(res => res.data.data || [])
  },

  uploadDocument(file: File): Promise<Document> {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(res => res.data.data)
  },

  deleteDocument(id: string): Promise<void> {
    return api.delete(`/documents/${id}`)
  }
}

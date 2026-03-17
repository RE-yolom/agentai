import axios from 'axios'
import type { Message, Document, Session, ChatResponse } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

export const chatApi = {
  sendMessage(message: string, sessionId?: string): Promise<ChatResponse> {
    return api.post('/chat', { message, session_id: sessionId })
  },

  getSessions(): Promise<Session[]> {
    return api.get('/sessions')
  },

  getSession(id: string): Promise<Session> {
    return api.get(`/sessions/${id}`)
  },

  deleteSession(id: string): Promise<void> {
    return api.delete(`/sessions/${id}`)
  },

  createSession(name: string): Promise<Session> {
    return api.post('/sessions', { name })
  }
}

export const documentApi = {
  getDocuments(): Promise<Document[]> {
    return api.get('/documents')
  },

  uploadDocument(file: File): Promise<Document> {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  deleteDocument(id: string): Promise<void> {
    return api.delete(`/documents/${id}`)
  }
}

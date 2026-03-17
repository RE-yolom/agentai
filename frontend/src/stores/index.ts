import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Message, Session, Document } from '@/types'
import { chatApi, documentApi } from '@/api'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<string | null>(null)
  const isLoading = ref(false)

  const addMessage = (message: Message) => {
    messages.value.push(message)
  }

  const clearMessages = () => {
    messages.value = []
  }

  const sendMessage = async (content: string) => {
    isLoading.value = true
    try {
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content,
        timestamp: Date.now()
      }
      addMessage(userMessage)

      const response = await chatApi.sendMessage(content, currentSessionId.value || undefined)

      if (response.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.data.reply,
          timestamp: Date.now(),
          sources: response.data.sources
        }
        addMessage(assistantMessage)

        // Refresh sessions after chat
        await loadSessions()
      }

      return response
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '抱歉，发生错误，请稍后重试。',
        timestamp: Date.now()
      }
      addMessage(errorMessage)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const loadSessions = async () => {
    try {
      sessions.value = await chatApi.getSessions()
    } catch (error) {
      console.error('Failed to load sessions:', error)
    }
  }

  const createNewSession = async (name: string = '新会话') => {
    try {
      const session = await chatApi.createSession(name)
      sessions.value.unshift(session)
      currentSessionId.value = session.id
      clearMessages()
      return session
    } catch (error) {
      console.error('Failed to create session:', error)
      throw error
    }
  }

  const selectSession = async (sessionId: string) => {
    currentSessionId.value = sessionId
    // Load session messages (implementation depends on backend)
    clearMessages()
  }

  const deleteSessionById = async (sessionId: string) => {
    try {
      await chatApi.deleteSession(sessionId)
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      if (currentSessionId.value === sessionId) {
        currentSessionId.value = null
        clearMessages()
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
      throw error
    }
  }

  return {
    messages,
    sessions,
    currentSessionId,
    isLoading,
    sendMessage,
    loadSessions,
    createNewSession,
    selectSession,
    deleteSessionById
  }
})

export const useDocumentStore = defineStore('document', () => {
  const documents = ref<Document[]>([])
  const isUploading = ref(false)

  const loadDocuments = async () => {
    try {
      documents.value = await documentApi.getDocuments()
    } catch (error) {
      console.error('Failed to load documents:', error)
    }
  }

  const uploadDocument = async (file: File) => {
    isUploading.value = true
    try {
      const doc = await documentApi.uploadDocument(file)
      documents.value.unshift(doc)
      return doc
    } catch (error) {
      console.error('Failed to upload document:', error)
      throw error
    } finally {
      isUploading.value = false
    }
  }

  const deleteDocumentById = async (docId: string) => {
    try {
      await documentApi.deleteDocument(docId)
      documents.value = documents.value.filter(d => d.id !== docId)
    } catch (error) {
      console.error('Failed to delete document:', error)
      throw error
    }
  }

  return {
    documents,
    isUploading,
    loadDocuments,
    uploadDocument,
    deleteDocumentById
  }
})

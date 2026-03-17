export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  sources?: Source[]
}

export interface Source {
  doc_id: string
  content: string
  score: number
}

export interface Session {
  id: string
  name: string
  created_at: string
  updated_at: string
}

export interface Document {
  id: string
  filename: string
  file_type: string
  upload_time: string
  status: 'processing' | 'completed' | 'failed'
}

export interface ChatResponse {
  success: boolean
  data: {
    reply: string
    sources?: Source[]
  }
  error?: string
}

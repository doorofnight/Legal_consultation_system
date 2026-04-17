export interface ChatMessage {
  id: number
  session_id: number
  role: string  // 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

export interface ChatSession {
  id: number
  title: string
  model_provider: string  // 'siliconflow' | 'ollama'
  created_at: string
  updated_at?: string
  message_count?: number  // 会话中的消息数量
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[]
}

export interface ChatSessionCreate {
  title: string
  model_provider: string
}

export interface ChatSessionUpdate {
  title?: string
  model_provider?: string
}

export interface ChatRequest {
  message: string
  session_id?: number
  model_provider?: string
}

export interface ChatResponse {
  session_id: number
  message_id: number
  content: string
  created_at: string
}
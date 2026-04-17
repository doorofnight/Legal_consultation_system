import axios from 'axios'
import type {
  ChatSession,
  ChatSessionCreate,
  ChatSessionUpdate,
  ChatSessionDetail,
  ChatMessage,
  ChatRequest,
  ChatResponse
} from '@/types/chat'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000, // 增加超时时间到120秒（2分钟），因为AI聊天和调查表分析可能需要较长时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 聊天会话API
export const chatApi = {
  // 获取会话列表
  getSessions: async (skip: number = 0, limit: number = 100): Promise<ChatSession[]> => {
    const response = await api.get('/chat/sessions', {
      params: { skip, limit }
    })
    return response.data
  },

  // 创建会话
  createSession: async (sessionData: ChatSessionCreate): Promise<ChatSession> => {
    const response = await api.post('/chat/sessions', sessionData)
    return response.data
  },

  // 获取会话详情
  getSession: async (sessionId: number): Promise<ChatSessionDetail> => {
    const response = await api.get(`/chat/sessions/${sessionId}`)
    return response.data
  },

  // 更新会话
  updateSession: async (sessionId: number, updateData: ChatSessionUpdate): Promise<ChatSession> => {
    const response = await api.put(`/chat/sessions/${sessionId}`, updateData)
    return response.data
  },

  // 删除会话
  deleteSession: async (sessionId: number): Promise<void> => {
    await api.delete(`/chat/sessions/${sessionId}`)
  },

  // 获取会话消息
  getSessionMessages: async (sessionId: number, skip: number = 0, limit: number = 100): Promise<ChatMessage[]> => {
    const response = await api.get(`/chat/sessions/${sessionId}/messages`, {
      params: { skip, limit }
    })
    return response.data
  },

  // 发送聊天消息（非流式）
  sendMessage: async (chatRequest: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/chat', chatRequest)
    return response.data
  },

  // 发送流式聊天消息
  sendMessageStream: async (chatRequest: ChatRequest, onChunk: (chunk: any) => void, onComplete: (response: any) => void, onError: (error: any) => void): Promise<void> => {
    try {
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(chatRequest)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Response body is not readable')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        
        // 按行分割处理SSE格式
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留未完成的行

        for (const line of lines) {
          const trimmedLine = line.trim()
          if (trimmedLine.startsWith('data: ')) {
            const dataStr = trimmedLine.slice(6) // 移除"data: "前缀
            if (dataStr === '[DONE]') continue
            
            try {
              const data = JSON.parse(dataStr)
              onChunk(data)
            } catch (e) {
              console.error('Failed to parse SSE data:', e, 'Data:', dataStr)
            }
          }
        }
      }

      // 处理剩余的buffer
      if (buffer.trim().startsWith('data: ')) {
        const dataStr = buffer.trim().slice(6)
        if (dataStr !== '[DONE]') {
          try {
            const data = JSON.parse(dataStr)
            onChunk(data)
          } catch (e) {
            console.error('Failed to parse remaining SSE data:', e)
          }
        }
      }

      onComplete({ success: true })
    } catch (error) {
      console.error('Streaming request failed:', error)
      onError(error)
    }
  }
}

export default chatApi
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

  // 发送聊天消息
  sendMessage: async (chatRequest: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/chat/chat', chatRequest)
    return response.data
  }
}

export default chatApi
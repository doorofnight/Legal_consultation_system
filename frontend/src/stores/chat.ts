import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatSession, ChatMessage, ChatSessionDetail } from '@/types/chat'
import { chatApi } from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const sessions = ref<ChatSession[]>([])
  const currentSession = ref<ChatSessionDetail | null>(null)
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const hasSessions = computed(() => sessions.value.length > 0)
  const hasMessages = computed(() => messages.value.length > 0)
  const currentSessionId = computed(() => currentSession.value?.id || null)

  // 获取会话列表
  const fetchSessions = async () => {
    try {
      isLoading.value = true
      error.value = null
      sessions.value = await chatApi.getSessions()
    } catch (err: any) {
      error.value = err.message || '获取会话列表失败'
      console.error('获取会话列表失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  // 创建会话
  const createSession = async (title: string = '新对话', modelProvider: string = 'siliconflow') => {
    try {
      isLoading.value = true
      error.value = null
      const session = await chatApi.createSession({
        title,
        model_provider: modelProvider
      })
      sessions.value.unshift(session)
      return session
    } catch (err: any) {
      error.value = err.message || '创建会话失败'
      console.error('创建会话失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 获取会话详情
  const fetchSession = async (sessionId: number) => {
    try {
      isLoading.value = true
      error.value = null
      const sessionDetail = await chatApi.getSession(sessionId)
      currentSession.value = sessionDetail
      messages.value = sessionDetail.messages
      return sessionDetail
    } catch (err: any) {
      error.value = err.message || '获取会话详情失败'
      console.error('获取会话详情失败:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 发送消息
  const sendMessage = async (message: string, sessionId?: number, modelProvider?: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      // 添加用户消息到本地
      const userMessage: ChatMessage = {
        id: Date.now(), // 临时ID
        session_id: sessionId || currentSessionId.value || 0,
        role: 'user',
        content: message,
        created_at: new Date().toISOString()
      }
      messages.value.push(userMessage)
      
      // 发送到服务器
      const response = await chatApi.sendMessage({
        message,
        session_id: sessionId || currentSessionId.value || undefined,
        model_provider: modelProvider
      })
      
      // 添加AI回复到本地
      const aiMessage: ChatMessage = {
        id: response.message_id,
        session_id: response.session_id,
        role: 'assistant',
        content: response.content,
        created_at: response.created_at
      }
      messages.value.push(aiMessage)
      
      // 如果当前会话为空，更新会话
      if (!currentSession.value && response.session_id) {
        await fetchSession(response.session_id)
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || '发送消息失败'
      console.error('发送消息失败:', err)
      // 移除临时消息
      messages.value = messages.value.filter(msg => msg.id !== Date.now())
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 清空当前会话
  const clearCurrentSession = () => {
    currentSession.value = null
    messages.value = []
  }

  // 删除会话
  const deleteSession = async (sessionId: number) => {
    try {
      await chatApi.deleteSession(sessionId)
      sessions.value = sessions.value.filter(session => session.id !== sessionId)
      if (currentSession.value?.id === sessionId) {
        clearCurrentSession()
      }
    } catch (err: any) {
      error.value = err.message || '删除会话失败'
      console.error('删除会话失败:', err)
      throw err
    }
  }

  // 更新会话标题
  const updateSessionTitle = async (sessionId: number, title: string) => {
    try {
      const updatedSession = await chatApi.updateSession(sessionId, { title })
      const index = sessions.value.findIndex(s => s.id === sessionId)
      if (index !== -1) {
        sessions.value[index] = updatedSession
      }
      if (currentSession.value?.id === sessionId) {
        currentSession.value.title = title
      }
    } catch (err: any) {
      error.value = err.message || '更新会话标题失败'
      console.error('更新会话标题失败:', err)
      throw err
    }
  }

  // 更新会话模型提供商
  const updateSessionModel = async (sessionId: number, modelProvider: string) => {
    try {
      const updatedSession = await chatApi.updateSession(sessionId, { model_provider: modelProvider })
      const index = sessions.value.findIndex(s => s.id === sessionId)
      if (index !== -1) {
        sessions.value[index] = updatedSession
      }
      if (currentSession.value?.id === sessionId) {
        currentSession.value.model_provider = modelProvider
      }
    } catch (err: any) {
      error.value = err.message || '更新会话模型失败'
      console.error('更新会话模型失败:', err)
      throw err
    }
  }

  return {
    // 状态
    sessions,
    currentSession,
    messages,
    isLoading,
    error,
    
    // 计算属性
    hasSessions,
    hasMessages,
    currentSessionId,
    
    // 方法
    fetchSessions,
    createSession,
    fetchSession,
    sendMessage,
    clearCurrentSession,
    deleteSession,
    updateSessionTitle,
    updateSessionModel
  }
})
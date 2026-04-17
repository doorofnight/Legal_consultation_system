<template>
  <div class="legal-ai-container">
    <!-- 顶部导航栏 -->
    <header class="top-nav">
      <div class="nav-brand">
        <div class="header-left">
          <el-icon class="page-title-icon"><ChatDotRound /></el-icon>
        </div>
        <div class="brand-text">
          <h1>智能法律顾问</h1>
          <span>专业 · 精准 · 高效</span>
        </div>
      </div>

      <div class="nav-actions">
        <div v-if="currentModelProvider" class="model-badge" :class="currentModelProvider">
          <span class="model-dot"></span>
          {{ currentModelProvider === 'siliconflow' ? '云端模型' : '本地模型' }}
        </div>
        <div v-else class="model-badge loading">
          <span class="model-dot"></span>
          加载中...
        </div>

        <button class="new-chat-btn" @click="newChat">
          <el-icon :size="16"><Plus /></el-icon>
          新对话
        </button>
      </div>
    </header>

    <div class="main-layout">
      <!-- 左侧边栏 -->
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <button class="toggle-btn" @click="sidebarCollapsed = !sidebarCollapsed">
            <el-icon :size="16">
              <ArrowLeft v-if="!sidebarCollapsed" />
              <ArrowRight v-else />
            </el-icon>
          </button>
          <span class="session-label">历史会话</span>
        </div>

        <div class="sessions-list">
          <div
            v-for="session in chatStore.sessions"
            :key="session.id"
            class="session-item"
            :class="{ active: chatStore.currentSession?.id === session.id }"
            :data-title="session.title"
            @click="selectSession(session.id)"
          >
            <div class="session-icon">
              <el-icon :size="16"><ChatDotRound /></el-icon>
            </div>
            <div class="session-info">
              <span class="session-title">{{ session.title }}</span>
              <span class="session-time">{{ formatDate(session.updated_at) }}</span>
            </div>
            <button class="delete-btn" @click.stop="deleteSession(session.id)">
              <el-icon :size="14"><Close /></el-icon>
            </button>
          </div>

          <div v-if="!chatStore.sessions.length" class="empty-state">
            <p>暂无会话记录</p>
          </div>
        </div>

        <div class="sidebar-footer">
          <div class="user-profile">
            <div class="avatar">用</div>
            <span>专业版用户</span>
          </div>
        </div>
      </aside>

      <!-- 主聊天区域 -->
      <main class="chat-area">
        <!-- 动态背景（固定在视口） -->
        <BackgroundPaths class="chat-background" />
        
        <div class="messages-wrapper" ref="messagesContainer">
          <!-- 欢迎界面 -->
          <div v-if="!chatStore.hasMessages" class="welcome-screen">
            <div class="welcome-content">
              <div class="welcome-badge">
                <span>AI 驱动的法律智能体</span>
              </div>
              <h2>专业法律咨询<br/>即刻获得解答</h2>
              <p class="subtitle">基于海量法律法规与司法判例，为您提供精准、可信赖的法律建议</p>

              <div class="quick-start">
                <p class="quick-label">快速开始</p>
                <div class="quick-chips">
                  <button 
                    v-for="q in quickQuestions" 
                    :key="q"
                    class="quick-chip"
                    @click="inputMessage = q; autoResize()"
                  >
                    {{ q }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 消息列表（支持打字机效果） -->
          <div v-else class="messages-list">
            <div
              v-for="msg in chatStore.messages"
              :key="msg.id"
              class="message-group"
              :class="msg.role"
            >
              <div class="message" :class="msg.role">
                <div class="avatar" :class="msg.role">
                  <span v-if="msg.role === 'user'">我</span>
                  <el-icon v-else :size="20"><ScaleToOriginal /></el-icon>
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender">{{ msg.role === 'user' ? '我' : '智能法律顾问' }}</span>
                    <span class="time">{{ formatTime(msg.created_at) }}</span>
                  </div>
                  <div
                    class="message-body"
                    :ref="el => setupMessageElement(el as HTMLElement, msg)"
                    v-html="getMessageDisplay(msg)"
                  ></div>
                </div>
              </div>
            </div>

            <!-- 加载状态 -->
            <div v-if="chatStore.isLoading" class="message-group assistant">
              <div class="message assistant">
                <div class="avatar assistant">
                  <el-icon :size="20"><ScaleToOriginal /></el-icon>
                </div>
                <div class="message-content">
                  <div class="typing-indicator">
                    <span v-for="i in 3" :key="i"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-section">
          <div class="input-container">
            <div class="input-wrapper">
              <textarea
                v-model="inputMessage"
                placeholder="输入您的法律问题"
                rows="1"
                @keydown.enter.exact.prevent="sendMessage"
                @input="autoResize"
                ref="textareaRef"
              ></textarea>
              <button 
                class="send-btn"
                :class="{ active: inputMessage.trim() && !chatStore.isLoading }"
                @click="sendMessage"
                :disabled="!inputMessage.trim() || chatStore.isLoading"
              >
                <el-icon :size="20"><Promotion /></el-icon>
              </button>
            </div>
            <p class="input-hint">LLM自动结合最新调查表内容+历史聊天记录+知识库语义向量+用户问题综合回答，实现个性化法律咨询</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useChatStore } from '../stores/chat'
import { chatApi } from '@/api/chat'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

// 导入打字机效果工具
import { Typewriter, TypewriterManager } from '@/utils/typewriter'

// 导入背景组件
import BackgroundPaths from '@/components/BackgroundPaths.vue'

// 从图标集中管理文件导入图标
import {
  ScaleToOriginal,
  ChatDotRound
} from '@/icons'


// 导入共享CSS - 使用新的SCSS架构
import '@/assets/css/main.scss'

// Router
const route = useRoute()

// Store
const chatStore = useChatStore()

// Refs
const inputMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const sidebarCollapsed = ref(false)
const currentModelProvider = ref('')
const isLoadingConfig = ref(false)

// 打字机效果管理器
const typewriterManager = new TypewriterManager()

// 存储每个消息的打字机状态
const messageTypewriters = ref<Map<number, Typewriter>>(new Map())
const messageDisplayText = ref<Map<number, string>>(new Map())

// 跟踪哪些消息已经完成打字（历史消息或已完成的打字机）
const completedMessages = ref<Set<number>>(new Set())

// 跟踪当前会话中哪些消息是新接收的
const newMessageIds = ref<Set<number>>(new Set())

const quickQuestions = [
  '劳动合同试用期最长可以约定多久？',
  '公司拖欠工资，员工如何维权？',
  '股权转让需要缴纳哪些税费？',
  '公司如何合法解除严重违纪员工的劳动合同？',
  '未签劳动合同超过一年，公司面临哪些法律风险？',
]

// 优化的Markdown渲染器（使用缓存提高性能）
const md: MarkdownIt = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: (str: string, lang: string): string => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch {}
    }
    return md.utils.escapeHtml(str)
  }
})

// Markdown渲染缓存
const markdownCache = new Map<string, string>()

/**
 * 优化的Markdown渲染函数（带缓存）
 */
const renderMessage = (content: string): string => {
  // 检查缓存
  if (markdownCache.has(content)) {
    return markdownCache.get(content)!
  }
  
  // 同步渲染Markdown，对于典型长度的法律文本不会造成性能问题
  const rendered = md.render(content)
  
  // 缓存结果
  markdownCache.set(content, rendered)
  
  return rendered
}

/**
 * 为AI消息创建打字机效果
 */
const createTypewriterForMessage = (messageId: number, content: string, element: HTMLElement) => {
  // 如果已有打字机实例，先销毁
  const existingTypewriter = messageTypewriters.value.get(messageId)
  if (existingTypewriter) {
    existingTypewriter.destroy()
  }
  
  // 创建新的打字机实例
  const typewriter = new Typewriter({
    speed: 30, // 30ms/字符
    markdown: true,
    markdownRenderer: renderMessage,
    onUpdate: (displayText: string) => {
      // 使用requestAnimationFrame优化渲染
      requestAnimationFrame(() => {
        element.innerHTML = displayText
        messageDisplayText.value.set(messageId, displayText)
        
        // 自动滚动到底部
        nextTick(() => {
          messagesContainer.value?.scrollTo({
            top: messagesContainer.value.scrollHeight,
            behavior: 'smooth'
          })
        })
      })
    },
    onComplete: () => {
      console.log(`消息 ${messageId} 打字完成`)
      // 标记消息为已完成
      completedMessages.value.add(messageId)
      // 从新消息集合中移除
      newMessageIds.value.delete(messageId)
    }
  })
  
  // 存储打字机实例
  messageTypewriters.value.set(messageId, typewriter)
  
  // 开始打字效果
  typewriter.start(content)
  
  return typewriter
}

/**
 * 立即完成所有打字机效果
 */
const completeAllTypewriters = () => {
  messageTypewriters.value.forEach(typewriter => {
    if (!typewriter.completed) {
      typewriter.completeImmediately()
    }
  })
}

/**
 * 清理打字机资源
 */
const cleanupTypewriters = () => {
  messageTypewriters.value.forEach(typewriter => {
    typewriter.destroy()
  })
  messageTypewriters.value.clear()
  messageDisplayText.value.clear()
  markdownCache.clear()
  completedMessages.value.clear()
  newMessageIds.value.clear()
}

// 消息元素设置
const setupMessageElement = (el: HTMLElement | null, msg: any) => {
  if (!el || msg.role !== 'assistant') return
  
  // 检查是否已经有打字机效果
  const existingTypewriter = messageTypewriters.value.get(msg.id)
  if (existingTypewriter) {
    return // 已有打字机实例，不需要再创建
  }
  
  // 检查是否是历史消息（已经完成或不是新消息）
  const isHistoricalMessage = completedMessages.value.has(msg.id) || !newMessageIds.value.has(msg.id)
  
  if (isHistoricalMessage) {
    // 历史消息：直接显示完整内容，不创建打字机效果
    const renderedContent = renderMessage(msg.content)
    requestAnimationFrame(() => {
      el.innerHTML = renderedContent
      messageDisplayText.value.set(msg.id, renderedContent)
    })
  } else {
    // 新消息：创建打字机效果
    createTypewriterForMessage(msg.id, msg.content, el)
  }
}

// 获取消息显示内容
const getMessageDisplay = (msg: any): string => {
  // 用户消息直接渲染
  if (msg.role === 'user') {
    return renderMessage(msg.content)
  }
  
  // AI消息：检查是否有打字机显示文本
  const displayText = messageDisplayText.value.get(msg.id)
  if (displayText) {
    return displayText
  }
  
  // 对于历史消息或已完成的消息，直接渲染完整内容
  // 这确保在setupMessageElement执行前就有内容显示
  return renderMessage(msg.content)
}

// 自动调整输入框高度
const autoResize = () => {
  const el = textareaRef.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }
}

// 发送消息
const sendMessage = async () => {
  const msg = inputMessage.value.trim()
  if (!msg || chatStore.isLoading) return

  inputMessage.value = ''
  if (textareaRef.value) textareaRef.value.style.height = 'auto'

  try {
    // 首先添加用户消息到消息列表
    const userMessageId = Date.now()
    const userMessage = {
      id: userMessageId,
      session_id: chatStore.currentSession?.id || 0,
      role: 'user' as const,
      content: msg,
      created_at: new Date().toISOString()
    }
    chatStore.messages.push(userMessage)
    
    // 创建临时AI消息用于流式显示
    const tempAiMessageId = Date.now() + 1 // 确保ID不同
    const tempAiMessage = {
      id: tempAiMessageId,
      session_id: chatStore.currentSession?.id || 0,
      role: 'assistant' as const,
      content: '',
      created_at: new Date().toISOString()
    }
    
    // 添加到消息列表
    chatStore.messages.push(tempAiMessage)
    
    // 标记为新消息，以便使用打字机效果
    newMessageIds.value.add(tempAiMessageId)
    
    // 创建打字机实例 - 启用Markdown渲染
    const typewriter = new Typewriter({
      speed: 20, // 20ms/字符，更快地显示流式内容
      markdown: true,
      markdownRenderer: renderMessage,
      onUpdate: (text) => {
        // 更新显示文本（已经是渲染后的HTML）
        messageDisplayText.value.set(tempAiMessageId, text)
      },
      onComplete: () => {
        // 标记为已完成
        completedMessages.value.add(tempAiMessageId)
      }
    })
    
    // 存储打字机实例
    messageTypewriters.value.set(tempAiMessageId, typewriter)
    
    // 开始打字机效果（初始为空）
    typewriter.start('')
    
    // 使用流式API发送消息
    await chatApi.sendMessageStream(
      {
        message: msg,
        session_id: chatStore.currentSession?.id || undefined,
        model_provider: currentModelProvider.value
      },
      // onChunk回调 - 处理后端返回的不同事件类型
      (chunk) => {
        console.log('收到流式数据块:', chunk)
        
        // 处理内容块
        if (chunk.content) {
          // 更新打字机内容
          const typewriter = messageTypewriters.value.get(tempAiMessageId)
          if (typewriter) {
            typewriter.updateContent(chunk.content)
          }
        }
        // 处理开始事件
        else if (chunk.event === 'start') {
          console.log('流式传输开始，会话ID:', chunk.session_id)
          // 可以在这里更新会话ID等
        }
        // 处理完成事件
        else if (chunk.event === 'complete') {
          console.log('流式传输完成，消息ID:', chunk.message_id, '完整响应:', chunk.full_response)
          
          // 立即完成打字机效果
          const typewriter = messageTypewriters.value.get(tempAiMessageId)
          if (typewriter) {
            typewriter.completeImmediately()
          }
          
          // 更新消息列表中的消息为最终版本
          const messageIndex = chatStore.messages.findIndex(m => m.id === tempAiMessageId)
          if (messageIndex !== -1) {
            chatStore.messages[messageIndex] = {
              id: chunk.message_id || tempAiMessageId,
              session_id: chatStore.currentSession?.id || 0,
              role: 'assistant' as const,
              content: chunk.full_response || typewriter?.text || '',
              created_at: new Date().toISOString()
            }
            
            // 更新显示文本为最终内容
            const finalContent = chunk.full_response || typewriter?.text || ''
            messageDisplayText.value.set(chunk.message_id || tempAiMessageId, renderMessage(finalContent))
          }
        }
        // 处理错误
        else if (chunk.error) {
          console.error('流式传输错误:', chunk.error)
          ElMessage.error('AI响应错误: ' + chunk.error)
        }
      },
      // onComplete回调 - 流式传输完全结束
      (response) => {
        console.log('流式传输完成回调:', response)
        
        // 检查打字机是否还在运行（如果没有收到完成事件）
        const typewriter = messageTypewriters.value.get(tempAiMessageId)
        if (typewriter && !typewriter.completed) {
          typewriter.complete()
          
          // 如果没有收到完成事件，使用打字机中的内容作为最终内容
          const finalContent = typewriter.text || ''
          const messageIndex = chatStore.messages.findIndex(m => m.id === tempAiMessageId)
          if (messageIndex !== -1 && finalContent) {
            chatStore.messages[messageIndex] = {
              id: tempAiMessageId,
              session_id: chatStore.currentSession?.id || 0,
              role: 'assistant' as const,
              content: finalContent,
              created_at: new Date().toISOString()
            }
            
            messageDisplayText.value.set(tempAiMessageId, renderMessage(finalContent))
          }
        }
        
        // 清理临时打字机
        setTimeout(() => {
          messageTypewriters.value.delete(tempAiMessageId)
          messageDisplayText.value.delete(tempAiMessageId)
        }, 1000)
      },
      // onError回调
      (error) => {
        console.error('流式传输失败:', error)
        ElMessage.error('流式传输失败: ' + (error.message || '未知错误'))
        
        // 清理临时消息
        const messageIndex = chatStore.messages.findIndex(m => m.id === tempAiMessageId)
        if (messageIndex !== -1) {
          chatStore.messages.splice(messageIndex, 1)
        }
        
        // 清理打字机
        messageTypewriters.value.delete(tempAiMessageId)
        messageDisplayText.value.delete(tempAiMessageId)
        newMessageIds.value.delete(tempAiMessageId)
      }
    )
    
  } catch (error) {
    ElMessage.error('发送失败，请重试')
  }
}

// 会话操作
const selectSession = async (id: number) => {
  try {
    await chatStore.fetchSession(id)
  } catch {
    ElMessage.error('加载会话失败')
  }
}

const deleteSession = async (id: number) => {
  try {
    await chatStore.deleteSession(id)
    ElMessage.success('已删除')
  } catch {
    ElMessage.error('删除失败')
  }
}

const newChat = async () => {
  try {
    await chatStore.createSession('新对话', currentModelProvider.value)
    chatStore.clearCurrentSession()
  } catch {
    ElMessage.error('创建失败')
  }
}

// 格式化时间
const formatTime = (date: string | Date) => 
  new Date(date).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })

const formatDate = (dateString?: string) => {
  if (!dateString) return '刚刚'
  const date = new Date(dateString)
  const diff = Date.now() - date.getTime()
  const days = Math.floor(diff / 86400000)

  if (days === 0) return formatTime(date)
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 自动滚动到底部
watch(() => chatStore.messages.length, () => {
  nextTick(() => {
    messagesContainer.value?.scrollTo({ top: messagesContainer.value.scrollHeight, behavior: 'smooth' })
  })
})

// 监听消息变化，为新AI消息准备打字机效果
watch(() => chatStore.messages, (newMessages, oldMessages) => {
  // 检查是否有新的AI消息
  if (newMessages.length > oldMessages.length) {
    const newMessage = newMessages[newMessages.length - 1]
    if (newMessage.role === 'assistant') {
      // 标记为新消息，以便创建打字机效果
      newMessageIds.value.add(newMessage.id)
      console.log(`标记消息 ${newMessage.id} 为新消息`)
    }
  } else if (newMessages.length < oldMessages.length) {
    // 消息被删除，清理相关状态
    const deletedIds = oldMessages.filter(oldMsg =>
      !newMessages.some(newMsg => newMsg.id === oldMsg.id)
    ).map(msg => msg.id)
    
    deletedIds.forEach(id => {
      messageTypewriters.value.get(id)?.destroy()
      messageTypewriters.value.delete(id)
      messageDisplayText.value.delete(id)
      completedMessages.value.delete(id)
      newMessageIds.value.delete(id)
    })
  }
}, { deep: true })

// 监听会话变化，重置状态
watch(() => chatStore.currentSession?.id, () => {
  // 切换会话时，清理所有打字机状态
  cleanupTypewriters()
  completedMessages.value.clear()
  newMessageIds.value.clear()
  
  // 对于新会话中的历史消息，标记为已完成
  chatStore.messages.forEach(msg => {
    if (msg.role === 'assistant') {
      completedMessages.value.add(msg.id)
    }
  })
})

// 组件卸载时清理资源
onUnmounted(() => {
  cleanupTypewriters()
})

// 初始化现有消息状态
const initializeMessageStates = () => {
  // 将所有现有AI消息标记为已完成（历史消息）
  chatStore.messages.forEach(msg => {
    if (msg.role === 'assistant') {
      completedMessages.value.add(msg.id)
      // 预渲染内容到displayText
      const renderedContent = renderMessage(msg.content)
      messageDisplayText.value.set(msg.id, renderedContent)
    }
  })
}

// 初始化
onMounted(async () => {
  // 初始化消息状态
  initializeMessageStates()
  
  // 获取模型配置
  isLoadingConfig.value = true
  try {
    const res = await fetch('/api/v1/chat/config')
    if (res.ok) {
      const config = await res.json()
      currentModelProvider.value = config.model_provider || 'siliconflow'
    } else {
      // 如果后端配置获取失败，使用默认值
      currentModelProvider.value = 'siliconflow'
    }
  } catch {
    // 网络错误时使用默认值
    currentModelProvider.value = 'siliconflow'
  } finally {
    isLoadingConfig.value = false
  }

  // 加载会话列表
  try {
    await chatStore.fetchSessions()
    
    // 检查是否有来自路由参数的会话ID
    const sessionIdFromRoute = route.query.session_id
    if (sessionIdFromRoute && chatStore.sessions.length) {
      const sessionId = parseInt(sessionIdFromRoute as string)
      // 检查会话是否存在
      const sessionExists = chatStore.sessions.some(session => session.id === sessionId)
      if (sessionExists) {
        await selectSession(sessionId)
        // 初始化新会话的消息状态
        initializeMessageStates()
      } else {
        // 如果会话不存在，选择第一个会话
        await selectSession(chatStore.sessions[0].id)
        initializeMessageStates()
      }
    } else if (chatStore.sessions.length) {
      // 没有路由参数，选择第一个会话
      await selectSession(chatStore.sessions[0].id)
      initializeMessageStates()
    }
  } catch {}
})
</script>
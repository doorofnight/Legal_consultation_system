<template>
  <div class="legal-ai-container">
    <!-- 顶部导航栏 -->
    <header class="top-nav">
      <div class="nav-brand">
        <div class="header-left">
          <el-icon ><ChatDotRound /></el-icon>
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

          <!-- 消息列表 -->
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
                  <div class="message-body" v-html="renderMessage(msg.content)"></div>
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
            <p class="input-hint">智能法律顾问提供的建议仅供参考，不构成正式法律意见。重要决策请咨询执业律师。</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

// 从图标集中管理文件导入图标
import {
  ScaleToOriginal,
  ChatDotRound
} from '@/icons'


// 导入共享CSS
import '@/assets/css/variables.css'
import '@/assets/css/utilities.css'
import '@/assets/css/home.css'

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

const quickQuestions = [
  '劳动合同试用期最长可以约定多久？',
  '公司拖欠工资，员工如何维权？',
  '股权转让需要缴纳哪些税费？',
  '公司如何合法解除严重违纪员工的劳动合同？',
  '未签劳动合同超过一年，公司面临哪些法律风险？',
]

// Markdown渲染器
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

const renderMessage = (content: string) => md.render(content)

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
    await chatStore.sendMessage(msg, chatStore.currentSession?.id, currentModelProvider.value)
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

// 初始化
onMounted(async () => {
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
      } else {
        // 如果会话不存在，选择第一个会话
        await selectSession(chatStore.sessions[0].id)
      }
    } else if (chatStore.sessions.length) {
      // 没有路由参数，选择第一个会话
      await selectSession(chatStore.sessions[0].id)
    }
  } catch {}
})
</script>
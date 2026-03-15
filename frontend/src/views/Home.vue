<template>
  <div class="legal-ai-container">
    <!-- 顶部导航栏 -->
    <header class="top-nav">
      <div class="nav-brand">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
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

        <button class="icon-btn" @click="clearChat" title="清空对话">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
          </svg>
        </button>
        <button class="new-chat-btn" @click="newChat">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          新对话
        </button>
      </div>
    </header>

    <div class="main-layout">
      <!-- 左侧边栏 -->
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <button class="toggle-btn" @click="sidebarCollapsed = !sidebarCollapsed">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 17l-5-5 5-5M18 17l-5-5 5-5"/>
            </svg>
          </button>
          <span class="session-label">历史会话</span>
        </div>

        <div class="sessions-list">
          <div 
            v-for="session in chatStore.sessions" 
            :key="session.id"
            class="session-item"
            :class="{ active: chatStore.currentSession?.id === session.id }"
            @click="selectSession(session.id)"
          >
            <div class="session-icon">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
              </svg>
            </div>
            <div class="session-info">
              <span class="session-title">{{ session.title }}</span>
              <span class="session-time">{{ formatDate(session.updated_at) }}</span>
            </div>
            <button class="delete-btn" @click.stop="deleteSession(session.id)">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
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

              <div class="capabilities">
                <div class="capability-card" v-for="cap in capabilities" :key="cap.text">
                  <div class="cap-icon" :class="cap.color">
                    <span>{{ cap.emoji }}</span>
                  </div>
                  <span>{{ cap.text }}</span>
                </div>
              </div>

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
                  <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                  </svg>
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
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                  </svg>
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
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
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
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

// Store
const chatStore = useChatStore()

// Refs
const inputMessage = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const sidebarCollapsed = ref(false)
const currentModelProvider = ref('')
const isLoadingConfig = ref(false)

// 数据
const capabilities = [
  { emoji: '⚖️', text: '法规检索', color: 'blue' },
  { emoji: '📋', text: '合同审查', color: 'purple' },
  { emoji: '🔍', text: '案例分析', color: 'orange' },
  { emoji: '💡', text: '风险预警', color: 'green' },
]

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

const clearChat = () => {
  chatStore.clearCurrentSession()
  ElMessage.success('已清空')
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
    if (chatStore.sessions.length) {
      await selectSession(chatStore.sessions[0].id)
    }
  } catch {}
})
</script>

<style scoped>
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --accent-primary: #2563eb;
  --accent-success: #059669;
  --text-primary: #111827;
  --text-secondary: #4b5563;
  --text-muted: #9ca3af;
  --border-color: rgba(0, 0, 0, 0.08);
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.legal-ai-container {
  height: 100%;
  background: #ffffff;
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
  display: flex;
  flex-direction: column;
}

/* Top Navigation */
.top-nav {
  height: 64px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px -3px rgba(37, 99, 235, 0.3);
}

.logo-icon svg {
  width: 20px;
  height: 20px;
}

.brand-text h1 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.5px;
}

.brand-text span {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.model-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.model-badge.siliconflow {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: #059669;
}

.model-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-color);
  background: white;
  color: var(--text-secondary);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.icon-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border: none;
  color: white;
  font-size: 13px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 15px -3px rgba(37, 99, 235, 0.3);
}

.new-chat-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 25px -5px rgba(37, 99, 235, 0.4);
}

/* Main Layout */
.main-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  height: calc(100vh - 124px);
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: rgba(249, 250, 251, 0.8);
  backdrop-filter: blur(10px);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  height: 48px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-color);
  gap: 12px;
}

.toggle-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--text-primary);
}

.session-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sidebar.collapsed .session-label,
.sidebar.collapsed .session-info,
.sidebar.collapsed .delete-btn,
.sidebar.collapsed .sidebar-footer {
  display: none;
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.5);
}

.session-item:hover {
  background: white;
  border-color: var(--border-color);
  box-shadow: var(--shadow-sm);
}

.session-item.active {
  background: rgba(37, 99, 235, 0.08);
  border-color: rgba(37, 99, 235, 0.3);
}

.session-icon {
  color: var(--text-muted);
  flex-shrink: 0;
}

.session-item.active .session-icon {
  color: var(--accent-primary);
}

.session-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.session-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  font-size: 11px;
  color: var(--text-muted);
}

.delete-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.session-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
  font-size: 13px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid var(--border-color);
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  color: white;
}

.user-profile span {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

/* Chat Area */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: transparent;
}

.messages-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}

/* Welcome Screen */
.welcome-screen {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.welcome-content {
  max-width: 720px;
  text-align: center;
}

.welcome-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background: rgba(37, 99, 235, 0.1);
  border: 1px solid rgba(37, 99, 235, 0.2);
  border-radius: 20px;
  margin-bottom: 24px;
}

.welcome-badge span {
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-primary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.welcome-content h2 {
  font-size: 42px;
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 16px;
  letter-spacing: -1px;
}

.subtitle {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 48px;
  line-height: 1.6;
}

.capabilities {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 48px;
}

.capability-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-sm);
}

.capability-card:hover {
  transform: translateY(-4px);
  background: white;
  box-shadow: var(--shadow-lg);
}

.cap-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: var(--bg-secondary);
}

.cap-icon.blue { background: rgba(37, 99, 235, 0.1); }
.cap-icon.purple { background: rgba(124, 58, 237, 0.1); }
.cap-icon.orange { background: rgba(249, 115, 22, 0.1); }
.cap-icon.green { background: rgba(5, 150, 105, 0.1); }

.capability-card span {
  font-size: 14px;
  font-weight: 600;
}

.quick-start {
  text-align: left;
}

.quick-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 12px;
  text-align: center;
}

.quick-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.quick-chip {
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
}

.quick-chip:hover {
  background: white;
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* Messages */
.messages-list {
  max-width: 850px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.message-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-group.user {
  align-items: flex-end;
}

.message {
  display: flex;
  gap: 16px;
  max-width: 85%;
  animation: messageSlide 0.3s ease;
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  flex-direction: row-reverse;
}

.message .avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-weight: 600;
  font-size: 13px;
  box-shadow: var(--shadow-sm);
}

.avatar.user {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: white;
}

.avatar.assistant {
  background: rgba(5, 150, 105, 0.1);
  color: var(--accent-success);
  border: 1px solid rgba(5, 150, 105, 0.2);
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.message.user .message-header {
  flex-direction: row-reverse;
}

.sender {
  font-size: 13px;
  font-weight: 600;
}

.time {
  font-size: 11px;
  color: var(--text-muted);
}

.message-body {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  font-size: 14px;
  line-height: 1.7;
  box-shadow: var(--shadow-sm);
}

.message.user .message-body {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border-color: transparent;
  color: white;
  border-radius: 12px 12px 4px 12px;
}

.message.assistant .message-body {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px 12px 12px 4px;
}

/* Markdown Content Styles */
.message-body :deep(p) {
  margin: 0 0 12px;
}

.message-body :deep(p:last-child) {
  margin-bottom: 0;
}

.message-body :deep(code) {
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  color: var(--accent-primary);
}

.message-body :deep(pre) {
  background: rgba(0, 0, 0, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  margin: 12px 0;
}

.message-body :deep(pre code) {
  background: transparent;
  padding: 0;
  color: var(--text-primary);
}

.message-body :deep(ul), .message-body :deep(ol) {
  padding-left: 20px;
  margin: 12px 0;
}

.message-body :deep(li) {
  margin-bottom: 6px;
}

.message.user .message-body :deep(code) {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 6px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--border-color);
  border-radius: 12px 12px 12px 4px;
  width: fit-content;
  box-shadow: var(--shadow-sm);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--accent-success);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* Input Section */
.input-section {
  padding: 24px;
  background: transparent;
}

.input-container {
  max-width: 850px;
  margin: 0 auto;
}

.input-wrapper {
  position: relative;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  padding: 16px 20px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 10px 20px -5px rgba(0, 0, 0, 0.05);
}

.input-wrapper:focus-within {
  background: white;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1), 0 10px 40px -10px rgba(37, 99, 235, 0.2);
}

.input-wrapper textarea {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 15px;
  line-height: 1.6;
  resize: none;
  outline: none;
  min-height: 24px;
  max-height: 200px;
  font-family: inherit;
  padding-right: 50px;
}

.input-wrapper textarea::placeholder {
  color: var(--text-muted);
}

.send-btn {
  position: absolute;
  right: 16px;
  bottom: 16px;
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(0, 0, 0, 0.05);
  color: var(--text-muted);
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.send-btn.active {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: white;
  box-shadow: 0 4px 15px -3px rgba(37, 99, 235, 0.3);
}

.send-btn.active:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 25px -5px rgba(37, 99, 235, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-hint {
  text-align: center;
  margin-top: 12px;
  font-size: 12px;
  color: var(--text-muted);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}

/* Responsive */
@media (max-width: 1024px) {
  .capabilities {
    grid-template-columns: repeat(2, 1fr);
  }

  .sidebar {
    position: absolute;
    z-index: 50;
    height: 100%;
    box-shadow: var(--shadow-lg);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }
}

@media (max-width: 640px) {
  .welcome-content h2 {
    font-size: 28px;
  }

  .capabilities {
    grid-template-columns: 1fr;
  }

  .message {
    max-width: 95%;
  }

  .top-nav {
    padding: 0 16px;
  }

  .brand-text span {
    display: none;
  }
}
</style>
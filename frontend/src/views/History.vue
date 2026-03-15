<template>
  <div class="history-container">
    <el-card class="history-header-card">
      <div class="history-header">
        <div class="header-left">
          <el-icon size="28" color="#409eff"><Clock /></el-icon>
          <h2>咨询历史</h2>
        </div>
        <div class="header-right">
          <el-button type="primary" size="small" @click="refreshHistory">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button type="info" size="small" @click="exportHistory">
            <el-icon><Download /></el-icon>
            导出记录
          </el-button>
        </div>
      </div>
      <div class="history-subtitle">
        <p>查看您的法律咨询历史记录，包括聊天会话、调查表修改和合同分析记录。</p>
      </div>
    </el-card>

    <div class="history-content">
      <!-- 聊天历史 -->
      <el-card class="history-section">
        <template #header>
          <div class="section-header">
            <h3>聊天会话历史</h3>
            <el-tag type="success">{{ chatSessions.length }} 个会话</el-tag>
          </div>
        </template>
        
        <div class="session-list">
          <el-table :data="chatSessions" style="width: 100%">
            <el-table-column prop="title" label="会话标题" width="200">
              <template #default="scope">
                <div class="session-title-cell">
                  <el-icon><ChatLineRound /></el-icon>
                  <span>{{ scope.row.title }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="model_provider" label="模型" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.model_provider === 'siliconflow' ? 'primary' : 'success'" size="small">
                  {{ scope.row.model_provider === 'siliconflow' ? 'SiliconFlow' : 'Ollama' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message_count" label="消息数" width="100" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="最后活跃" width="180">
              <template #default="scope">
                {{ formatDateTime(scope.row.updated_at || scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="primary" size="small" @click="viewSession(scope.row.id)">
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>

      <!-- 调查表历史 -->
      <el-card class="history-section">
        <template #header>
          <div class="section-header">
            <h3>调查表修改历史</h3>
            <el-tag type="warning">开发中</el-tag>
          </div>
        </template>
        
        <div class="survey-history">
          <div class="empty-history">
            <el-icon size="64" color="#909399"><Document /></el-icon>
            <h4>暂无调查表历史记录</h4>
            <p>调查表功能正在开发中，完成后将显示您的修改历史</p>
            <el-button type="primary" @click="goToSurvey">
              前往调查表
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 合同分析历史 -->
      <el-card class="history-section">
        <template #header>
          <div class="section-header">
            <h3>合同分析历史</h3>
            <el-tag type="warning">开发中</el-tag>
          </div>
        </template>
        
        <div class="contract-history">
          <div class="empty-history">
            <el-icon size="64" color="#909399"><Files /></el-icon>
            <h4>暂无合同分析记录</h4>
            <p>合同诊断功能正在开发中，完成后将显示您的分析历史</p>
            <el-button type="primary" @click="goToContract">
              前往合同诊断
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 统计信息 -->
    <div class="history-stats">
      <el-card class="stats-card">
        <template #header>
          <div class="stats-header">
            <el-icon><DataAnalysis /></el-icon>
            <h3>使用统计</h3>
          </div>
        </template>
        
        <div class="stats-content">
          <div class="stat-item">
            <div class="stat-value">{{ totalChatMessages }}</div>
            <div class="stat-label">总聊天消息数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ chatSessions.length }}</div>
            <div class="stat-label">聊天会话数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ avgSessionLength }}</div>
            <div class="stat-label">平均会话长度</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ favoriteModel }}</div>
            <div class="stat-label">常用模型</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { 
  Clock, 
  Refresh, 
  Download, 
  ChatLineRound, 
  Document, 
  Files,
  DataAnalysis
} from '@element-plus/icons-vue'

const router = useRouter()
const chatStore = useChatStore()

// 示例聊天会话数据
const chatSessions = ref([
  {
    id: 1,
    title: '劳动合同咨询',
    model_provider: 'siliconflow',
    message_count: 8,
    created_at: '2026-03-10T14:30:00Z',
    updated_at: '2026-03-10T14:45:00Z'
  },
  {
    id: 2,
    title: '公司股权结构问题',
    model_provider: 'ollama',
    message_count: 12,
    created_at: '2026-03-09T10:15:00Z',
    updated_at: '2026-03-09T11:30:00Z'
  },
  {
    id: 3,
    title: '借款合同风险咨询',
    model_provider: 'siliconflow',
    message_count: 6,
    created_at: '2026-03-08T16:20:00Z',
    updated_at: '2026-03-08T16:40:00Z'
  },
  {
    id: 4,
    title: '知识产权保护策略',
    model_provider: 'siliconflow',
    message_count: 10,
    created_at: '2026-03-07T09:45:00Z',
    updated_at: '2026-03-07T10:30:00Z'
  }
])

// 统计信息
const totalChatMessages = computed(() => {
  return chatSessions.value.reduce((sum, session) => sum + session.message_count, 0)
})

const avgSessionLength = computed(() => {
  if (chatSessions.value.length === 0) return 0
  return Math.round(totalChatMessages.value / chatSessions.value.length)
})

const favoriteModel = computed(() => {
  const counts = chatSessions.value.reduce((acc, session) => {
    acc[session.model_provider] = (acc[session.model_provider] || 0) + 1
    return acc
  }, {} as Record<string, number>)
  
  const max = Math.max(...Object.values(counts))
  const favorite = Object.keys(counts).find(key => counts[key] === max)
  return favorite === 'siliconflow' ? 'SiliconFlow' : 'Ollama'
})

// 格式化日期时间
const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 查看会话
const viewSession = (sessionId: number) => {
  router.push('/')
  // 在实际应用中，这里应该跳转到具体的会话页面
  // 这里简单地在控制台输出
  console.log('查看会话:', sessionId)
}

// 刷新历史
const refreshHistory = () => {
  ElMessage.success('历史记录已刷新')
  // 在实际应用中，这里应该重新加载数据
}

// 导出历史
const exportHistory = () => {
  ElMessage.info('导出功能开发中')
}

// 前往调查表
const goToSurvey = () => {
  router.push('/survey')
}

// 前往合同诊断
const goToContract = () => {
  router.push('/contract')
}

// 初始化
onMounted(() => {
  // 加载聊天会话
  chatStore.fetchSessions()
})
</script>

<style scoped>
.history-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.history-header-card {
  width: 100%;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.history-subtitle p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.history-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.history-section {
  width: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  color: #303133;
}

.session-title-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.survey-history,
.contract-history {
  padding: 40px 20px;
}

.empty-history {
  text-align: center;
  color: #909399;
}

.empty-history h4 {
  margin: 16px 0 8px;
  color: #606266;
}

.empty-history p {
  margin-bottom: 20px;
}

.history-stats {
  margin-top: 20px;
}

.stats-card {
  width: 100%;
}

.stats-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stats-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.stats-content {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  transition: all 0.3s;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}
</style>
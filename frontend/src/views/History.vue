<template>
  <div class="history-container">
    <el-card class="history-header-card">
      <div class="history-header">
        <div class="header-left">
          <el-icon class="page-title-icon"><Clock /></el-icon>
          <h2>咨询历史</h2>
        </div>
      </div>
      <div class="history-subtitle">
        <p>查看您的法律咨询历史记录，包括聊天会话、调查表修改和合同分析记录。</p>
      </div>
    </el-card>

    <div class="history-content">
      <el-card class="documents-card">
        <template #header>
          <div class="documents-header">
            <div class="header-left">
              <el-icon><ChatLineRound /></el-icon>
              <h3>聊天会话历史</h3>
              <el-tag type="info" size="small">{{ chatSessions.length }} 个会话</el-tag>
            </div>
            <div class="header-right">
              <GlowingButton @click="refreshChatHistory" glowColor="#3b82f6" class="header-refresh-btn">
                刷新记录
              </GlowingButton>
            </div>
          </div>
        </template>
        
        <div class="session-list">
          <el-table :data="chatSessions" style="width: 100%" stripe v-loading="loadingChatSessions">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="会话标题" min-width="180">
              <template #default="scope">
                <div class="session-title-cell">
                  <span>{{ scope.row.title }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" min-width="160">
              <template #default="scope">
                {{ formatDateTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="message_count" label="消息数" width="100" />
            <el-table-column prop="model_provider" label="使用模型" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.model_provider === 'siliconflow' ? 'primary' : 'success'" size="small">
                  {{ scope.row.model_provider === 'siliconflow' ? 'SiliconFlow' : 'Ollama' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getChatStatusTagType(scope.row.status)" size="small">
                  {{ getChatStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="viewSession(scope.row.id)">
                  查看会话
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="deleteChatSession(scope.row.id)"
                  :loading="deletingChatSessionId === scope.row.id"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
        </div>
      </el-card>

      <!-- 调查表历史 -->
      <el-card class="documents-card">
        <template #header>
          <div class="documents-header">
            <div class="header-left">
              <el-icon><Document /></el-icon>
              <h3>调查表历史记录</h3>
              <el-tag type="info" size="small">{{ surveyRecords.length }} 条记录</el-tag>
            </div>
            <div class="header-right">
              <GlowingButton @click="refreshSurveyHistory" glowColor="#3b82f6" class="header-refresh-btn">
                刷新记录
              </GlowingButton>
            </div>
          </div>
        </template>
        
        <div class="survey-history">
          <el-table :data="surveyRecords" style="width: 100%" stripe v-loading="loadingSurveyRecords">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="template_id" label="模板名称" min-width="160">
              <template #default="scope">
                {{ scope.row.template ? scope.row.template.name : `模板 ${scope.row.template_id}` }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="提交时间" min-width="160">
              <template #default="scope">
                {{ formatDateTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusTagType(scope.row.status)" size="small">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="version" label="版本号" width="100">
              <template #default="scope">
                <el-tag type="info" size="small">
                  v{{ scope.row.version || '1.0' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="法律建议" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.suggestions?.length > 0" type="success" size="small">
                  {{ scope.row.suggestions.length }} 条建议
                </el-tag>
                <el-tag v-else type="info" size="small">
                  无建议
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="viewSurveyRecord(scope.row.id)">
                  查看调查表
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="deleteSurveyRecord(scope.row.id)"
                  :loading="deletingRecordId === scope.row.id"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
        </div>
      </el-card>

      <!-- 合同分析历史 -->
      <el-card class="documents-card">
        <template #header>
          <div class="documents-header">
            <div class="header-left">
              <el-icon><Files /></el-icon>
              <h3>合同分析历史</h3>
              <el-tag type="info" size="small">{{ contractUploads.length }} 个合同</el-tag>
            </div>
            <div class="header-right">
              <GlowingButton @click="refreshContractHistory" glowColor="#3b82f6" class="header-refresh-btn">
                刷新记录
              </GlowingButton>
            </div>
          </div>
        </template>
        
        <div class="contract-history">
          <el-table :data="contractUploads" style="width: 100%" stripe v-loading="loadingContractUploads">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="filename" label="文件名" min-width="180">
              <template #default="scope">
                <span>{{ scope.row.filename }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="contract_type" label="合同类型" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.contract_type" type="info" size="small">
                  {{ scope.row.contract_type }}
                </el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="上传时间" min-width="160">
              <template #default="scope">
                {{ formatDateTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getContractStatusTagType(scope.row.status)" size="small">
                  {{ getContractStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="file_size" label="文件大小" width="100">
              <template #default="scope">
                {{ formatFileSize(scope.row.file_size) }}
              </template>
            </el-table-column>
            <el-table-column label="诊断结果" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.diagnoses && scope.row.diagnoses.length > 0" type="success" size="small">
                  {{ scope.row.diagnoses.length }} 个分析
                </el-tag>
                <el-tag v-else type="info" size="small">
                  未分析
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="viewContractAnalysis(scope.row)">
                  查看分析
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="deleteContractUpload(scope.row.id)"
                  :loading="deletingContractId === scope.row.id"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
        </div>
      </el-card>
    </div>

    <!-- 调查记录详情弹窗 -->
    <SurveyRecordDetailDialog
      v-model:visible="recordDialogVisible"
      :record-data="currentRecord"
      @close="handleRecordDialogClose"
    />

    <!-- 合同分析详情弹窗 -->
    <ContractDiagnosisDetailDialog
      v-model:visible="contractDialogVisible"
      :record-data="currentContract"
      @close="handleContractDialogClose"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { chatApi } from '@/api/chat'
import { getSurveyHistory, deleteSurveyRecord as deleteSurveyRecordApi } from '@/api/survey'
import { getContractHistory, deleteContractUpload as deleteContractUploadApi } from '@/api/contract'
import SurveyRecordDetailDialog from '@/components/SurveyRecordDetailDialog.vue'
import ContractDiagnosisDetailDialog from '@/components/ContractDiagnosisDetailDialog.vue'
import GlowingButton from '@/components/GlowingButton.vue'
// 从图标集中管理文件导入图标
import {
  Clock,
  Refresh,
  ChatLineRound,
  Files,
  Document
} from '@/icons'
// 导入共享CSS
import '@/assets/css/pages/history.css'

const router = useRouter()

// 聊天会话数据（从API获取）
const chatSessions = ref<any[]>([])

// 获取聊天会话
const fetchChatSessions = async () => {
  try {
    loadingChatSessions.value = true
    const sessions = await chatApi.getSessions(0, 100)
    // 转换数据格式，添加status字段（根据实际情况）
    chatSessions.value = sessions.map(session => ({
      ...session,
      status: session.updated_at ? 'completed' : 'active' // 简单判断状态
    }))
  } catch (error) {
    console.error('获取聊天会话失败:', error)
    ElMessage.error('获取聊天会话失败')
  } finally {
    loadingChatSessions.value = false
  }
}

// 聊天会话相关变量
const loadingChatSessions = ref(false)
const deletingChatSessionId = ref<number | null>(null)

// 调查表记录数据
const surveyRecords = ref<any[]>([])
const loadingSurveyRecords = ref(false)
const deletingRecordId = ref<number | null>(null)

// 合同上传记录数据
const contractUploads = ref<any[]>([])
const loadingContractUploads = ref(false)
const deletingContractId = ref<number | null>(null)

// 调查记录详情弹窗相关变量
const recordDialogVisible = ref(false)
const currentRecord = ref<any>(null)
const loadingRecordDetail = ref(false)

// 合同分析详情弹窗相关变量
const contractDialogVisible = ref(false)
const currentContract = ref<any>(null)

// 获取调查表记录
const fetchSurveyRecords = async () => {
  try {
    loadingSurveyRecords.value = true
    // 不传递user_id参数，让后端返回所有记录
    const response = await getSurveyHistory('', 100, 0)
    surveyRecords.value = response.records || []
  } catch (error) {
    console.error('获取调查表记录失败:', error)
    ElMessage.error('获取调查表记录失败')
    surveyRecords.value = []
  } finally {
    loadingSurveyRecords.value = false
  }
}

// 状态映射
const statusMap: Record<string, { text: string, type: string }> = {
  'submitted': { text: '已提交', type: 'warning' },
  'analyzed': { text: '已分析', type: 'success' }
}

// 获取状态文本
const getStatusText = (status: string) => {
  return statusMap[status]?.text || status
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  return statusMap[status]?.type || 'info'
}

// 行业映射
// 聊天会话状态映射
const chatStatusMap: Record<string, { text: string, type: string }> = {
  'active': { text: '活跃', type: 'success' },
  'completed': { text: '已完成', type: 'info' },
  'archived': { text: '已归档', type: 'warning' }
}

// 获取聊天状态文本
const getChatStatusText = (status: string) => {
  return chatStatusMap[status]?.text || status
}

// 获取聊天状态标签类型
const getChatStatusTagType = (status: string) => {
  return chatStatusMap[status]?.type || 'info'
}

// 删除聊天会话
const deleteChatSession = async (sessionId: number) => {
  try {
    deletingChatSessionId.value = sessionId
    // 调用API删除会话
    await chatApi.deleteSession(sessionId)
    
    // 从本地数据中移除
    chatSessions.value = chatSessions.value.filter(session => session.id !== sessionId)
    ElMessage.success('会话删除成功')
  } catch (error) {
    console.error('删除聊天会话失败:', error)
    ElMessage.error('删除失败')
  } finally {
    deletingChatSessionId.value = null
  }
}

// 刷新聊天历史
const refreshChatHistory = () => {
  fetchChatSessions()
}

// 查看调查记录详情
const viewSurveyRecord = async (recordId: number) => {
  try {
    loadingRecordDetail.value = true
    
    // 从现有数据中查找记录
    const record = surveyRecords.value.find(r => r.id === recordId)
    if (record) {
      currentRecord.value = record
      recordDialogVisible.value = true
    } else {
      ElMessage.warning('未找到该记录')
    }
  } catch (error) {
    console.error('加载记录详情失败:', error)
    ElMessage.error('加载记录详情失败')
  } finally {
    loadingRecordDetail.value = false
  }
}

// 处理记录弹窗关闭
const handleRecordDialogClose = () => {
  // 弹窗关闭时的清理操作
  currentRecord.value = null
}

// 处理合同弹窗关闭
const handleContractDialogClose = () => {
  // 弹窗关闭时的清理操作
  currentContract.value = null
}

// 删除调查记录
const deleteSurveyRecord = async (recordId: number) => {
  try {
    // 确认对话框
    await ElMessageBox.confirm(
      '确定要删除这条调查记录吗？删除后无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    deletingRecordId.value = recordId
    
    // 调用API删除记录
    // 注意：这里不传递user_id参数，后端将允许删除任何记录
    // 实际项目中应该从用户状态获取真实的用户ID
    await deleteSurveyRecordApi(recordId)
    
    // 从本地数据中移除
    surveyRecords.value = surveyRecords.value.filter(record => record.id !== recordId)
    ElMessage.success('记录删除成功')
  } catch (error: any) {
    if (error !== 'cancel') { // 用户点击了取消
      console.error('删除记录失败:', error)
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
    }
  } finally {
    deletingRecordId.value = null
  }
}

// 刷新调查表历史
const refreshSurveyHistory = () => {
  fetchSurveyRecords()
  ElMessage.success('调查表历史已刷新')
}

// 获取合同上传记录
const fetchContractUploads = async () => {
  try {
    loadingContractUploads.value = true
    const response = await getContractHistory(100, 0)
    contractUploads.value = response.uploads || []
  } catch (error) {
    console.error('获取合同上传记录失败:', error)
    ElMessage.error('获取合同上传记录失败')
    contractUploads.value = []
  } finally {
    loadingContractUploads.value = false
  }
}

// 合同状态映射
const contractStatusMap: Record<string, { text: string, type: string }> = {
  'uploaded': { text: '已上传', type: 'info' },
  'parsing': { text: '解析中', type: 'warning' },
  'analyzing': { text: '分析中', type: 'warning' },
  'completed': { text: '已完成', type: 'success' },
  'failed': { text: '失败', type: 'danger' }
}

// 获取合同状态文本
const getContractStatusText = (status: string) => {
  return contractStatusMap[status]?.text || status
}

// 获取合同状态标签类型
const getContractStatusTagType = (status: string) => {
  return contractStatusMap[status]?.type || 'info'
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 查看合同分析
const viewContractAnalysis = (upload: any) => {
  // 设置当前合同数据并打开弹窗
  currentContract.value = upload
  contractDialogVisible.value = true
}

// 删除合同上传记录
const deleteContractUpload = async (uploadId: number) => {
  try {
    // 确认对话框
    await ElMessageBox.confirm(
      '确定要删除这个合同上传记录吗？删除后文件和分析结果都将被永久删除。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    deletingContractId.value = uploadId
    
    // 调用API删除记录
    await deleteContractUploadApi(uploadId)
    
    // 从本地数据中移除
    contractUploads.value = contractUploads.value.filter(upload => upload.id !== uploadId)
    ElMessage.success('合同上传记录删除成功')
  } catch (error: any) {
    if (error !== 'cancel') { // 用户点击了取消
      console.error('删除合同上传记录失败:', error)
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
    }
  } finally {
    deletingContractId.value = null
  }
}

// 刷新合同历史
const refreshContractHistory = () => {
  fetchContractUploads()
  ElMessage.success('合同分析历史已刷新')
}

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
  // 跳转到主页并传递会话ID作为查询参数
  router.push({ path: '/', query: { session_id: sessionId.toString() } })
}


// 初始化
onMounted(() => {
  // 加载聊天会话
  fetchChatSessions()
  // 加载调查表记录
  fetchSurveyRecords()
  // 加载合同上传记录
  fetchContractUploads()
})
</script>

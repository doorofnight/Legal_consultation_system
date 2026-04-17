<template>
  <div class="contract-container">
    <!-- 顶部标题和说明 -->
    <el-card class="contract-header-card">
      <div class="contract-header">
        <div class="header-left">
          <el-icon class="page-title-icon"><Files /></el-icon>
          <h2>合同智能诊断</h2>
        </div>
        <div class="header-right">
          <GlowingButton @click="showHelp = true" glowColor="#3b82f6">
            使用帮助
          </GlowingButton>
        </div>
      </div>
      <div class="contract-subtitle">
        <p>上传您的合同文档，AI将基于本地知识库进行深度分析，识别风险条款并提供专业修改建议。</p>
        <p class="contract-tip">支持 .docx、.doc、.txt 格式，最大文件大小 10MB</p>
      </div>
    </el-card>

    <!-- 主内容区域 -->
    <div class="contract-content">
      <!-- 步骤指示器 -->
      <div class="steps-container" v-if="activeStep > 0">
        <el-steps :active="activeStep" align-center>
          <el-step title="上传合同" description="拖拽或选择合同文件" />
          <el-step title="解析确认" description="确认合同基本信息" />
          <el-step title="风险诊断" description="AI分析风险条款" />
          <el-step title="查看结果" description="查看诊断报告和建议" />
        </el-steps>
      </div>

      <!-- 步骤1：上传合同 -->
      <div v-if="activeStep === 0" class="upload-section">
        <el-card class="upload-card">
          <template #header>
            <div class="upload-header">
              <h3>上传合同文件</h3>
              <p>将合同文件拖到此处，或点击选择文件</p>
            </div>
          </template>
          
          <div class="upload-area">
            <el-upload
              class="upload-dragger"
              drag
              action=""
              :http-request="handleUpload"
              :before-upload="beforeUpload"
              :show-file-list="false"
              :accept="'.docx,.doc,.txt'"
              :disabled="uploading"
            >
              <div class="upload-content">
                <el-icon class="upload-icon" :size="60">
                  <UploadFilled />
                </el-icon>
                <div class="upload-text">
                  <p class="upload-title">点击上传或将文件拖到此处</p>
                  <p class="upload-subtitle">支持 .docx、.doc、.txt 格式</p>
                </div>
                <div v-if="uploading" class="upload-progress">
                  <el-progress
                    :percentage="uploadProgress"
                    :status="uploadStatus"
                    :stroke-width="8"
                  />
                  <p class="progress-text">{{ uploadMessage }}</p>
                </div>
              </div>
            </el-upload>
            
            <div class="upload-tips">
              <h4>上传提示：</h4>
              <ul class="list-none space-y-2">
                <li>确保合同文件内容清晰可读</li>
                <li>建议使用标准合同格式，便于AI准确分析</li>
                <li>敏感信息可在上传前进行脱敏处理</li>
                <li>分析过程可能需要1-3分钟，请耐心等待</li>
              </ul>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 步骤2：解析确认 -->
      <div v-if="activeStep === 1" class="confirm-section">
        <el-card class="confirm-card">
          <template #header>
            <div class="confirm-header">
              <h3>合同信息确认</h3>
              <p>请确认AI识别的合同基本信息</p>
            </div>
          </template>
          
          <div class="contract-info">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">文件名：</span>
                <span class="info-value">{{ contractUpload?.filename }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">文件大小：</span>
                <span class="info-value">{{ formatFileSize(contractUpload?.file_size || 0) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">上传时间：</span>
                <span class="info-value">{{ formatDate(contractUpload?.created_at) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">合同类型：</span>
                <el-select
                  v-model="contractType"
                  placeholder="请选择合同类型"
                  class="type-select"
                  filterable
                  allow-create
                >
                  <el-option
                    v-for="type in contractTypes"
                    :key="type"
                    :label="type"
                    :value="type"
                  />
                </el-select>
              </div>
            </div>
            
            <div class="preview-section">
              <h4>合同内容预览：</h4>
              <div class="preview-content">
                <pre v-if="contractPreview">{{ contractPreview }}</pre>
                <div v-else class="preview-empty">
                  <el-icon><Document /></el-icon>
                  <p>正在解析合同内容...</p>
                </div>
              </div>
            </div>   
            <div class="action-buttons">
              <GlowingButton @click="goBackToUpload" glowColor="#6b7280">
                重新上传
              </GlowingButton>
              <GlowingButton @click="startDiagnosis" :disabled="diagnosing" glowColor="#10b981">
                开始诊断分析
              </GlowingButton>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 步骤3：诊断分析中 -->
      <div v-if="activeStep === 2" class="analyzing-section">
        <el-card class="analyzing-card">
          <template #header>
            <div class="analyzing-header">
              <h3>AI正在诊断合同风险</h3>
              <p>基于本地知识库和AI模型进行深度分析</p>
            </div>
          </template>
          
          <div class="analyzing-content">
            <div class="analyzing-progress">
              <el-progress
                type="circle"
                :percentage="diagnosisProgress"
                :status="diagnosisStatus"
                :width="120"
              />
              <div class="analyzing-details">
                <h4>{{ diagnosisMessage }}</h4>
                <p>当前状态：{{ diagnosisStatusText }}</p>
                <p v-if="estimatedTime">预计剩余时间：{{ estimatedTime }}</p>
              </div>
            </div>
            
            <div class="analyzing-steps">
              <div class="step-item" :class="{ active: currentStep >= 1 }">
                <div class="step-icon">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="step-info">
                  <h5>解析合同文本</h5>
                  <p>提取合同条款和关键信息</p>
                </div>
              </div>
              <div class="step-item" :class="{ active: currentStep >= 2 }">
                <div class="step-icon">
                  <el-icon><Reading /></el-icon>
                </div>
                <div class="step-info">
                  <h5>检索相关知识</h5>
                  <p>从本地知识库匹配相关法律条文</p>
                </div>
              </div>
              <div class="step-item" :class="{ active: currentStep >= 3 }">
                <div class="step-icon">
                  <el-icon><Warning /></el-icon>
                </div>
                <div class="step-info">
                  <h5>识别风险条款</h5>
                  <p>分析合同中的潜在风险点</p>
                </div>
              </div>
              <div class="step-item" :class="{ active: currentStep >= 4 }">
                <div class="step-icon">
                  <el-icon><EditPen /></el-icon>
                </div>
                <div class="step-info">
                  <h5>生成修改建议</h5>
                  <p>提供专业的条款修改方案</p>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 步骤4：诊断结果 -->
      <div v-if="activeStep === 3" class="result-section">
        <el-card class="result-card">
          <template #header>
            <div class="result-header">
              <div class="header-left">
                <h3>合同诊断报告</h3>
                <p class="result-subtitle">
                  合同类型：{{ diagnosisResult?.contract_type }} |
                  分析时间：{{ formatDate(diagnosisResult?.created_at) }} |
                  风险总数：{{ diagnosisResult?.risks?.length || 0 }}个
                </p>
              </div>
            </div>
          </template>
          
          <div class="result-content">
            <!-- 总体评价 -->
            <div class="overall-assessment">
              <h4>总体评价</h4>
              <div class="assessment-content">
                <p>{{ diagnosisResult?.summary || '暂无总体评价' }}</p>
              </div>
            </div>
            
            <!-- 风险统计 -->
            <div class="risk-statistics">
              <h4>风险统计</h4>
              <div class="statistics-grid">
                <div class="stat-item high-risk">
                  <div class="stat-icon">
                    <el-icon><WarningFilled /></el-icon>
                  </div>
                  <div class="stat-info">
                    <h5>高风险</h5>
                    <p class="stat-count">{{ highRiskCount }}</p>
                  </div>
                </div>
                <div class="stat-item medium-risk">
                  <div class="stat-icon">
                    <el-icon><Warning /></el-icon>
                  </div>
                  <div class="stat-info">
                    <h5>中风险</h5>
                    <p class="stat-count">{{ mediumRiskCount }}</p>
                  </div>
                </div>
                <div class="stat-item low-risk">
                  <div class="stat-icon">
                    <el-icon><InfoFilled /></el-icon>
                  </div>
                  <div class="stat-info">
                    <h5>低风险</h5>
                    <p class="stat-count">{{ lowRiskCount }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 风险详情 -->
            <div class="risk-details">
              <h4>风险条款详情</h4>
              <div class="risk-list">
                <div v-for="(risk, index) in diagnosisResult?.risks" :key="index" class="risk-item">
                  <div class="risk-header" :class="risk.risk_level">
                    <div class="risk-title">
                      <span class="risk-index">风险 {{ index + 1 }}</span>
                      <span class="risk-level" :class="risk.risk_level">
                        {{ getRiskLevelText(risk.risk_level) }}
                      </span>
                      <span class="risk-type">{{ risk.risk_type }}</span>
                    </div>
                  </div>
                  <div class="risk-content">
                    <div class="risk-clause">
                      <h5>风险条款：</h5>
                      <p>{{ risk.clause }}</p>
                    </div>
                    <div class="risk-description">
                      <h5>风险描述：</h5>
                      <p>{{ risk.description || '暂无详细描述' }}</p>
                    </div>
                    <div class="risk-suggestion">
                      <h5>修改建议：</h5>
                      <p>{{ risk.suggestion }}</p>
                    </div>
                  </div>
                </div>
                
                <div v-if="!diagnosisResult?.risks?.length" class="no-risks">
                  <el-icon><SuccessFilled /></el-icon>
                  <p>未发现明显风险条款，合同相对完善</p>
                </div>
              </div>
            </div>
            
            <!-- 综合建议 -->
            <div class="overall-suggestions">
              <h4>综合建议</h4>
              <div class="suggestions-content">
                <p>{{ diagnosisResult?.suggestions || '暂无综合建议' }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 使用帮助对话框 -->
    <ContractHelpDialog
      v-model="showHelp"
      title="合同诊断使用帮助"
      width="50%"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Files,
  UploadFilled,
  Document,
  Reading,
  Warning,
  EditPen,
  WarningFilled,
  InfoFilled,
  SuccessFilled
} from '@element-plus/icons-vue'
import { uploadContract, diagnoseContract, getDiagnosisStatus, getContractDiagnosis } from '../api/contract'
import type { ContractUpload, ContractDiagnosis, ContractDiagnosisRequest } from '../types/contract'
import ContractHelpDialog from '@/components/ContractHelpDialog.vue'
import GlowingButton from '@/components/GlowingButton.vue'

// 导入CSS文件
import '@/assets/css/pages/contract.css'
import '@/assets/css/pages/dialog.css'

// 响应式数据
const activeStep = ref(0) // 0:上传, 1:确认, 2:分析中, 3:结果
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref<'success' | 'exception' | 'warning' | undefined>()
const uploadMessage = ref('')

const contractUpload = ref<ContractUpload | null>(null)
const contractPreview = ref('')
const contractType = ref('')
const contractTypes = ref<string[]>([
  '买卖合同',
  '租赁合同',
  '劳动合同',
  '服务合同',
  '技术合同',
  '借款合同',
  '担保合同',
  '委托合同',
  '合伙协议',
  '其他合同'
])

const diagnosing = ref(false)
const diagnosisProgress = ref(0)
const diagnosisStatus = ref<'success' | 'exception' | 'warning' | undefined>()
const diagnosisMessage = ref('正在准备分析...')
const diagnosisStatusText = ref('等待开始')
const estimatedTime = ref('')
const currentStep = ref(0)

const diagnosisResult = ref<ContractDiagnosis | null>(null)
const currentDiagnosisId = ref<number | null>(null)
const showHelp = ref(false)

// 轮询状态检查的定时器
let statusCheckInterval: number | null = null

// 计算属性
const highRiskCount = computed(() => {
  return diagnosisResult.value?.risks?.filter((r) => r.risk_level === '高风险').length || 0
})

const mediumRiskCount = computed(() => {
  return diagnosisResult.value?.risks?.filter((r) => r.risk_level === '中风险').length || 0
})

const lowRiskCount = computed(() => {
  return diagnosisResult.value?.risks?.filter((r) => r.risk_level === '低风险').length || 0
})

// 方法
const beforeUpload = (file: File) => {
  const isDoc = file.type.includes('document') || 
                file.name.endsWith('.docx') || 
                file.name.endsWith('.doc') ||
                file.name.endsWith('.txt')
  const isLt10M = file.size / 1024 / 1024 < 10
  
  if (!isDoc) {
    ElMessage.error('只能上传文档文件（.docx, .doc, .txt）!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

const handleUpload = async (options: any) => {
  const { file } = options
  uploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = undefined
  uploadMessage.value = '正在上传文件...'
  
  try {
    // 调用真实的上传API
    const response = await uploadContract({ file })
    contractUpload.value = response.upload
    
    // 如果有预分析数据，显示合同预览
    if (response.pre_analysis) {
      // 从文件名提取文件格式
      const fileFormat = file.name.split('.').pop()?.toUpperCase() || '未知格式'
      contractPreview.value = `文件格式：${fileFormat}\n总页数：${response.pre_analysis.total_pages}\n总段落数：${response.pre_analysis.total_paragraphs}\n风险分析：待AI审查`
    } else {
      contractPreview.value = `合同文件：${file.name}\n大小：${formatFileSize(file.size)}\n上传时间：${formatDate(new Date().toISOString())}`
    }
    
    uploadProgress.value = 100
    uploadStatus.value = 'success'
    uploadMessage.value = '上传成功'
    
    // 延迟切换到下一步
    setTimeout(() => {
      activeStep.value = 1
      uploading.value = false
    }, 500)
    
  } catch (error: any) {
    console.error('上传失败:', error)
    uploadStatus.value = 'exception'
    uploadMessage.value = '上传失败'
    ElMessage.error(error.response?.data?.error || '上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const goBackToUpload = () => {
  activeStep.value = 0
  contractUpload.value = null
  contractPreview.value = ''
  contractType.value = ''
  diagnosisResult.value = null
  currentDiagnosisId.value = null
}

const startDiagnosis = async () => {
  if (!contractUpload.value?.id) {
    ElMessage.error('请先上传合同文件')
    return
  }

  diagnosing.value = true
  activeStep.value = 2
  diagnosisProgress.value = 0
  diagnosisStatus.value = undefined
  diagnosisMessage.value = '正在启动AI分析...'
  diagnosisStatusText.value = '初始化'
  currentStep.value = 0

  try {
    // 构建诊断请求
    const diagnosisRequest: ContractDiagnosisRequest = {
      upload_id: contractUpload.value.id,
      contract_type: contractType.value || '其他合同', // 传递用户选择的合同类型
      perspective: '通用', // 审查立场默认为通用
      focus_areas: [],
      model_provider: 'siliconflow' // 默认使用siliconflow
    }

    // 开始诊断
    const response = await diagnoseContract(diagnosisRequest)
    diagnosisResult.value = response.diagnosis
    currentDiagnosisId.value = response.diagnosis.id
    
    // 启动状态轮询
    startStatusPolling(contractUpload.value.id, response.diagnosis.id)
    
  } catch (error: any) {
    console.error('诊断启动失败:', error)
    diagnosisStatus.value = 'exception'
    diagnosisMessage.value = '诊断启动失败'
    diagnosisStatusText.value = '失败'
    ElMessage.error(error.response?.data?.error || '诊断启动失败，请重试')
    activeStep.value = 1
    diagnosing.value = false
  }
}

const startStatusPolling = (uploadId: number, diagnosisId: number) => {
  // 清除之前的定时器
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
  }

  // 设置轮询间隔
  statusCheckInterval = window.setInterval(async () => {
    try {
      const status = await getDiagnosisStatus(uploadId)
      
      // 更新进度和状态
      diagnosisProgress.value = status.progress
      diagnosisStatusText.value = getStatusText(status.status)
      diagnosisMessage.value = status.message
      
      // 根据状态更新当前步骤
      switch (status.status) {
        case 'uploading':
          currentStep.value = 0
          break
        case 'parsing':
          currentStep.value = 1
          break
        case 'analyzing':
          currentStep.value = 2
          break
        default:
          currentStep.value = 3
      }
      
      // 如果分析完成，跳转到结果页面
      if (status.status === 'completed') {
        clearInterval(statusCheckInterval!)
        statusCheckInterval = null
        
        // 获取完整的诊断结果
        try {
          // 调用API获取完整的诊断结果
          const fullDiagnosis = await getContractDiagnosis(diagnosisId)
          diagnosisResult.value = fullDiagnosis
          
          diagnosisProgress.value = 100
          diagnosisStatus.value = 'success'
          diagnosisMessage.value = '分析完成'
          diagnosisStatusText.value = '完成'
          
          // 跳转到结果页面
          activeStep.value = 3
          diagnosing.value = false
          
        } catch (error) {
          console.error('获取诊断结果失败:', error)
          // 如果获取失败，仍然跳转到结果页面，但显示错误信息
          diagnosisStatus.value = 'exception'
          diagnosisMessage.value = '获取诊断结果失败'
          diagnosisStatusText.value = '失败'
          ElMessage.error('获取诊断结果失败，请刷新页面重试')
          activeStep.value = 3
          diagnosing.value = false
        }
      } else if (status.status === 'failed') {
        clearInterval(statusCheckInterval!)
        statusCheckInterval = null
        diagnosisStatus.value = 'exception'
        diagnosisMessage.value = '分析失败'
        diagnosisStatusText.value = '失败'
        ElMessage.error('合同分析失败，请重试')
        activeStep.value = 1
        diagnosing.value = false
      }
      
    } catch (error) {
      console.error('状态检查失败:', error)
    }
  }, 2000) // 每2秒检查一次
}

const getStatusText = (status: string): string => {
  switch (status) {
    case 'uploading': return '上传中'
    case 'parsing': return '解析中'
    case 'analyzing': return '分析中'
    case 'completed': return '完成'
    case 'failed': return '失败'
    default: return '未知'
  }
}

const getRiskLevelText = (level: string): string => {
  switch (level) {
    case '高风险': return '高风险'
    case '中风险': return '中风险'
    case '低风险': return '低风险'
    default: return '未知风险'
  }
}


// 组件卸载时清除定时器
onUnmounted(() => {
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
    statusCheckInterval = null
  }
})
</script>
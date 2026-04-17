/* 合同诊断详情弹窗 - 模仿SurveyRecordDetailDialog.vue逻辑 */
<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`合同诊断详情 - ID: ${record?.id || ''}`"
    width="900px"
    :close-on-click-modal="false"
  >
    <div class="record-detail-content" v-if="record">
      <div class="record-header">
        <div class="record-info">
          <p><strong>上传时间：</strong>{{ formatDateTime(record.created_at) }}</p>
          <p><strong>状态：</strong>
            <el-tag :type="getStatusTagType(record.status)" size="small">
              {{ getStatusText(record.status) }}
            </el-tag>
          </p>
          <p><strong>文件名：</strong>{{ record.filename }}</p>
          <p><strong>文件大小：</strong>{{ formatFileSize(record.file_size) }}</p>
        </div>
      </div>

      <el-divider>合同诊断结果</el-divider>
        
      <div class="diagnosis-results">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-diagnosis">
          <el-skeleton :rows="5" animated />
        </div>
          
        <!-- 显示诊断结果 -->
        <div v-else-if="diagnosis">
          <div class="diagnosis-info" style="margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
            <p><strong>合同类型：</strong>{{ diagnosis.contract_type || '未知类型' }}</p>
            <p><strong>分析时间：</strong>{{ formatDateTime(diagnosis.created_at) }}</p>
            <p v-if="diagnosis.model_used"><strong>分析模型：</strong>{{ diagnosis.model_used }}</p>
          </div>
            
          <!-- 总体评价 -->
          <div class="summary-section" style="margin-bottom: 20px;">
            <h4 style="margin-bottom: 10px; color: #333;">总体评价</h4>
            <div style="padding: 12px; background-color: #f0f9ff; border-radius: 6px; border-left: 4px solid #409eff;">
              {{ diagnosis.summary || '暂无总体评价' }}
            </div>
          </div>

          <!-- 风险分析 -->
          <div v-if="diagnosis.risks && diagnosis.risks.length > 0" class="risks-section">
            <h4 style="margin-bottom: 15px; color: #333;">风险条款分析</h4>
            <el-descriptions :column="1" border>
              <template v-for="(risk, index) in diagnosis.risks" :key="risk.id || index">
                <el-descriptions-item :label="`风险 ${index + 1}`" :span="1">
                  <div style="display: flex; flex-direction: column; gap: 8px;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                      <el-tag :type="getRiskLevelTagType(risk.risk_level)" size="small">
                        {{ getRiskLevelText(risk.risk_level) }}
                      </el-tag>
                      <el-tag type="info" size="small">
                        {{ risk.risk_type || '未知类型' }}
                      </el-tag>
                    </div>
                    
                    <div>
                      <strong>风险条款：</strong>
                      <span>{{ risk.clause || '未指定具体条款' }}</span>
                    </div>
                    
                    <div>
                      <strong>风险描述：</strong>
                      <span>{{ risk.description || '暂无描述' }}</span>
                    </div>
                    
                    <div>
                      <strong>修改建议：</strong>
                      <span>{{ risk.suggestion || '暂无建议' }}</span>
                    </div>
                  </div>
                </el-descriptions-item>
              </template>
            </el-descriptions>
          </div>
          <div v-else class="no-risks">
            <el-empty description="未发现风险条款" :image-size="80" />
          </div>

          <!-- 综合建议 -->
          <div v-if="diagnosis.suggestions" class="suggestions-section" style="margin-top: 20px;">
            <h4 style="margin-bottom: 10px; color: #333;">综合修改建议</h4>
            <div style="padding: 12px; background-color: #f8f9fa; border-radius: 6px; border:none;">
              <pre style="margin: 0; background: transparent; border: none; padding: 0; font-family: inherit;">{{ diagnosis.suggestions }}</pre>
            </div>
          </div>
        </div>
          
        <!-- 诊断加载失败时显示简单提示 -->
        <div v-else class="diagnosis-error">
          <pre style="margin: 0; background: transparent; border: none; padding: 0; font-family: inherit;">
            无法加载诊断结果信息
          </pre>
        </div>
      </div>

    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="closeDialog">关闭</el-button>
        <el-button type="primary" @click="exportRecord" v-if="record">导出记录</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { ContractUploadWithDiagnosis, ContractDiagnosis } from '../types/contract'

// 扩展ContractDiagnosis类型
interface ExtendedContractDiagnosis extends ContractDiagnosis {
  model_used?: string
  analysis_time?: number
}

// 定义组件属性
interface Props {
  visible: boolean
  recordData?: ContractUploadWithDiagnosis | null
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  recordData: null
})

// 定义组件事件
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'close': []
}>()

// 响应式数据
const dialogVisible = ref(false)
const record = ref<ContractUploadWithDiagnosis | null>(null)
const diagnosis = ref<ExtendedContractDiagnosis | null>(null)
const loading = ref(false)

// 加载诊断数据
const loadDiagnosis = async () => {
  if (!record.value) {
    diagnosis.value = null
    return
  }
  
  try {
    loading.value = true
    
    // 首先检查上传记录中是否已经包含诊断数据
    if (record.value.diagnoses && record.value.diagnoses.length > 0) {
      // 使用最新的诊断结果（按创建时间排序）
      const sortedDiagnoses = [...record.value.diagnoses].sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      const latestDiagnosis = sortedDiagnoses[0]
      
      // 尝试获取完整的诊断详情
      try {
        // 导入API函数
        const { getContractDiagnosis } = await import('@/api/contract')
        const fullDiagnosis = await getContractDiagnosis(latestDiagnosis.id)
        
        // 合并数据，确保包含所有字段
        // 注意：fullDiagnosis 是 ContractDiagnosis 类型，不包含 model_used 和 analysis_time
        // 我们需要从响应中获取这些字段，或者使用默认值
        diagnosis.value = {
          ...fullDiagnosis,
          model_used: fullDiagnosis.model_used || '未知模型',
          analysis_time: fullDiagnosis.analysis_time || 0
        } as ExtendedContractDiagnosis
      } catch (apiError) {
        // 如果API调用失败，使用本地数据
        console.warn('获取完整诊断详情失败，使用本地数据:', apiError)
        // 使用类型断言来处理可能存在的额外字段
        const diagnosisData = latestDiagnosis as any
        diagnosis.value = {
          ...latestDiagnosis,
          model_used: diagnosisData.model_used || '未知模型',
          analysis_time: diagnosisData.analysis_time || 0
        } as ExtendedContractDiagnosis
      }
    } else {
      // 没有诊断数据
      diagnosis.value = null
      ElMessage.warning('该合同暂无诊断结果')
    }
  } catch (error: any) {
    console.error('加载诊断结果失败:', error)
    diagnosis.value = null
    ElMessage.error('加载诊断结果失败')
  } finally {
    loading.value = false
  }
}

// 监听属性变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && record.value) {
    loadDiagnosis()
  }
})

watch(() => props.recordData, async (newVal) => {
  record.value = newVal
  if (newVal && dialogVisible.value) {
    await loadDiagnosis()
  }
})

// 监听对话框可见性变化
watch(dialogVisible, (newVal) => {
  if (!newVal) {
    emit('update:visible', false)
    emit('close')
  }
})

// 状态映射
const getStatusText = (status?: string) => {
  if (!status) return '未知状态'
  const statusMap: Record<string, string> = {
    'uploaded': '已上传',
    'parsing': '解析中',
    'analyzing': '分析中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || status
}

// 状态标签类型
const getStatusTagType = (status?: string) => {
  if (!status) return 'info'
  switch (status) {
    case 'uploaded': return 'info'
    case 'parsing': return 'warning'
    case 'analyzing': return 'warning'
    case 'completed': return 'success'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

// 风险等级映射
const getRiskLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    'high': '高风险',
    'medium': '中风险',
    'low': '低风险'
  }
  return levelMap[level] || level
}

const getRiskLevelTagType = (level: string) => {
  switch (level) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'success'
    default: return 'info'
  }
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

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 导出记录
const exportRecord = () => {
  if (!record.value) return
  
  try {
    // 创建导出数据
    const exportData = {
      record_id: record.value.id,
      filename: record.value.filename,
      created_at: record.value.created_at,
      status: record.value.status || 'unknown',
      file_size: record.value.file_size,
      diagnosis: diagnosis.value
    }
    
    // 创建Blob并下载
    const dataStr = JSON.stringify(exportData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `contract_diagnosis_${record.value.id}_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success('记录导出成功')
  } catch (error) {
    console.error('导出记录失败:', error)
    ElMessage.error('导出记录失败')
  }
}

// 关闭对话框
const closeDialog = () => {
  dialogVisible.value = false
}
</script>

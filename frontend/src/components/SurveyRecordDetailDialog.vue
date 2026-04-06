/* 企业调查表查看详细弹窗 - 从history.vue中提取 */

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`调查记录详情 - ID: ${record?.id || ''}`"
    width="900px"
    :close-on-click-modal="false"
  >
    <div class="record-detail-content" v-if="record">
      <div class="record-header">
        <div class="record-info">
          <p><strong>提交时间：</strong>{{ formatDateTime(record.created_at) }}</p>
          <p><strong>状态：</strong>
            <el-tag :type="getStatusTagType(record.status)" size="small">
              {{ getStatusText(record.status) }}
            </el-tag>
          </p>
          <p><strong>模板ID：</strong>{{ record.template_id }}</p>
        </div>
      </div>

      <el-divider>调查表内容</el-divider>
        
      <div class="survey-answers">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-template">
          <el-skeleton :rows="5" animated />
        </div>
         
        <!-- 动态显示模板字段 -->
        <div v-else-if="template && template.fields">
          <div class="template-info" style="margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 8px;">
            <p><strong>模板名称：</strong>{{ template.name }}</p>
            <p><strong>模板版本：</strong>{{ template.version }}</p>
            <p v-if="template.description"><strong>模板描述：</strong>{{ template.description }}</p>
          </div>
           
          <el-descriptions :column="2" border>
            <template v-for="(fieldDef, fieldKey) in template.fields" :key="fieldKey">
              <el-descriptions-item
                :label="getFieldLabel(fieldKey, fieldDef)"
                :span="fieldDef.type === 'textarea' || fieldKey === 'businessScope' || fieldKey === 'remarks' ? 2 : 1"
              >
                <template v-if="fieldDef.type === 'checkbox' && Array.isArray(record.answers?.[fieldKey])">
                  <div>
                    <el-tag
                      v-for="item in record.answers[fieldKey]"
                      :key="item"
                      size="small"
                      style="margin-right: 5px; margin-bottom: 5px;"
                    >
                      {{ formatFieldValue(fieldKey, fieldDef, item) }}
                    </el-tag>
                  </div>
                </template>
                <template v-else>
                  {{ formatFieldValue(fieldKey, fieldDef, record.answers?.[fieldKey]) }}
                </template>
              </el-descriptions-item>
            </template>
          </el-descriptions>
        </div>
         
        <!-- 模板加载失败时显示简单提示 -->
        <div v-else class="template-error">
          <p style="color: #f56c6c; text-align: center; padding: 20px;">
            无法加载调查表模板信息
          </p>
        </div>
      </div>

      <el-divider>法律建议</el-divider>
       
      <div class="suggestions-section" v-if="record.suggestions && record.suggestions.length > 0">
        <div v-for="suggestion in record.suggestions" :key="suggestion.id" class="suggestion-item">
          <div class="suggestion-header">
            <el-tag :type="getSuggestionTagType(suggestion.analysis_type)" size="small">
              {{ getAnalysisTypeText(suggestion.analysis_type) }}
            </el-tag>
            <span class="suggestion-time">生成时间: {{ formatDateTime(suggestion.created_at) }}</span>
          </div>
          <div class="suggestion-content">
            <p>{{ suggestion.suggestion }}</p>
          </div>
          <div v-if="suggestion.trigger_changes" class="trigger-changes">
            <p><strong>触发变更的字段：</strong></p>
            <pre>{{ JSON.stringify(suggestion.trigger_changes, null, 2) }}</pre>
          </div>
        </div>
      </div>
      <div v-else class="no-suggestions">
        <el-empty description="暂无法律建议" :image-size="80" />
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
import { getSurveyTemplate } from '../api/survey'
import type { SurveyTemplate, SurveyRecord } from '../types/survey'

// 定义组件属性
interface Props {
  visible: boolean
  recordData?: SurveyRecord | null
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
const record = ref<SurveyRecord | null>(null)
const template = ref<SurveyTemplate | null>(null)
const loading = ref(false)

// 加载模板数据
const loadTemplate = async () => {
  if (!record.value?.template_id) {
    template.value = null
    return
  }
  
  try {
    loading.value = true
    const templateData = await getSurveyTemplate(record.value.template_id)
    template.value = templateData
  } catch (error: any) {
    console.error('加载模板失败:', error)
    template.value = null
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
  }
}

// 监听属性变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && record.value) {
    loadTemplate()
  }
})

watch(() => props.recordData, async (newVal) => {
  record.value = newVal
  if (newVal && dialogVisible.value) {
    await loadTemplate()
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
const getStatusText = (status: string) => {
  return status
}

// 状态标签类型
const getStatusTagType = (status: string) => {
  switch (status) {
    case 'draft': return 'info'
    case 'submitted': return 'warning'
    case 'analyzed': return 'success'
    default: return 'info'
  }
}

// 法律建议类型映射
const getSuggestionTagType = (type: string = 'general') => {
  switch (type) {
    case 'labor': return 'warning'
    case 'contract': return 'success'
    case 'ip': return 'info'
    case 'tax': return 'danger'
    case 'compliance': return 'primary'
    default: return ''
  }
}

// 获取分析类型文本
const getAnalysisTypeText = (type: string = 'general') => {
  return type === 'general' ? '法律建议' : `${type}建议`
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

// 根据字段类型格式化值
const formatFieldValue = (_fieldKey: string, fieldDef: any, value: any) => {
  if (value === undefined || value === null || value === '') {
    return '未填写'
  }
  
  const fieldType = fieldDef?.type || 'text'
  
  switch (fieldType) {
    case 'select':
      // 查找选项标签
      if (fieldDef.options && Array.isArray(fieldDef.options)) {
        const option = fieldDef.options.find((opt: any) => opt.value === value)
        return option ? option.label : value
      }
      return value
    
    case 'checkbox':
      // 多选值
      if (Array.isArray(value) && fieldDef.options && Array.isArray(fieldDef.options)) {
        return value.map(v => {
          const option = fieldDef.options.find((opt: any) => opt.value === v)
          return option ? option.label : v
        }).join(', ')
      }
      return Array.isArray(value) ? value.join(', ') : value
    
    case 'switch':
    case 'boolean':
      // 直接显示布尔值，true/false
      return value ? 'true' : 'false'
    
    case 'date':
      return value
    
    case 'number':
      // 直接显示数字值，单位信息应该从模板配置中获取
      return value
    
    default:
      return value
  }
}

// 获取字段显示标签
const getFieldLabel = (fieldKey: string, fieldDef: any) => {
  return fieldDef?.label || fieldKey
}

// 导出记录
const exportRecord = () => {
  if (!record.value) return
  
  try {
    // 创建导出数据
    const exportData = {
      record_id: record.value.id,
      created_at: record.value.created_at,
      status: record.value.status,
      answers: record.value.answers,
      suggestions: record.value.suggestions || []
    }
    
    // 创建Blob并下载
    const dataStr = JSON.stringify(exportData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `survey_record_${record.value.id}_${new Date().toISOString().split('T')[0]}.json`
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

<style scoped>
@import '@/assets/css/dialog.css';
</style>
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
          <div class="suggestion-content markdown-content" v-html="renderMarkdown(suggestion.suggestion)"></div>
          <div v-if="suggestion.trigger_changes && Object.keys(suggestion.trigger_changes).length > 0" class="trigger-changes">
            <p><strong>触发变更的字段：</strong></p>
            <div class="trigger-changes-list">
              <div v-for="(value, field) in suggestion.trigger_changes" :key="field" class="trigger-change-item">
                <span class="trigger-field">{{ field }}:</span>
                <span class="trigger-value">{{ formatTriggerValue(value) }}</span>
              </div>
            </div>
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
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'
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

// 渲染Markdown内容
const renderMarkdown = (content: string): string => {
  if (!content) return ''
  return md.render(content)
}

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

// 格式化触发变更字段的值
const formatTriggerValue = (value: any): string => {
  if (value === undefined || value === null) {
    return '未设置'
  }
  
  if (typeof value === 'boolean') {
    return value ? '是' : '否'
  }
  
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value, null, 2)
    } catch {
      return String(value)
    }
  }
  
  return String(value)
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
@import '@/assets/css/pages/dialog.css';

/* Markdown内容样式 */
.markdown-content {
  line-height: 1.6;
  color: #333;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  margin-top: 1em;
  margin-bottom: 0.5em;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-content h1 {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-content h2 {
  font-size: 1.3em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-content h3 {
  font-size: 1.1em;
}

.markdown-content p {
  margin-top: 0;
  margin-bottom: 1em;
}

.markdown-content ul,
.markdown-content ol {
  padding-left: 2em;
  margin-bottom: 1em;
}

.markdown-content li {
  margin-bottom: 0.25em;
}

.markdown-content blockquote {
  margin: 0;
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
}

.markdown-content code {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

.markdown-content pre {
  padding: 1em;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
  margin-bottom: 1em;
}

.markdown-content pre code {
  padding: 0;
  background-color: transparent;
  border-radius: 0;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1em;
}

.markdown-content th,
.markdown-content td {
  padding: 0.5em 1em;
  border: 1px solid #dfe2e5;
}

.markdown-content th {
  background-color: #f6f8fa;
  font-weight: 600;
}

.markdown-content a {
  color: #0366d6;
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

/* 触发变更字段样式 */
.trigger-changes-list {
  margin-top: 10px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.trigger-change-item {
  display: flex;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #dee2e6;
}

.trigger-change-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.trigger-field {
  font-weight: 600;
  color: #495057;
  min-width: 150px;
  flex-shrink: 0;
}

.trigger-value {
  color: #212529;
  flex-grow: 1;
  word-break: break-word;
}
</style>
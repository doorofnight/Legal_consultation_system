<template>
  <div class="survey-container">
    <el-card class="survey-header-card">
      <div class="survey-header">
        <div class="header-left">
          <el-icon ><Document /></el-icon>
          <h2>企业调查表</h2>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="showTemplateSelectDialog = true">
            选定企业调查表
          </el-button>
          <el-button @click="showTemplateCreateDialog = true">
            创建企业调查表
          </el-button>
        </div>
      </div>
      <div class="survey-subtitle">
        <p v-if="selectedTemplate">
          当前使用模板：<strong>{{ selectedTemplate.name }}</strong> - {{ selectedTemplate.description }}
        </p>
        <p v-else>
          请先选择一个调查表模板，或创建一个新的模板。
        </p>
        <p class="survey-tip">任何字段修改都会触发AI分析，生成针对性的法律建议。</p>
      </div>
    </el-card>

    <div class="survey-content">
      <el-card class="survey-form-card">
        <template #header>
          <div class="form-header">
            <h3 v-if="selectedTemplate">{{ selectedTemplate.name }}</h3>
            <h3 v-else>企业调查表</h3>
            <p class="form-description" v-if="selectedTemplate">
              请填写以下信息，{{ hasRequiredFields ? '标*的字段为必填项' : '所有字段均为选填项' }}
            </p>
            <p class="form-description" v-else>
              请先选择一个调查表模板
            </p>
          </div>
        </template>
        
        <!-- 动态表单 -->
        <div v-if="selectedTemplate && templateFields" class="dynamic-form-container">
          <el-form 
            :model="surveyForm" 
            :rules="formRules" 
            ref="surveyFormRef" 
            label-width="120px" 
            class="survey-form"
          >
            <!-- 动态生成表单字段 -->
            <template v-for="(field, key) in templateFields" :key="key">
              <!-- 文本字段 -->
              <el-form-item 
                v-if="field.type === 'text'" 
                :label="field.label" 
                :prop="key"
                :required="field.required"
              >
                <el-input 
                  v-model="surveyForm[key]" 
                  :placeholder="field.placeholder || `请输入${field.label}`" 
                />
              </el-form-item>
              
              <!-- 文本域字段 -->
              <el-form-item 
                v-else-if="field.type === 'textarea'" 
                :label="field.label" 
                :prop="key"
                :required="field.required"
              >
                <el-input
                  v-model="surveyForm[key]"
                  type="textarea"
                  :rows="3"
                  :placeholder="field.placeholder || `请输入${field.label}`"
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
              
              <!-- 数字字段 -->
              <el-form-item 
                v-else-if="field.type === 'number'" 
                :label="field.label" 
                :prop="key"
                :required="field.required"
              >
                <el-input-number 
                  v-model="surveyForm[key]" 
                  :min="0" 
                  :placeholder="field.placeholder || `请输入${field.label}`"
                  style="width: 100%;"
                />
              </el-form-item>
              
              <!-- 选择字段 -->
              <el-form-item 
                v-else-if="field.type === 'select'" 
                :label="field.label" 
                :prop="key"
                :required="field.required"
              >
                <el-select 
                  v-model="surveyForm[key]" 
                  :placeholder="field.placeholder || `请选择${field.label}`"
                  style="width: 100%;"
                >
                  <el-option
                    v-for="option in field.options || []"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </el-form-item>
              
              <!-- 多选字段 -->
              <el-form-item 
                v-else-if="field.type === 'checkbox'" 
                :label="field.label" 
                :prop="key"
                :required="field.required"
              >
                <el-checkbox-group v-model="surveyForm[key]">
                  <el-checkbox
                    v-for="option in field.options || []"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-checkbox-group>
              </el-form-item>
              
              <!-- 日期字段 -->
              <el-form-item 
                v-else-if="field.type === 'date'" 
                :label="field.label" 
                :prop="key"
                :required="field.required"
              >
                <el-date-picker
                  v-model="surveyForm[key]"
                  type="date"
                  :placeholder="field.placeholder || `选择${field.label}`"
                  value-format="YYYY-MM-DD"
                  style="width: 100%;"
                />
              </el-form-item>
              
              <!-- 开关字段 -->
              <el-form-item 
                v-else-if="field.type === 'switch'" 
                :label="field.label" 
                :prop="key"
                :required="field.required"
              >
                <el-switch v-model="surveyForm[key]" />
              </el-form-item>
              
              <!-- 默认文本字段 -->
              <el-form-item 
                v-else
                :label="field.label" 
                :prop="key"
                :required="field.required"
              >
                <el-input 
                  v-model="surveyForm[key]" 
                  :placeholder="field.placeholder || `请输入${field.label}`" 
                />
              </el-form-item>
            </template>
            
            <!-- 提交按钮 -->
            <el-form-item v-if="selectedTemplate">
              <el-button type="primary" size="large" @click="handleSubmitSurvey" :loading="isSubmitting">
                提交调查表
              </el-button>
              <el-button size="large" @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 无模板时的提示 -->
        <div v-else class="no-template">
          <el-empty description="请先选择一个调查表模板" :image-size="100">
            <template #description>
              <p>您还没有选择任何调查表模板</p>
              <p class="empty-tip">请点击右上角的"选定企业调查表"按钮选择一个模板</p>
            </template>
            <el-button type="primary" @click="showTemplateSelectDialog = true">
              选择模板
            </el-button>
          </el-empty>
        </div>
      </el-card>

      <div class="survey-sidebar">
        <el-card class="progress-card" v-if="hasPreviousRecord">
          <template #header>
            <div class="progress-header">
              <el-icon><TrendCharts /></el-icon>
              <h3>变更分析</h3>
            </div>
          </template>
          <div class="progress-content">
            <p>检测到您有历史记录，系统将对比变更并提供针对性建议。</p>
            <el-progress :percentage="analysisProgress" :status="analysisStatus" />
            <p class="progress-tip">已识别 {{ effectiveChangedFieldsCount }} 个字段变更</p>
            
            <!-- 详细变更内容 -->
            <div v-if="effectiveChangedFieldsDetails.length > 0" class="changed-fields-details">
              <el-collapse>
                <el-collapse-item title="查看详细变更内容">
                  <div class="changed-fields-list">
                    <div v-for="field in effectiveChangedFieldsDetails" :key="field.fieldKey" class="changed-field-item">
                      <div class="field-header">
                        <span class="field-label">{{ field.fieldLabel }}</span>
                        <el-tag size="small" type="warning">已修改</el-tag>
                      </div>
                      <div class="field-values">
                        <div class="value-item">
                          <span class="value-label">原值：</span>
                          <span class="value-content">{{ formatFieldValue(field.previousValue) }}</span>
                        </div>
                        <div class="value-item">
                          <span class="value-label">新值：</span>
                          <span class="value-content new-value">{{ formatFieldValue(field.currentValue) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
            
            <!-- 无变更时的提示 -->
            <div v-else-if="hasPreviousRecord && effectiveChangedFieldsDetails.length === 0" class="no-changes">
              <p class="no-changes-text">当前表单与历史记录一致，无字段变更。</p>
            </div>
          </div>
        </el-card>
        
        <!-- 模板信息卡片 -->
        <el-card class="template-info-card" v-if="selectedTemplate">
          <template #header>
            <div class="template-info-header">
              <el-icon><InfoFilled /></el-icon>
              <h3>模板信息</h3>
            </div>
          </template>
          <div class="template-info-content">
            <div class="info-item">
              <span class="info-label">模板名称：</span>
              <span class="info-value">{{ selectedTemplate.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">版本：</span>
              <span class="info-value">{{ selectedTemplate.version }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">字段数量：</span>
              <span class="info-value">{{ Object.keys(templateFields || {}).length }} 个</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间：</span>
              <span class="info-value">{{ formatDate(selectedTemplate.created_at) }}</span>
            </div>
            <div v-if="selectedTemplate.description" class="info-item description">
              <span class="info-label">描述：</span>
              <span class="info-value">{{ selectedTemplate.description }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 法律建议弹窗 -->
    <LegalSuggestionDialog
      v-model="suggestionDialogVisible"
      :ai-generating="aiGenerating"
      :ai-progress="aiProgress"
      :suggestion="currentSuggestion"
      :template-fields="templateFields"
      @close="closeSuggestionDialog"
    />

    <!-- 模板选择弹窗 -->
    <SurveyTemplateSelectDialog
      v-model="showTemplateSelectDialog"
      @select="handleTemplateSelect"
      @edit="handleTemplateEdit"
      @create-new="showTemplateCreateDialog = true"
    />

    <!-- 模板创建弹窗 -->
    <SurveyTemplateCreateDialog
      v-model="showTemplateCreateDialog"
      :template-to-edit="templateToEdit"
      @created="handleTemplateCreated"
      @updated="handleTemplateUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
// 从图标集中管理文件导入图标
import {
  Document,
  TrendCharts,
  InfoFilled
} from '@/icons'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { submitSurvey as apiSubmitSurvey, getLatestSuggestion, getSurveyHistory, getSurveyTemplates } from '@/api/survey'
import type { SurveySubmitRequest, LegalSuggestion, SurveyTemplate } from '@/types/survey'
import SurveyTemplateSelectDialog from '@/components/SurveyTemplateSelectDialog.vue'
import SurveyTemplateCreateDialog from '@/components/SurveyTemplateCreateDialog.vue'
import LegalSuggestionDialog from '@/components/LegalSuggestionDialog.vue'
import { initializeFormData, generateFormRules } from '@/utils/dynamicForm'

// 导入共享CSS
import '@/assets/css/variables.css'
import '@/assets/css/utilities.css'
import '@/assets/css/survey.css'

// 表单引用
const surveyFormRef = ref<FormInstance>()

// 模板相关状态
const selectedTemplate = ref<SurveyTemplate | null>(null)
const templateFields = ref<Record<string, any> | null>(null)
const showTemplateSelectDialog = ref(false)
const showTemplateCreateDialog = ref(false)
const templateToEdit = ref<any>(null)

// 表单数据
const surveyForm = reactive<Record<string, any>>({})

// 表单验证规则
const formRules = reactive<FormRules>({})

// 状态变量
const isSubmitting = ref(false)
const suggestionDialogVisible = ref(false)
const currentSuggestion = ref<LegalSuggestion | null>(null)
const hasPreviousRecord = ref(false)
const changedFieldsCount = ref(0)
const previousAnswers = ref<Record<string, any> | null>(null)
const changedFieldsDetails = ref<Array<{
  fieldKey: string
  fieldLabel: string
  previousValue: any
  currentValue: any
}>>([])

// AI生成状态
const aiGenerating = ref(false)
const aiProgress = ref(0)

// 计算属性
const hasRequiredFields = computed(() => {
  if (!templateFields.value) return false
  return Object.values(templateFields.value).some((field: any) => field.required)
})

// 获取变更详情，优先使用trigger_changes
const effectiveChangedFieldsDetails = computed(() => {
  console.log('currentSuggestion:', currentSuggestion.value)
  console.log('trigger_changes:', currentSuggestion.value?.trigger_changes)
  
  // 如果currentSuggestion中有trigger_changes，使用它
  if (currentSuggestion.value?.trigger_changes) {
    const triggerChanges = currentSuggestion.value.trigger_changes
    const details: Array<{
      fieldKey: string
      fieldLabel: string
      previousValue: any
      currentValue: any
    }> = []
    
    Object.entries(triggerChanges).forEach(([key, changeInfo]) => {
      const fieldLabel = templateFields.value?.[key]?.label || key
      
      // 尝试解析changeInfo，它可能是各种格式
      let previousValue: any = null
      let currentValue: any = null
      
      if (changeInfo && typeof changeInfo === 'object') {
        // 格式1: {old: ..., new: ...}
        if ('old' in changeInfo && 'new' in changeInfo) {
          previousValue = changeInfo.old
          currentValue = changeInfo.new
        }
        // 格式2: {previous: ..., current: ...}
        else if ('previous' in changeInfo && 'current' in changeInfo) {
          previousValue = changeInfo.previous
          currentValue = changeInfo.current
        }
        // 格式3: 直接包含原值和新值的对象
        else {
          // 尝试获取第一个和第二个值
          const values = Object.values(changeInfo)
          if (values.length >= 2) {
            previousValue = values[0]
            currentValue = values[1]
          } else if (values.length === 1) {
            // 如果只有一个值，可能是新值，原值为空
            currentValue = values[0]
            previousValue = null
          }
        }
      } else {
        // 如果不是对象，直接作为当前值
        currentValue = changeInfo
        previousValue = null
      }
      
      details.push({
        fieldKey: key,
        fieldLabel,
        previousValue,
        currentValue
      })
    })
    
    console.log('Parsed trigger_changes details:', details)
    return details
  }
  
  console.log('No trigger_changes, using local calculation')
  // 否则使用本地计算的变更
  return changedFieldsDetails.value
})

// 基于有效变更详情计算变更数量
const effectiveChangedFieldsCount = computed(() => {
  return effectiveChangedFieldsDetails.value.length
})

const analysisProgress = computed(() => {
  return Math.min(effectiveChangedFieldsCount.value * 10, 100)
})

const analysisStatus = computed(() => {
  return effectiveChangedFieldsCount.value > 0 ? 'success' : 'warning'
})

// 计算变更字段数量和详情
const calculateChangedFields = () => {
  if (!previousAnswers.value || !templateFields.value) {
    changedFieldsCount.value = 0
    changedFieldsDetails.value = []
    return
  }
  
  let count = 0
  const currentAnswers = surveyForm
  const details: Array<{
    fieldKey: string
    fieldLabel: string
    previousValue: any
    currentValue: any
  }> = []
  
  Object.keys(templateFields.value).forEach(key => {
    const currentValue = currentAnswers[key]
    const previousValue = previousAnswers.value?.[key]
    const fieldLabel = templateFields.value?.[key]?.label || key
    
    // 比较值是否不同
    if (JSON.stringify(currentValue) !== JSON.stringify(previousValue)) {
      count++
      details.push({
        fieldKey: key,
        fieldLabel,
        previousValue,
        currentValue
      })
    }
  })
  
  changedFieldsCount.value = count
  changedFieldsDetails.value = details
}

// 方法
// 获取用户ID（从localStorage或生成新的）
const getUserId = () => {
  let userId = localStorage.getItem('legal_system_user_id')
  if (!userId) {
    // 生成新的用户ID并保存
    userId = 'user_' + Date.now()
    localStorage.setItem('legal_system_user_id', userId)
  }
  return userId
}

// 处理模板选择
const handleTemplateSelect = (template: SurveyTemplate) => {
  selectedTemplate.value = template
  templateFields.value = template.fields || {}
  
  // 初始化表单数据
  Object.assign(surveyForm, initializeFormData(templateFields.value))
  
  // 生成表单验证规则
  Object.assign(formRules, generateFormRules(templateFields.value))
  
  // 计算变更字段数量
  calculateChangedFields()
  
  ElMessage.success(`已选择模板: ${template.name}`)
}

// 处理模板创建
const handleTemplateCreated = (template: SurveyTemplate) => {
  ElMessage.success(`模板创建成功: ${template.name}`)
  // 自动选择新创建的模板
  handleTemplateSelect(template)
}

// 处理模板编辑
const handleTemplateEdit = (template: SurveyTemplate) => {
  templateToEdit.value = template
  showTemplateCreateDialog.value = true
}

// 处理模板更新
const handleTemplateUpdated = (template: SurveyTemplate) => {
  ElMessage.success(`模板更新成功: ${template.name}`)
  
  // 如果当前选中的模板是刚刚更新的模板，刷新当前模板
  if (selectedTemplate.value?.id === template.id) {
    handleTemplateSelect(template)
  }
  
  // 重置编辑状态
  templateToEdit.value = null
}

// 提交调查表
const handleSubmitSurvey = async () => {
  if (!selectedTemplate.value) {
    ElMessage.warning('请先选择一个调查表模板')
    return
  }
  
  try {
    await surveyFormRef.value?.validate()
    
    isSubmitting.value = true
    
    const request: SurveySubmitRequest = {
      template_id: selectedTemplate.value.id,
      answers: { ...surveyForm },
      user_id: getUserId()
    }
    
    // 显示弹窗并开始AI生成进度
    suggestionDialogVisible.value = true
    aiGenerating.value = true
    const progressInterval = simulateAIProgress()
    
    const response = await apiSubmitSurvey(request)
    
    // 停止进度模拟
    clearInterval(progressInterval)
    aiProgress.value = 100
    
    // 短暂延迟以显示100%进度
    await new Promise(resolve => setTimeout(resolve, 500))
    
    console.log('后端返回的响应:', response)
    console.log('response.suggestion:', response.suggestion)
    
    if (response.suggestion) {
      console.log('设置currentSuggestion:', response.suggestion)
      currentSuggestion.value = response.suggestion
      ElMessage.success('调查表提交成功！已生成法律建议')
    } else {
      console.warn('后端没有返回suggestion数据')
      ElMessage.success('调查表提交成功！')
    }
    
    // 重置AI生成状态
    aiGenerating.value = false
    
    // 重置表单
    resetForm()
    
  } catch (error: any) {
    // 停止进度模拟
    aiGenerating.value = false
    ElMessage.error(error.message || '提交失败，请重试')
  } finally {
    isSubmitting.value = false
  }
}

const resetForm = () => {
  if (selectedTemplate.value && templateFields.value) {
    // 重置为默认值
    Object.assign(surveyForm, initializeFormData(templateFields.value))
  }
  surveyFormRef.value?.clearValidate()
}

const closeSuggestionDialog = () => {
  suggestionDialogVisible.value = false
}

// 模拟AI生成进度
const simulateAIProgress = () => {
  aiGenerating.value = true
  aiProgress.value = 0
  
  const interval = setInterval(() => {
    if (aiProgress.value < 90) {
      aiProgress.value += Math.floor(Math.random() * 15) + 5
      if (aiProgress.value > 90) aiProgress.value = 90
    }
  }, 500)
  
  return interval
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 格式化字段值用于显示
const formatFieldValue = (value: any): string => {
  if (value === null || value === undefined || value === '') {
    return '(空)'
  }
  
  if (Array.isArray(value)) {
    return value.length > 0 ? value.join(', ') : '(空数组)'
  }
  
  if (typeof value === 'boolean') {
    return value ? '是' : '否'
  }
  
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value)
    } catch {
      return '(对象)'
    }
  }
  
  return String(value)
}

// 监听表单值变化，更新变更字段数量
watch(
  () => ({ ...surveyForm }),
  () => {
    calculateChangedFields()
  },
  { deep: true }
)

// 监听模板创建对话框关闭，重置编辑状态
watch(
  () => showTemplateCreateDialog.value,
  (newValue) => {
    if (!newValue) {
      // 对话框关闭时，如果不是刚刚更新了模板，则重置编辑状态
      setTimeout(() => {
        templateToEdit.value = null
      }, 100)
    }
  }
)

// 初始化
onMounted(async () => {
  // 尝试加载默认模板
  try {
    const templates = await getSurveyTemplates(true)
    if (templates && templates.length > 0) {
      // 选择第一个模板作为默认
      handleTemplateSelect(templates[0])
    }
  } catch (error) {
    console.error('加载模板失败:', error)
  }
  
  // 检查是否有历史记录
  try {
    const userId = getUserId()
    const history = await getSurveyHistory(userId, 1, 0)
    hasPreviousRecord.value = history.total > 0
    
    if (hasPreviousRecord.value && history.records && history.records.length > 0) {
      // 获取最新的历史记录
      const latestRecord = history.records[0]
      previousAnswers.value = latestRecord.answers || {}
      
      // 从最新记录中获取建议（优先使用记录中的建议）
      if (latestRecord.suggestions && latestRecord.suggestions.length > 0) {
        // 获取最新的建议（按创建时间排序，最后一个可能是最新的）
        const latestSuggestion = latestRecord.suggestions[latestRecord.suggestions.length - 1]
        currentSuggestion.value = latestSuggestion
        console.log('Found suggestion in record:', latestSuggestion)
      } else {
        // 如果没有，尝试获取最新的建议
        const suggestion = await getLatestSuggestion(userId)
        if (suggestion) {
          currentSuggestion.value = suggestion
          console.log('Found suggestion from API:', suggestion)
        }
      }
      
      // 计算初始变更字段数量
      calculateChangedFields()
    }
  } catch (error) {
    console.error('初始化失败:', error)
  }
})
</script>

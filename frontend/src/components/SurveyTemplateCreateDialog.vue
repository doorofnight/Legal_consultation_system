/* 创建企业调查表弹窗 - 从survey.vue中提取 */

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="template-create-dialog">
      <!-- 基本信息 -->
      <el-form
        :model="formData"
        :rules="formRules"
        ref="formRef"
        label-width="100px"
        class="template-form"
      >
        <el-form-item label="模板名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入模板名称，如：企业基本信息调查表"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="模板描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模板描述，说明此模板的用途和适用场景"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="模板版本" prop="version">
          <el-input
            v-model="formData.version"
            placeholder="请输入版本号，如：1.0"
            style="width: 200px;"
          />
        </el-form-item>

        <!-- 字段管理 -->
        <el-form-item label="字段定义" required>
          <div class="fields-section">
            <div class="fields-header">
              <div class="fields-header-left">
                <h4>字段列表</h4>
                <p class="fields-tip">定义调查表中需要填写的各个字段，每个字段对应一个问题</p>
              </div>
              <el-button type="primary" size="small" @click="handleAddField">
                <el-icon><Plus /></el-icon>
                添加字段
              </el-button>
            </div>
            
            <div class="creation-tips">
              <el-alert title="创建提示" type="info" :closable="false">
                <ul class="tips-list">
                  <li><strong>字段键名</strong>：英文名称，用于后台识别，如：companyName</li>
                  <li><strong>字段标签</strong>：中文名称，显示给用户看，如：企业名称</li>
                  <li><strong>字段类型</strong>：根据输入内容选择合适类型</li>
                  <li><strong>选项配置</strong>：仅"单选"和"多选"类型需要配置选项</li>
                </ul>
              </el-alert>
            </div>

            <div class="fields-list">
              <div
                v-for="(field, index) in formData.fields"
                :key="index"
                class="field-item"
              >
                <div class="field-header">
                  <span class="field-index">字段 {{ index + 1 }}</span>
                  <div class="field-actions">
                    <el-button
                      type="danger"
                      size="small"
                      text
                      @click="handleRemoveField(index)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>

                <div class="field-content">
                  <el-row :gutter="20">
                    <el-col :span="8">
                      <el-form-item
                        :prop="`fields[${index}].key`"
                        :rules="fieldKeyRules"
                        label="字段键名"
                        label-width="80px"
                      >
                        <el-input
                          v-model="field.key"
                          placeholder="英文键名，如：companyName"
                          @blur="validateFieldKey(field, index)"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item
                        :prop="`fields[${index}].label`"
                        :rules="fieldLabelRules"
                        label="字段标签"
                        label-width="80px"
                      >
                        <el-input
                          v-model="field.label"
                          placeholder="中文标签，如：企业名称"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item
                        label="字段类型"
                        label-width="80px"
                      >
                        <el-select
                          v-model="field.type"
                          placeholder="选择字段类型"
                          style="width: 100%;"
                          @change="handleFieldTypeChange(field)"
                        >
                          <el-option label="单行文本（短文本输入）" value="text" />
                          <el-option label="多行文本（长文本输入）" value="textarea" />
                          <el-option label="数字（只能输入数字）" value="number" />
                          <el-option label="单选（下拉选择）" value="select" />
                          <el-option label="多选（复选框）" value="checkbox" />
                          <el-option label="日期（选择日期）" value="date" />
                          <el-option label="开关（是/否）" value="switch" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <!-- 字段类型特定配置 -->
                  <div v-if="field.type === 'select' || field.type === 'checkbox'" class="field-options">
                    <el-form-item
                      label="选项配置"
                      label-width="80px"
                    >
                      <div class="options-list">
                        <div
                          v-for="(option, optIndex) in field.options || []"
                          :key="optIndex"
                          class="option-item"
                        >
                          <el-input
                            v-model="option.label"
                            placeholder="选项标签"
                            style="width: 150px; margin-right: 10px;"
                          />
                          <el-input
                            v-model="option.value"
                            placeholder="选项值"
                            style="width: 150px; margin-right: 10px;"
                          />
                          <el-button
                            type="danger"
                            size="small"
                            text
                            @click="handleRemoveOption(field, optIndex)"
                          >
                            <el-icon><Delete /></el-icon>
                          </el-button>
                        </div>
                        <el-button
                          type="primary"
                          size="small"
                          text
                          @click="handleAddOption(field)"
                        >
                          <el-icon><Plus /></el-icon>
                          添加选项
                        </el-button>
                      </div>
                    </el-form-item>
                  </div>

                  <!-- 其他字段配置 -->
                  <el-row :gutter="20" class="field-config">
                    <el-col :span="8">
                      <el-form-item label="是否必填" label-width="80px">
                        <el-switch v-model="field.required" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="默认值" label-width="80px">
                        <el-input
                          v-model="field.defaultValue"
                          :placeholder="getDefaultValuePlaceholder(field.type)"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="占位文本" label-width="80px">
                        <el-input
                          v-model="field.placeholder"
                          placeholder="输入提示文本"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>

                  <!-- 验证规则 -->
                  <div v-if="field.type === 'text' || field.type === 'textarea'" class="field-validation">
                    <el-form-item label="验证规则" label-width="80px">
                      <el-input
                        v-model="field.validation"
                        placeholder="例如：^[\\u4e00-\\u9fa5]+$（只能输入中文）或 ^1[3-9]\\d{9}$（手机号格式）"
                      />
                      <div class="validation-tips">
                        <small>常用规则：手机号：^1[3-9]\d{9}$ | 邮箱：^\w+@\w+\.\w+$ | 身份证：^\d{17}[\dXx]$</small>
                      </div>
                    </el-form-item>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="formData.fields.length === 0" class="no-fields">
              <el-empty description="暂无字段定义" :image-size="60" />
              <p class="no-fields-tip">点击"添加字段"按钮开始定义调查表字段</p>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ submitButtonText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { createSurveyTemplate, updateSurveyTemplate } from '@/api/survey'

interface FieldDefinition {
  key: string
  label: string
  type: string
  required: boolean
  defaultValue?: any
  placeholder?: string
  validation?: string
  options?: Array<{ label: string; value: string }>
}

interface FormData {
  name: string
  description: string
  version: string
  fields: FieldDefinition[]
}

interface Props {
  modelValue: boolean
  title?: string
  templateToEdit?: any
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'created', template: any): void
  (e: 'updated', template: any): void
}

const props = withDefaults(defineProps<Props>(), {
  title: '创建企业调查表模板',
  modelValue: false,
  templateToEdit: null
})

const emit = defineEmits<Emits>()

// 计算属性
const isEditMode = computed(() => {
  return !!props.templateToEdit && props.templateToEdit.id
})

const dialogTitle = computed(() => {
  return isEditMode.value ? '修改企业调查表模板' : props.title
})

const submitButtonText = computed(() => {
  return isEditMode.value ? '更新模板' : '创建模板'
})

// 响应式数据
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formRef = ref<FormInstance>()
const submitting = ref(false)

const formData = reactive<FormData>({
  name: '',
  description: '',
  version: '1.0',
  fields: []
})

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述不能超过 500 个字符', trigger: 'blur' }
  ],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' },
    { pattern: /^\d+(\.\d+)*$/, message: '版本号格式不正确，如：1.0 或 1.0.1', trigger: 'blur' }
  ]
}

const fieldKeyRules = [
  { required: true, message: '请输入字段键名', trigger: 'blur' },
  { pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/, message: '只能包含字母、数字和下划线，且以字母开头', trigger: 'blur' }
]

const fieldLabelRules = [
  { required: true, message: '请输入字段标签', trigger: 'blur' }
]

// 方法
const handleAddField = () => {
  formData.fields.push({
    key: '',
    label: '',
    type: 'text',
    required: true,
    defaultValue: '',
    placeholder: '',
    options: []
  })
}

const handleRemoveField = (index: number) => {
  formData.fields.splice(index, 1)
}

const handleFieldTypeChange = (field: FieldDefinition) => {
  // 根据字段类型初始化选项
  if ((field.type === 'select' || field.type === 'checkbox') && !field.options) {
    field.options = []
  }
  
  // 设置默认值占位符
  if (field.type === 'number') {
    field.defaultValue = 0
  } else if (field.type === 'switch') {
    field.defaultValue = false
  } else if (field.type === 'checkbox') {
    field.defaultValue = []
  } else {
    field.defaultValue = ''
  }
}

const handleAddOption = (field: FieldDefinition) => {
  if (!field.options) {
    field.options = []
  }
  field.options.push({ label: '', value: '' })
}

const handleRemoveOption = (field: FieldDefinition, index: number) => {
  if (field.options) {
    field.options.splice(index, 1)
  }
}

const validateFieldKey = (field: FieldDefinition, index: number) => {
  // 检查键名是否重复
  const duplicateIndex = formData.fields.findIndex((f, i) => 
    i !== index && f.key === field.key && field.key.trim() !== ''
  )
  
  if (duplicateIndex !== -1) {
    ElMessage.warning(`字段键名 "${field.key}" 已存在，请使用不同的键名`)
    field.key = ''
  }
}

const getDefaultValuePlaceholder = (type: string) => {
  switch (type) {
    case 'text':
    case 'textarea':
      return '请输入默认文本'
    case 'number':
      return '请输入默认数字'
    case 'select':
      return '请选择默认选项值'
    case 'checkbox':
      return '请输入默认选项值（多个用逗号分隔）'
    case 'date':
      return 'YYYY-MM-DD'
    default:
      return '请输入默认值'
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    // 验证字段定义
    if (formData.fields.length === 0) {
      ElMessage.warning('请至少定义一个字段')
      return
    }
    
    // 验证字段键名和标签
    for (const field of formData.fields) {
      if (!field.key.trim()) {
        ElMessage.warning('请填写所有字段的键名')
        return
      }
      if (!field.label.trim()) {
        ElMessage.warning('请填写所有字段的标签')
        return
      }
    }
    
    // 构建字段定义JSON
    const fieldsDefinition: Record<string, any> = {}
    formData.fields.forEach(field => {
      fieldsDefinition[field.key] = {
        label: field.label,
        type: field.type,
        required: field.required,
        defaultValue: field.defaultValue,
        placeholder: field.placeholder || '',
        validation: field.validation || '',
        options: field.options || []
      }
    })
    
    // 提交数据
    submitting.value = true
    
    let response
    if (isEditMode.value && props.templateToEdit?.id) {
      // 更新现有模板
      response = await updateSurveyTemplate(props.templateToEdit.id, {
        name: formData.name,
        description: formData.description,
        version: formData.version,
        fields: fieldsDefinition,
        is_active: 1
      })
      ElMessage.success('模板更新成功')
      emit('updated', response)
    } else {
      // 创建新模板
      response = await createSurveyTemplate({
        name: formData.name,
        description: formData.description,
        version: formData.version,
        fields: fieldsDefinition,
        is_active: 1
      })
      ElMessage.success('模板创建成功')
      emit('created', response)
    }
    
    dialogVisible.value = false
    
  } catch (error: any) {
    if (error.response?.data?.detail) {
      ElMessage.error(`操作失败: ${error.response.data.detail}`)
    } else {
      ElMessage.error(`操作失败: ${error.message || '未知错误'}`)
    }
  } finally {
    submitting.value = false
  }
}

// 加载模板数据到表单
const loadTemplateData = (template: any) => {
  if (!template) return
  
  formData.name = template.name || ''
  formData.description = template.description || ''
  formData.version = template.version || '1.0'
  
  // 转换fields对象为数组
  formData.fields = []
  if (template.fields && typeof template.fields === 'object') {
    Object.entries(template.fields).forEach(([key, fieldDef]: [string, any]) => {
      formData.fields.push({
        key,
        label: fieldDef.label || '',
        type: fieldDef.type || 'text',
        required: fieldDef.required !== undefined ? fieldDef.required : true,
        defaultValue: fieldDef.defaultValue || '',
        placeholder: fieldDef.placeholder || '',
        validation: fieldDef.validation || '',
        options: fieldDef.options || []
      })
    })
  }
}

// 监听templateToEdit变化
watch(() => props.templateToEdit, (newTemplate) => {
  if (newTemplate && newTemplate.id) {
    loadTemplateData(newTemplate)
  }
}, { immediate: true })

const handleClose = () => {
  // 重置表单
  if (formRef.value) {
    formRef.value.resetFields()
  }
  formData.fields = []
  formData.name = ''
  formData.description = ''
  formData.version = '1.0'
}

// 暴露方法
defineExpose({
  resetForm: handleClose
})
</script>

<style scoped>
@import '@/assets/css/dialog.css';
</style>
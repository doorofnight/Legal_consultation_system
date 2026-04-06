import type { FormRules } from 'element-plus'

/**
 * 字段类型定义
 */
export interface FieldDefinition {
  label: string
  type: string
  required: boolean
  defaultValue?: any
  placeholder?: string
  validation?: string
  options?: Array<{ label: string; value: string }>
}

/**
 * 模板字段定义
 */
export interface TemplateFields {
  [key: string]: FieldDefinition
}

/**
 * 根据字段类型生成对应的表单组件
 */
export function generateFormItem(fieldKey: string, field: FieldDefinition, _formData: any, formRules: FormRules) {
  const { label, type, required, placeholder, options = [] } = field
  
  // 生成验证规则
  if (required) {
    formRules[fieldKey] = [
      { required: true, message: `请输入${label}`, trigger: type === 'select' ? 'change' : 'blur' }
    ]
  }
  
  // 根据字段类型生成不同的表单组件
  switch (type) {
    case 'text':
      return `
        <el-form-item label="${label}" prop="${fieldKey}">
          <el-input 
            v-model="surveyForm.${fieldKey}" 
            placeholder="${placeholder || `请输入${label}`}" 
          />
        </el-form-item>
      `
    
    case 'textarea':
      return `
        <el-form-item label="${label}" prop="${fieldKey}">
          <el-input
            v-model="surveyForm.${fieldKey}"
            type="textarea"
            :rows="3"
            placeholder="${placeholder || `请输入${label}`}"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      `
    
    case 'number':
      return `
        <el-form-item label="${label}" prop="${fieldKey}">
          <el-input-number 
            v-model="surveyForm.${fieldKey}" 
            :min="0" 
            :placeholder="${placeholder || `请输入${label}`}"
          />
        </el-form-item>
      `
    
    case 'select':
      const optionsHtml = options.map(opt => 
        `<el-option label="${opt.label}" value="${opt.value}" />`
      ).join('\n')
      
      return `
        <el-form-item label="${label}" prop="${fieldKey}">
          <el-select 
            v-model="surveyForm.${fieldKey}" 
            placeholder="${placeholder || `请选择${label}`}"
            style="width: 100%;"
          >
            ${optionsHtml}
          </el-select>
        </el-form-item>
      `
    
    case 'checkbox':
      const checkboxOptionsHtml = options.map(opt => 
        `<el-checkbox label="${opt.label}" value="${opt.value}" />`
      ).join('\n')
      
      return `
        <el-form-item label="${label}" prop="${fieldKey}">
          <el-checkbox-group v-model="surveyForm.${fieldKey}">
            ${checkboxOptionsHtml}
          </el-checkbox-group>
        </el-form-item>
      `
    
    case 'date':
      return `
        <el-form-item label="${label}" prop="${fieldKey}">
          <el-date-picker
            v-model="surveyForm.${fieldKey}"
            type="date"
            placeholder="${placeholder || `选择${label}`}"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
      `
    
    case 'switch':
      return `
        <el-form-item label="${label}" prop="${fieldKey}">
          <el-switch v-model="surveyForm.${fieldKey}" />
        </el-form-item>
      `
    
    default:
      return `
        <el-form-item label="${label}" prop="${fieldKey}">
          <el-input 
            v-model="surveyForm.${fieldKey}" 
            placeholder="${placeholder || `请输入${label}`}" 
          />
        </el-form-item>
      `
  }
}

/**
 * 初始化表单数据
 */
export function initializeFormData(fields: TemplateFields): Record<string, any> {
  const formData: Record<string, any> = {}
  
  Object.entries(fields).forEach(([key, field]) => {
    if (field.defaultValue !== undefined) {
      formData[key] = field.defaultValue
    } else {
      // 根据类型设置默认值
      switch (field.type) {
        case 'text':
        case 'textarea':
          formData[key] = ''
          break
        case 'number':
          formData[key] = 0
          break
        case 'select':
          formData[key] = ''
          break
        case 'checkbox':
          formData[key] = []
          break
        case 'date':
          formData[key] = ''
          break
        case 'switch':
          formData[key] = false
          break
        default:
          formData[key] = ''
      }
    }
  })
  
  return formData
}

/**
 * 生成表单验证规则
 */
export function generateFormRules(fields: TemplateFields): FormRules {
  const rules: FormRules = {}
  
  Object.entries(fields).forEach(([key, field]) => {
    if (field.required) {
      rules[key] = [
        { 
          required: true, 
          message: `请输入${field.label}`, 
          trigger: field.type === 'select' ? 'change' : 'blur' 
        }
      ]
      
      // 添加自定义验证规则
      if (field.validation) {
        try {
          const pattern = new RegExp(field.validation)
          rules[key].push({
            pattern,
            message: `${field.label}格式不正确`,
            trigger: 'blur'
          })
        } catch (e) {
          console.warn(`无效的正则表达式: ${field.validation}`, e)
        }
      }
    }
  })
  
  return rules
}

/**
 * 将模板字段转换为可渲染的表单HTML
 */
export function renderFormTemplate(fields: TemplateFields, formData: any, formRules: FormRules): string {
  let html = ''
  
  Object.entries(fields).forEach(([key, field]) => {
    html += generateFormItem(key, field, formData, formRules)
  })
  
  return html
}
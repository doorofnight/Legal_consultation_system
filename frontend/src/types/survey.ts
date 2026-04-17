// 调查表相关类型定义

// 调查表模板
export interface SurveyTemplate {
  id: number
  name: string
  description?: string
  fields: Record<string, any>
  version: string
  is_active: number
  created_at: string
  updated_at?: string
}

// 调查记录
export interface SurveyRecord {
  id: number
  template_id: number
  user_id?: string
  answers: Record<string, any>
  version: string
  status: string
  created_at: string
  updated_at?: string
  suggestions?: LegalSuggestion[]
}

// 法律建议
export interface LegalSuggestion {
  id: number
  record_id: number
  trigger_changes?: Record<string, any>
  suggestion: string
  analysis_type: string
  confidence_score: number
  created_at: string
}

// 请求和响应类型
export interface SurveySubmitRequest {
  template_id: number
  answers: Record<string, any>
  user_id?: string
}

export interface SurveySubmitResponse {
  record_id: number
  suggestion?: LegalSuggestion
  message: string
}

export interface SurveyHistoryResponse {
  records: SurveyRecord[]
  total: number
}

export interface SurveyAnalysisRequest {
  record_id: number
  previous_answers?: Record<string, any>
}

// 表单字段类型
export interface SurveyFormData {
  companyName: string
  companyType: string
  industry: string
  employeeCount: number
  registeredCapital: string
  establishmentDate: string
  businessScope: string
  legalNeeds: string[]
  annualRevenue: string
  hasOverseasBusiness: boolean
  remarks: string
}
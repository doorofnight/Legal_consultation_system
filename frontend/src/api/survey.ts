import axios from 'axios'
import type {
  SurveySubmitRequest,
  SurveySubmitResponse,
  SurveyHistoryResponse,
  LegalSuggestion,
  SurveyRecord,
  SurveyTemplate
} from '../types/survey'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000, // 增加超时时间到120秒（2分钟），因为AI分析可能需要较长时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 提交调查表
export async function submitSurvey(data: SurveySubmitRequest): Promise<SurveySubmitResponse> {
  const response = await api.post('/survey/submit', data)
  return response.data
}

// 获取调查记录历史
export async function getSurveyHistory(
  user_id?: string,
  limit: number = 100,
  offset: number = 0
): Promise<SurveyHistoryResponse> {
  const params: any = { limit, offset }
  if (user_id) {
    params.user_id = user_id
  }
  const response = await api.get('/survey/records', {
    params
  })
  return response.data
}

// 获取特定调查记录
export async function getSurveyRecord(
  record_id: number,
  user_id?: string
): Promise<SurveyRecord> {
  const response = await api.get(`/survey/records/${record_id}`, {
    params: { user_id }
  })
  return response.data
}

// 获取调查记录的法律建议
export async function getSurveySuggestions(record_id: number): Promise<LegalSuggestion[]> {
  const response = await api.get(`/survey/suggestions/${record_id}`)
  return response.data
}

// 获取最新的法律建议
export async function getLatestSuggestion(user_id: string): Promise<LegalSuggestion | null> {
  const response = await api.get(`/survey/latest-suggestion/${user_id}`)
  return response.data
}

// 保存草稿（临时实现）
export async function saveDraftRecord(data: any): Promise<any> {
  // 临时实现：直接调用submit接口，但状态设为draft
  const draftData = {
    ...data,
    status: 'draft'
  }
  const response = await api.post('/survey/submit', draftData)
  return response.data
}

// 删除调查记录
export async function deleteSurveyRecord(record_id: number, user_id?: string): Promise<void> {
  await api.delete(`/survey/records/${record_id}`, {
    params: { user_id }
  })
}

// 获取调查表模板
export async function getSurveyTemplates(active_only: boolean = true): Promise<SurveyTemplate[]> {
  const response = await api.get('/survey/templates', {
    params: { active_only }
  })
  return response.data
}

// 创建调查表模板
export async function createSurveyTemplate(templateData: any): Promise<SurveyTemplate> {
  const response = await api.post('/survey/templates', templateData)
  return response.data
}

// 获取特定模板
export async function getSurveyTemplate(template_id: number): Promise<SurveyTemplate> {
  const response = await api.get(`/survey/templates/${template_id}`)
  return response.data
}

// 更新模板
export async function updateSurveyTemplate(template_id: number, templateData: any): Promise<SurveyTemplate> {
  const response = await api.put(`/survey/templates/${template_id}`, templateData)
  return response.data
}

// 删除模板
export async function deleteSurveyTemplate(template_id: number): Promise<void> {
  await api.delete(`/survey/templates/${template_id}`)
}
import axios from 'axios'
import type {
  ContractUpload,
  ContractUploadRequest,
  ContractUploadResponse,
  ContractDiagnosis,
  ContractDiagnosisRequest,
  ContractDiagnosisResponse,
  ContractHistoryResponse,
  ContractDiagnosisStatus
} from '../types/contract'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 300000, // 增加超时时间到5分钟，因为合同分析可能需要较长时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 上传合同文件
export async function uploadContract(request: ContractUploadRequest): Promise<ContractUploadResponse> {
  const formData = new FormData()
  formData.append('file', request.file)
  
  const response = await api.post('/contract/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

// 诊断合同
export async function diagnoseContract(
  data: ContractDiagnosisRequest
): Promise<ContractDiagnosisResponse> {
  const response = await api.post('/contract/diagnose', data)
  return response.data
}

// 获取合同诊断状态
export async function getDiagnosisStatus(
  upload_id: number
): Promise<ContractDiagnosisStatus> {
  const response = await api.get(`/contract/status/${upload_id}`)
  return response.data
}

// 获取合同上传历史
export async function getContractHistory(
  limit: number = 100,
  offset: number = 0
): Promise<ContractHistoryResponse> {
  const response = await api.get('/contract/history', {
    params: { limit, offset }
  })
  return response.data
}

// 获取特定合同诊断结果
export async function getContractDiagnosis(
  diagnosis_id: number
): Promise<ContractDiagnosis> {
  const response = await api.get(`/contract/diagnosis/${diagnosis_id}`)
  return response.data
}

// 获取特定合同上传记录
export async function getContractUpload(
  upload_id: number
): Promise<ContractUpload> {
  const response = await api.get(`/contract/upload/${upload_id}`)
  return response.data
}

// 删除合同上传记录
export async function deleteContractUpload(
  upload_id: number
): Promise<void> {
  await api.delete(`/contract/upload/${upload_id}`)
}

// 导出诊断报告
export async function exportDiagnosisReport(
  diagnosis_id: number,
  format: 'pdf' | 'docx' | 'txt' = 'pdf'
): Promise<Blob> {
  const response = await api.get(`/contract/export/${diagnosis_id}`, {
    params: { format },
    responseType: 'blob'
  })
  return response.data
}

// 获取支持的合同类型
export async function getSupportedContractTypes(): Promise<string[]> {
  const response = await api.get('/contract/types')
  return response.data
}

// 获取风险类型分类
export async function getRiskCategories(): Promise<{
  categories: string[]
  risk_levels: Array<'high' | 'medium' | 'low'>
}> {
  const response = await api.get('/contract/risk-categories')
  return response.data
}
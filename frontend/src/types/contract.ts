// 合同诊断相关类型定义

// 合同上传记录
export interface ContractUpload {
  id: number
  filename: string
  file_path: string
  file_type: string
  file_size: number
  status?: string
  contract_type?: string
  user_id?: number
  created_at: string
  updated_at: string
}

// 包含诊断记录的上传记录
export interface ContractUploadWithDiagnosis extends ContractUpload {
  diagnoses: ContractDiagnosis[]
}

// 合同风险项
export interface ContractRisk {
  id?: number  // 改为可选，因为后端可能不返回id
  clause: string  // 风险条款内容
  risk_level: '高风险' | '中风险' | '低风险'  // 风险等级
  risk_type: string  // 风险类型
  description: string  // 风险描述
  suggestion: string  // 修改建议
  line_number?: number  // 在合同中的行号
  paragraph_index?: number  // 段落索引
}

// 合同诊断结果
export interface ContractDiagnosis {
  id: number
  upload_id: number
  contract_type: string  // 合同类型
  summary: string  // 总体评价
  risks: ContractRisk[]  // 风险列表
  suggestions: string  // 综合建议
  created_at: string
  updated_at: string
  analysis_time?: number  // 分析耗时（秒）
  model_used?: string    // 使用的模型
}

// 合同上传请求
export interface ContractUploadRequest {
  file: File
}

// 合同上传响应
export interface ContractUploadResponse {
  upload: ContractUpload
  pre_analysis?: {
    contract_type: string
    total_pages: number
    total_paragraphs: number
    potential_risks_count: number
  }
}

// 合同诊断请求
export interface ContractDiagnosisRequest {
  upload_id: number
  contract_type?: string  // 合同类型（技术合同、服务合同等）
  perspective?: string  // 审查立场（甲方/乙方等）
  focus_areas?: string[]  // 重点关注领域
  model_provider?: 'siliconflow' | 'ollama'  // 模型提供商
}

// 合同诊断响应
export interface ContractDiagnosisResponse {
  diagnosis: ContractDiagnosis
  analysis_time: number
  model_used: string
}

// 合同历史记录
export interface ContractHistoryResponse {
  uploads: ContractUploadWithDiagnosis[]
  total: number
}

// 合同诊断状态
export interface ContractDiagnosisStatus {
  upload_id: number
  status: 'uploading' | 'parsing' | 'analyzing' | 'completed' | 'failed'
  progress: number
  message: string
}
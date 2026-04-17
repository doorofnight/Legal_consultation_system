import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 目录项类型
export interface DirectoryItem {
  type: 'directory' | 'file'
  name: string
  path: string
  size?: string
  modified?: string
  extension?: string
  children?: DirectoryItem[]
}

// 知识库文档类型
export interface KnowledgeDocument {
  id: string
  filename: string
  path: string
  rel_path: string
  category: string
  extension: string
  size: string
  size_bytes?: number
  modified: string
  content?: string
}

export interface DocumentContent {
  id: string
  filename: string
  path: string
  category: string
  extension: string
  content: string
}

// 知识库API
export const knowledgeApi = {
  // 获取目录结构
  getDirectory: async (): Promise<DirectoryItem[]> => {
    const response = await api.get('/knowledge/directory')
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '获取目录结构失败')
    }
  },

  // 获取文档列表
  getDocuments: async (category?: string): Promise<KnowledgeDocument[]> => {
    const response = await api.get('/knowledge/documents', {
      params: { category }
    })
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '获取文档列表失败')
    }
  },

  // 获取文档内容
  getDocumentContent: async (id: string): Promise<DocumentContent> => {
    const response = await api.get(`/knowledge/document/${id}/content`)
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '获取文档内容失败')
    }
  },

  // 扫描文档（重新扫描知识库）
  scanDocuments: async (): Promise<{ count: number, documents: any[] }> => {
    const response = await api.post('/knowledge/scan')
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '扫描文档失败')
    }
  },

  // 获取知识库统计
  getStats: async (): Promise<any> => {
    const response = await api.get('/knowledge/stats')
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '获取统计信息失败')
    }
  },

  // 搜索知识库
  search: async (query: string, n_results: number = 5): Promise<any> => {
    const response = await api.post('/knowledge/search', null, {
      params: { query, n_results }
    })
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '搜索失败')
    }
  },

  // 上传文档（单个）
  uploadDocument: async (file: File, category: string): Promise<any> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('category', category)
    
    const response = await api.post('/knowledge/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '上传文档失败')
    }
  },

  // 批量上传文档
  uploadMultipleDocuments: async (files: File[], category: string): Promise<any> => {
    const formData = new FormData()
    
    // 添加所有文件
    files.forEach((file, index) => {
      formData.append('files', file)
    })
    
    // 添加分类
    formData.append('category', category)
    
    const response = await api.post('/knowledge/upload-multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '批量上传文档失败')
    }
  },

  // 创建目录
  createDirectory: async (folderName: string): Promise<any> => {
    const response = await api.post('/knowledge/directory', null, {
      params: {
        folder_name: folderName
      }
    })
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '创建目录失败')
    }
  },

  // 创建属性映射
  createPropertyMapping: async (chineseName: string, englishName: string): Promise<any> => {
    const response = await api.post('/knowledge/properties', {
      chinese_name: chineseName,
      english_name: englishName
    })
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '创建属性映射失败')
    }
  },

  // 删除文档
  deleteDocument: async (filePath: string): Promise<any> => {
    const response = await api.delete(`/knowledge/document/${encodeURIComponent(filePath)}`)
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '删除文档失败')
    }
  },

  // 删除目录
  deleteDirectory: async (dirPath: string): Promise<any> => {
    const response = await api.delete(`/knowledge/directory/${encodeURIComponent(dirPath)}`)
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '删除目录失败')
    }
  },

  // 获取属性映射列表
  getPropertyMappings: async (): Promise<any[]> => {
    const response = await api.get('/knowledge/properties')
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.detail || '获取属性映射失败')
    }
  }
}
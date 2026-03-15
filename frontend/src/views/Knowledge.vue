<template>
  <div class="knowledge-container">
    <!-- 页面头部 -->
    <el-card class="knowledge-header-card">
      <div class="knowledge-header">
        <div class="header-left">
          <el-icon size="28" color="#409eff"><Reading /></el-icon>
          <h2>法律知识库管理</h2>
        </div>
        <div class="header-right">
          <el-button type="primary" size="small" @click="refreshDocuments">
            <el-icon><Refresh /></el-icon>
            刷新文档
          </el-button>
        </div>
      </div>
      <div class="knowledge-subtitle">
        <p>管理并查询法律知识库中的文档，支持txt、word等格式文档的查看。</p>
      </div>
    </el-card>

    <!-- 文档列表 -->
    <el-card class="documents-card">
      <template #header>
        <div class="documents-header">
          <el-icon><Files /></el-icon>
          <h3>知识库文档列表</h3>
          <el-tag type="info" size="small">{{ documents.length }} 个文档</el-tag>
        </div>
      </template>
      
      <!-- 搜索框 -->
      <div class="search-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文档名称或内容..."
          clearable
          @input="filterDocuments"
          @clear="filterDocuments"
          style="width: 300px; margin-right: 16px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="selectedCategory" placeholder="选择分类" clearable @change="filterDocuments">
          <el-option label="全部" value="" />
          <el-option label="劳动合同模板" value="contract_templates" />
          <el-option label="法律文档" value="legal_documents" />
          <el-option label="案例分析" value="case_analysis" />
          <el-option label="法律指南" value="legal_guidelines" />
        </el-select>
      </div>

      <!-- 文档表格 -->
      <el-table :data="filteredDocuments" style="width: 100%; margin-top: 20px;" v-loading="loading">
        <el-table-column prop="name" label="文档名称" width="300">
          <template #default="{ row }">
            <div class="document-name">
              <el-icon v-if="row.type === 'md'"><Document /></el-icon>
              <el-icon v-if="row.type === 'txt'"><Document /></el-icon>
              <el-icon v-if="row.type === 'doc' || row.type === 'docx'"><Document /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="150">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">
              {{ getCategoryName(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路径" />
        <el-table-column prop="size" label="大小" width="100" />
        <el-table-column prop="modified" label="修改时间" width="180" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDocument(row)">
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <div v-if="filteredDocuments.length === 0 && !loading" class="empty-state">
        <el-empty description="未找到相关文档">
          <el-button type="primary" @click="refreshDocuments">刷新文档列表</el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 文档查看对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      :title="currentDocument?.name"
      width="80%"
      top="5vh"
    >
      <div class="document-viewer">
        <div v-if="currentDocumentContent" class="document-content">
          <div class="document-meta">
            <el-tag type="info">分类: {{ getCategoryName(currentDocument?.category || '') }}</el-tag>
            <el-tag type="info">路径: {{ currentDocument?.path }}</el-tag>
            <el-tag type="info">大小: {{ currentDocument?.size }}</el-tag>
          </div>
          <div class="content-area">
            <pre v-if="currentDocument?.type === 'txt' || currentDocument?.type === 'md'">{{ currentDocumentContent }}</pre>
            <div v-else class="unsupported-format">
              <el-icon size="64" color="#909399"><Warning /></el-icon>
              <h3>暂不支持在线预览此格式</h3>
              <p>文档格式为 {{ currentDocument?.type.toUpperCase() }}，请下载后查看</p>
            </div>
          </div>
        </div>
        <div v-else class="loading-content">
          <el-skeleton :rows="10" animated />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="viewDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="downloadDocument(currentDocument)" v-if="currentDocument">
            下载
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { 
  Reading, 
  Refresh, 
  Files, 
  Search, 
  Document, 
  Warning 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 文档类型定义
interface KnowledgeDocument {
  id: number
  name: string
  category: string
  path: string
  size: string
  modified: string
  type: string
  content?: string
}

// 响应式数据
const documents = ref<KnowledgeDocument[]>([])
const filteredDocuments = ref<KnowledgeDocument[]>([])
const searchQuery = ref('')
const selectedCategory = ref('')
const loading = ref(false)
const viewDialogVisible = ref(false)
const currentDocument = ref<KnowledgeDocument | null>(null)
const currentDocumentContent = ref('')

// 模拟文档数据（实际应该从后端API获取）
const mockDocuments: KnowledgeDocument[] = [
  {
    id: 1,
    name: '劳动合同模板.md',
    category: 'contract_templates',
    path: 'knowledge_base/contract_templates/labor_contract/劳动合同模板.md',
    size: '2.5 KB',
    modified: '2026-01-15 10:30:25',
    type: 'md'
  },
  {
    id: 2,
    name: '劳动合同法试用期规定.md',
    category: 'legal_documents',
    path: 'knowledge_base/legal_documents/labor_law/劳动合同法试用期规定.md',
    size: '3.2 KB',
    modified: '2026-01-10 14:20:15',
    type: 'md'
  },
  {
    id: 3,
    name: '试用期违法解除案例.md',
    category: 'case_analysis',
    path: 'knowledge_base/case_analysis/labor_disputes/试用期违法解除案例.md',
    size: '4.1 KB',
    modified: '2026-01-05 09:15:30',
    type: 'md'
  },
  {
    id: 4,
    name: '劳动法合规指南.docx',
    category: 'legal_guidelines',
    path: 'knowledge_base/legal_guidelines/compliance_guide/劳动法合规指南.docx',
    size: '15.7 KB',
    modified: '2026-01-20 16:45:10',
    type: 'docx'
  },
  {
    id: 5,
    name: '公司股权协议模板.doc',
    category: 'contract_templates',
    path: 'knowledge_base/contract_templates/company_equity/公司股权协议模板.doc',
    size: '28.3 KB',
    modified: '2026-01-18 11:25:40',
    type: 'doc'
  },
  {
    id: 6,
    name: '民法典合同编要点.txt',
    category: 'legal_documents',
    path: 'knowledge_base/legal_documents/civil_code/民法典合同编要点.txt',
    size: '5.6 KB',
    modified: '2026-01-12 13:40:55',
    type: 'txt'
  }
]

// 获取分类名称
const getCategoryName = (category: string): string => {
  const categoryMap: Record<string, string> = {
    'contract_templates': '劳动合同模板',
    'legal_documents': '法律文档',
    'case_analysis': '案例分析',
    'legal_guidelines': '法律指南'
  }
  return categoryMap[category] || category
}

// 获取分类标签类型
const getCategoryTagType = (category: string): string => {
  const typeMap: Record<string, string> = {
    'contract_templates': 'success',
    'legal_documents': 'primary',
    'case_analysis': 'warning',
    'legal_guidelines': 'info'
  }
  return typeMap[category] || 'info'
}

// 加载文档
const loadDocuments = () => {
  loading.value = true
  // 模拟API调用延迟
  setTimeout(() => {
    documents.value = mockDocuments
    filteredDocuments.value = [...mockDocuments]
    loading.value = false
    ElMessage.success(`已加载 ${mockDocuments.length} 个文档`)
  }, 800)
}

// 刷新文档
const refreshDocuments = () => {
  loadDocuments()
}

// 过滤文档
const filterDocuments = () => {
  if (!searchQuery.value && !selectedCategory.value) {
    filteredDocuments.value = [...documents.value]
    return
  }

  filteredDocuments.value = documents.value.filter(doc => {
    const matchesSearch = !searchQuery.value || 
      doc.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      doc.path.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesCategory = !selectedCategory.value || 
      doc.category === selectedCategory.value
    
    return matchesSearch && matchesCategory
  })
}

// 查看文档
const viewDocument = (doc: KnowledgeDocument) => {
  currentDocument.value = doc
  viewDialogVisible.value = true
  
  // 模拟加载文档内容
  if (doc.type === 'md' || doc.type === 'txt') {
    currentDocumentContent.value = `# ${doc.name}\n\n这是 ${doc.name} 的示例内容。\n\n实际应用中，这里应该显示从后端API获取的文档实际内容。\n\n文档路径：${doc.path}\n\n分类：${getCategoryName(doc.category)}\n\n大小：${doc.size}\n\n修改时间：${doc.modified}`
  } else {
    currentDocumentContent.value = ''
  }
}

// 下载文档
const downloadDocument = (doc: KnowledgeDocument | null) => {
  if (!doc) return
  
  ElMessage.info(`开始下载: ${doc.name}`)
  // 实际应用中这里应该调用后端API下载文件
  // 这里只是模拟
  const link = document.createElement('a')
  link.href = '#'
  link.download = doc.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 初始化
onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.knowledge-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  gap: 20px;
}

.knowledge-header-card {
  width: 100%;
  margin-bottom: 0;
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.knowledge-subtitle p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.documents-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.documents-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.search-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.document-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.empty-state {
  padding: 40px 0;
}

.document-viewer {
  min-height: 400px;
}

.document-meta {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.content-area {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 20px;
  background-color: #fafafa;
  max-height: 500px;
  overflow-y: auto;
}

.content-area pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.unsupported-format {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.unsupported-format h3 {
  margin: 16px 0 8px;
  font-size: 18px;
}

.loading-content {
  padding: 20px;
}
</style>
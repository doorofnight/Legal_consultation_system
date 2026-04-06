<template>
  <div class="knowledge-container">
    <!-- 页面头部 -->
    <el-card class="knowledge-header-card">
      <div class="knowledge-header">
        <div class="header-left">
          <el-icon><Reading /></el-icon>
          <h2>法律知识库管理</h2>
        </div>
      </div>
      <div class="knowledge-subtitle">
        <p>管理法律知识库目录结构，支持目录和文档的添加、删除、查看。</p>
      </div>
    </el-card>

    <!-- 目录结构 -->
    <el-card class="directory-card">
      <template #header>
        <div class="directory-header">
          <div class="header-left">
            <h2>知识库目录</h2>
            <el-tag type="info" size="small">{{ totalFiles }} 个文档</el-tag>
          </div>
          <div class="header-middle">
            <el-input
              v-model="searchQuery"
              placeholder="搜索文档..."
              clearable
              style="width: 300px;"
              @input="filterDirectory"
              @clear="filterDirectory"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          <div class="header-right">
            <el-button type="info" size="medium" @click="toggleAllDirectories">
              <el-icon>
                <ArrowDown v-if="!allDirectoriesCollapsed" />
                <ArrowRight v-else />
              </el-icon>
              {{ allDirectoriesCollapsed ? '展开所有目录' : '收起所有目录' }}
            </el-button>
            <el-button type="primary" size="medium" @click="refreshDirectory">
              <el-icon><Refresh /></el-icon>
              刷新目录
            </el-button>
            <el-button type="success" size="medium" @click="showAddDirectoryDialog = true">
              <el-icon><Plus /></el-icon>
              添加文件夹
            </el-button>
          </div>
        </div>
      </template>

      <!-- 折叠面板显示目录 -->
      <div class="directory-collapse" v-loading="loading">
        <el-collapse v-model="activeNames">
          <template v-for="item in filteredDirectory" :key="item.path">
            <el-collapse-item
              v-if="item.type === 'directory'"
              :name="item.path"
            >
              <template #title>
                <div class="collapse-title">
                  <div class="title-left">
                    <el-icon><Files /></el-icon>
                    <span class="directory-name">{{ getDisplayName(item) }}</span>
                    <el-tag size="small" type="info">{{ item.children?.length || 0 }} 个文件</el-tag>
                  </div>
                  <div class="title-right">
                    <el-button
                      type="primary"
                      size="medium"
                      @click.stop="uploadToDirectory(item)"
                    >
                      <el-icon><Upload /></el-icon>
                      上传文档
                    </el-button>
                    <el-button
                      type="danger"
                      size="medium"
                      @click.stop="deleteDirectory(item)"
                    >
                      删除目录
                    </el-button>
                  </div>
                </div>
              </template>
              
              <!-- 文件列表 -->
              <div class="file-list" v-if="item.children && item.children.length > 0">
                <el-table :data="item.children" style="width: 100%">
                <el-table-column prop="name" label="文件名" width="300">
                  <template #default="{ row }">
                    <div class="file-name">
                      <el-icon><Document /></el-icon>
                      <span>{{ row.name }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="size" label="大小" width="100" />
                <el-table-column prop="modified" label="修改时间" width="180" />
                <el-table-column prop="extension" label="格式" width="100">
                  <template #default="{ row }">
                    <el-tag size="small" :type="row.extension === '.txt' ? 'success' : 'info'">
                      {{ row.extension }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="250">
                  <template #default="{ row }">
                    <el-button
                      type="primary"
                      size="medium"
                      @click="viewDocument(row)"
                    >
                      查看
                    </el-button>
                    <el-button
                      type="success"
                      size="medium"
                      @click="downloadDocument(row)"
                    >
                      下载
                    </el-button>
                    <el-button
                      type="danger"
                      size="medium"
                      @click="deleteFile(row)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            </el-collapse-item>
          </template>
        </el-collapse>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredDirectory.length === 0 && !loading" class="empty-state">
        <el-empty description="知识库为空">
          <el-button type="primary" size="medium" @click="showAddDirectoryDialog = true">添加文件夹</el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 添加文件夹对话框 -->
    <KnowledgeDirectoryCreateDialog
      v-model="showAddDirectoryDialog"
      @confirm="handleCreateDirectory"
    />

    <!-- 上传文档对话框 -->
    <KnowledgeUploadDialog
      v-model="showUploadDialog"
      :directory-name="uploadDirectoryName"
      @confirm="handleUploadDocument"
    />

    <!-- 文档查看对话框 -->
    <KnowledgeDocumentViewDialog
      v-model="viewDialogVisible"
      :document="currentDocument"
      :document-content="currentDocumentContent"
      @download="downloadDocument"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { knowledgeApi, type DirectoryItem } from '@/api/knowledge'
// 导入弹窗组件
import KnowledgeDirectoryCreateDialog from '@/components/KnowledgeDirectoryCreateDialog.vue'
import KnowledgeUploadDialog from '@/components/KnowledgeUploadDialog.vue'
import KnowledgeDocumentViewDialog from '@/components/KnowledgeDocumentViewDialog.vue'
// 从图标集中管理文件导入图标
import {
  Reading,
  Refresh,
  Files,
  Search,
  Document,
  Upload,
} from '@/icons'
import { ArrowDown, ArrowRight } from '@element-plus/icons-vue'
// 导入共享CSS
import '@/assets/css/variables.css'
import '@/assets/css/utilities.css'
import '@/assets/css/knowledge.css'
import '@/assets/css/dialog.css'

// 响应式数据
const directory = ref<DirectoryItem[]>([])
const filteredDirectory = ref<DirectoryItem[]>([])
const loading = ref(false)
const searchQuery = ref('')
const activeNames = ref<string[]>([]) // 展开的面板
const allDirectoriesCollapsed = ref(true) // 默认所有目录收起

// 对话框状态
const showAddDirectoryDialog = ref(false)
const showUploadDialog = ref(false)
const viewDialogVisible = ref(false)
const creatingDirectory = ref(false)
const uploading = ref(false)

// 当前上传的目录
const uploadDirectory = ref<DirectoryItem | null>(null)
const uploadDirectoryName = computed(() => {
  return uploadDirectory.value ? getDisplayName(uploadDirectory.value) : ''
})

// 当前文档
const currentDocument = ref<DirectoryItem | null>(null)
const currentDocumentContent = ref('')


// 计算总文件数
const totalFiles = computed(() => {
  let count = 0
  const countFiles = (items: DirectoryItem[]) => {
    for (const item of items) {
      if (item.type === 'file') {
        count++
      }
      if (item.children) {
        countFiles(item.children)
      }
    }
  }
  countFiles(directory.value)
  return count
})

// 获取显示名称（直接返回文件夹名或文件名）
const getDisplayName = (item: DirectoryItem): string => {
  return item.name
}

// 加载目录结构
const loadDirectory = async () => {
  loading.value = true
  try {
    const data = await knowledgeApi.getDirectory()
    directory.value = data
    filteredDirectory.value = data
    // 默认收起所有目录（根据用户要求）
    activeNames.value = []
    // 更新下拉按钮状态
    allDirectoriesCollapsed.value = true
  } catch (error: any) {
    ElMessage.error(`加载目录失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 刷新目录
const refreshDirectory = () => {
  loadDirectory()
}

// 切换所有目录的展开/收起状态
const toggleAllDirectories = () => {
  allDirectoriesCollapsed.value = !allDirectoriesCollapsed.value
  if (allDirectoriesCollapsed.value) {
    // 收起所有目录
    activeNames.value = []
  } else {
    // 展开所有目录
    activeNames.value = directory.value
      .filter(item => item.type === 'directory')
      .map(item => item.path)
  }
}

// 过滤目录
const filterDirectory = () => {
  if (!searchQuery.value) {
    filteredDirectory.value = directory.value
    return
  }
  
  const query = searchQuery.value.toLowerCase()
  filteredDirectory.value = directory.value.filter(dir => {
    if (dir.type === 'directory') {
      // 检查目录名是否匹配
      if (getDisplayName(dir).toLowerCase().includes(query)) {
        return true
      }
      
      // 检查目录下的文件是否匹配
      if (dir.children) {
        const filteredChildren = dir.children.filter(file => 
          file.name.toLowerCase().includes(query)
        )
        return filteredChildren.length > 0
      }
    }
    return false
  })
}

// 查看文档
const viewDocument = async (doc: DirectoryItem) => {
  if (doc.type !== 'file') {
    ElMessage.warning('只能查看文件')
    return
  }
  
  currentDocument.value = doc
  viewDialogVisible.value = true
  currentDocumentContent.value = ''
  
  try {
    // 获取所有文档列表
    const documents = await knowledgeApi.getDocuments()
    
    // 根据路径查找匹配的文档
    const matchedDoc = documents.find(d => d.rel_path === doc.path || d.path.includes(doc.path))
    
    if (matchedDoc) {
      // 获取文档内容
      const contentData = await knowledgeApi.getDocumentContent(matchedDoc.id)
      currentDocumentContent.value = contentData.content
    } else {
      // 如果找不到匹配的文档，尝试直接读取文件
      // 或者显示错误信息
      currentDocumentContent.value = `无法找到文档: ${doc.path}\n\n请确保文档已扫描到知识库中。`
    }
  } catch (error: any) {
    currentDocumentContent.value = `获取文档内容失败: ${error.message}`
  }
}

// 下载文档
const downloadDocument = async (doc: DirectoryItem | null) => {
  if (!doc || doc.type !== 'file') {
    ElMessage.warning('只能下载文件')
    return
  }
  
  try {
    // 将路径中的反斜杠转换为正斜杠，确保URL兼容性
    const normalizedPath = doc.path.replace(/\\/g, '/')
    // 创建下载链接
    const response = await fetch(`/api/v1/knowledge/document/${encodeURIComponent(normalizedPath)}/download`)
    if (!response.ok) throw new Error('下载失败')
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = doc.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`开始下载: ${doc.name}`)
  } catch (error: any) {
    ElMessage.error(`下载失败: ${error.message}`)
  }
}

// 创建目录
const handleCreateDirectory = async (folderName: string) => {
  if (!folderName) {
    ElMessage.error('请填写文件夹名')
    return
  }
  
  creatingDirectory.value = true
  try {
    // 调用后端API创建目录
    const result = await knowledgeApi.createDirectory(folderName)
    
    // 添加新目录到列表
    const newDir: DirectoryItem = {
      type: 'directory',
      name: result.english_name,
      path: result.path,
      children: []
    }
    
    directory.value.push(newDir)
    filteredDirectory.value = [...directory.value]
    activeNames.value.push(newDir.path)
    
    ElMessage.success(`文件夹 "${folderName}" 创建成功`)
    showAddDirectoryDialog.value = false
    
    // 刷新目录以获取最新状态
    await loadDirectory()
  } catch (error: any) {
    ElMessage.error(`创建文件夹失败: ${error.message}`)
  } finally {
    creatingDirectory.value = false
  }
}

// 上传到指定目录
const uploadToDirectory = (dir: DirectoryItem) => {
  uploadDirectory.value = dir
  showUploadDialog.value = true
}

// 删除目录
const deleteDirectory = async (dir: DirectoryItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除目录 "${getDisplayName(dir)}" 吗？此操作将删除目录下的所有文件。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用真正的API删除目录
    await knowledgeApi.deleteDirectory(dir.path)
    
    ElMessage.success('目录删除成功')
    
    // 刷新目录以更新目录列表
    await loadDirectory()
  } catch (error: any) {
    // 用户取消删除或删除失败
    if (error.message && !error.message.includes('取消')) {
      ElMessage.error(`删除失败: ${error.message}`)
    }
  }
}

// 删除文件
const deleteFile = async (file: DirectoryItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${file.name}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用真正的API删除文件
    await knowledgeApi.deleteDocument(file.path)
    
    ElMessage.success('文件删除成功')
    
    // 刷新目录以更新文件列表
    await loadDirectory()
  } catch (error: any) {
    // 用户取消删除或删除失败
    if (error.message && !error.message.includes('取消')) {
      ElMessage.error(`删除失败: ${error.message}`)
    }
  }
}


const handleUploadDocument = async (files: File[]) => {
  if (!files || files.length === 0) {
    ElMessage.error('请选择要上传的文件')
    return
  }
  
  uploading.value = true
  try {
    // 获取目录名作为分类
    const category = uploadDirectory.value ? uploadDirectory.value.path : ''
    
    // 调用批量上传API
    const result = await knowledgeApi.uploadMultipleDocuments(files, category)
    
    ElMessage.success(`批量上传完成，成功 ${result.success} 个，失败 ${result.failed} 个`)
    showUploadDialog.value = false
    uploadDirectory.value = null
    
    // 刷新目录以显示新上传的文件
    await loadDirectory()
  } catch (error: any) {
    ElMessage.error(`上传失败: ${error.message}`)
  } finally {
    uploading.value = false
  }
}

// 初始化
onMounted(() => {
  loadDirectory()
})
</script>

/* 选定企业调查表弹窗 - 从survey.vue中提取 */

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="template-select-dialog">
      <!-- 搜索和筛选 -->
      <div class="dialog-header">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索模板名称"
          clearable
          style="width: 300px; margin-right: 10px;"
          @input="handleSearch"
        />
        <el-button type="primary" @click="handleCreateNew">
          <el-icon><Plus /></el-icon>
          创建新模板
        </el-button>
      </div>

      <!-- 模板列表 -->
      <div class="template-list">
        <el-table
          :data="filteredTemplates"
          style="width: 100%"
          @row-click="handleSelectTemplate"
          highlight-current-row
        >
          <el-table-column prop="name" label="模板名称" width="180">
            <template #default="{ row }">
              <div class="template-name">
                <el-icon><Document /></el-icon>
                <span>{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="version" label="版本" width="80" align="center">
            <template #default="{ row }">
              <el-tag size="small">{{ row.version }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="fields" label="字段数量" width="100" align="center">
            <template #default="{ row }">
              <span>{{ getFieldCount(row) }} 个</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="140">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" align="center">
            <template #default="{ row, $index }">
              <div class="action-buttons">
                <el-button
                  type="primary"
                  size="small"
                  @click.stop="handleSelectTemplate(row)"
                >
                  选择
                </el-button>
                <el-button
                  type="warning"
                  size="small"
                  @click.stop="handleEditTemplate(row)"
                >
                  修改
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  @click.stop="handleDeleteTemplate(row, $index)"
                  :loading="deletingTemplateId === row.id"
                >
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredTemplates.length === 0" class="empty-state">
        <el-empty description="暂无调查表模板" :image-size="80" />
        <div class="empty-actions">
          <el-button type="primary" @click="handleCreateNew">
            创建第一个模板
          </el-button>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!selectedTemplate"
          @click="handleConfirm"
        >
          确定选择
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSurveyTemplates, deleteSurveyTemplate } from '@/api/survey'
import type { SurveyTemplate } from '@/types/survey'

interface Props {
  modelValue: boolean
  title?: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'select', template: SurveyTemplate): void
  (e: 'edit', template: SurveyTemplate): void
  (e: 'create-new'): void
}

const props = withDefaults(defineProps<Props>(), {
  title: '选择企业调查表模板',
  modelValue: false
})

const emit = defineEmits<Emits>()

// 响应式数据
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const templates = ref<SurveyTemplate[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const selectedTemplate = ref<SurveyTemplate | null>(null)
const deletingTemplateId = ref<number | null>(null)

// 计算属性
const filteredTemplates = computed(() => {
  if (!searchKeyword.value.trim()) {
    return templates.value
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  return templates.value.filter(template =>
    template.name.toLowerCase().includes(keyword)
  )
})

// 方法
const loadTemplates = async () => {
  try {
    loading.value = true
    const data = await getSurveyTemplates(true)
    templates.value = data
  } catch (error: any) {
    ElMessage.error(`加载模板失败: ${error.message || '未知错误'}`)
    templates.value = []
  } finally {
    loading.value = false
  }
}

const getFieldCount = (template: SurveyTemplate) => {
  if (!template.fields) return 0
  return Object.keys(template.fields).length
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const handleSearch = () => {
  // 搜索逻辑已通过计算属性实现
}

const handleSelectTemplate = (template: SurveyTemplate) => {
  selectedTemplate.value = template
}

const handleEditTemplate = (template: SurveyTemplate) => {
  emit('edit', template)
  dialogVisible.value = false
}

const handleConfirm = () => {
  if (selectedTemplate.value) {
    emit('select', selectedTemplate.value)
    dialogVisible.value = false
  }
}

const handleDeleteTemplate = async (template: SurveyTemplate, index: number) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板 "${template.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    deletingTemplateId.value = template.id
    await deleteSurveyTemplate(template.id)
    
    // 从列表中移除
    templates.value.splice(index, 1)
    
    ElMessage.success(`模板 "${template.name}" 删除成功`)
    
    // 如果删除的是当前选中的模板，清空选择
    if (selectedTemplate.value?.id === template.id) {
      selectedTemplate.value = null
    }
    
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`删除失败: ${error.message || '未知错误'}`)
      // 如果删除失败（例如404错误），重新加载模板列表
      // 这可能是因为模板在数据库中不存在，但前端仍然显示
      await loadTemplates()
    }
  } finally {
    deletingTemplateId.value = null
  }
}

const handleCreateNew = () => {
  emit('create-new')
  dialogVisible.value = false
}

const handleClose = () => {
  selectedTemplate.value = null
  searchKeyword.value = ''
}

// 生命周期
onMounted(() => {
  loadTemplates()
})

// 暴露方法
defineExpose({
  loadTemplates
})
</script>

<style scoped>
@import '@/assets/css/dialog.css';
</style>
/* 文件查看弹窗 - 从knowledge.vue中提取 */

<template>
  <el-dialog
    v-model="visible"
    :title="document?.name"
    width="80%"
    top="5vh"
    @close="handleClose"
  >
    <div class="document-viewer">
      <div v-if="documentContent" class="document-content">
        <div class="document-meta">
          <el-tag type="info">路径: {{ document?.path }}</el-tag>
          <el-tag type="info">大小: {{ document?.size }}</el-tag>
          <el-tag type="info">格式: {{ document?.extension }}</el-tag>
        </div>
        <div class="content-area">
          <pre>{{ documentContent }}</pre>
        </div>
      </div>
      <div v-else class="loading-content">
        <el-skeleton :rows="10" animated />
      </div>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button size="medium" @click="handleCancel">关闭</el-button>
        <el-button type="primary" size="medium" @click="handleDownload" v-if="document">
          下载
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { DirectoryItem } from '@/api/knowledge'

interface Props {
  modelValue: boolean
  document: DirectoryItem | null
  documentContent: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'download', document: DirectoryItem): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = ref(false)

// 监听外部modelValue变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

// 监听内部visible变化
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

const handleCancel = () => {
  visible.value = false
}

const handleClose = () => {
  visible.value = false
}

const handleDownload = () => {
  if (props.document) {
    emit('download', props.document)
  }
}
</script>


/* 上传文档弹窗 - 从knowledge.vue中提取 */

<template>
  <el-dialog
    v-model="visible"
    :title="`上传文档到 ${directoryName}`"
    width="500px"
    @close="handleClose"
  >
    <div class="upload-dialog">
      <el-form :model="form" label-width="100px">
        <el-form-item label="选择文件" required>
          <el-upload
            class="upload-demo"
            drag
            multiple
            :auto-upload="false"
            :on-change="handleFileChange"
            :before-upload="beforeUpload"
            :show-file-list="true"
            accept=".txt,.md,.pdf,.docx"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持.txt、.md、.pdf、.docx格式文件，且大小不超过10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button size="medium" @click="handleCancel">取消</el-button>
        <el-button type="primary" size="medium" @click="handleConfirm" :loading="loading">
          上传
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@/icons'

interface Props {
  modelValue: boolean
  directoryName: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', files: File[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = ref(false)
const loading = ref(false)
const form = ref({
  files: [] as File[]
})

// 计算属性用于显示目录名
const directoryName = computed(() => props.directoryName)

// 监听外部modelValue变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal) {
    // 重置表单
    form.value = { files: [] }
  }
})

// 监听内部visible变化
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

// 文件上传处理
const handleFileChange = (_file: any, fileList: any[]) => {
  form.value.files = fileList.map(f => f.raw)
}

const beforeUpload = (file: File) => {
  const supportedExtensions = ['.txt', '.md', '.pdf', '.docx']
  const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
  const isSupported = supportedExtensions.includes(fileExtension)
  const isLt10M = file.size / 1024 / 1024 < 10
    
  if (!isSupported) {
    ElMessage.error(`只能上传${supportedExtensions.join('、')}格式文件!`)
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过10MB!')
    return false
  }
  return true
}

const handleConfirm = async () => {
  if (!form.value.files || form.value.files.length === 0) {
    ElMessage.error('请选择要上传的文件')
    return
  }
  
  loading.value = true
  try {
    emit('confirm', form.value.files)
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  visible.value = false
}

const handleClose = () => {
  visible.value = false
}
</script>
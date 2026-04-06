/* 添加文件夹弹窗 - 从knowledge.vue中提取 */

<template>
  <el-dialog
    v-model="visible"
    title="添加文件夹"
    width="500px"
    @close="handleClose"
  >
    <div class="add-directory-dialog">
      <el-form :model="form" label-width="100px">
        <el-form-item label="文件夹名" required>
          <el-input v-model="form.folderName" placeholder="例如：contract_templates 或 合同模板" />
          <div class="form-tip">实际创建的文件夹名称，将同时作为显示名称</div>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button size="medium" @click="handleCancel">取消</el-button>
        <el-button type="primary" size="medium" @click="handleConfirm" :loading="loading">
          创建
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', folderName: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = ref(false)
const loading = ref(false)
const form = ref({
  folderName: ''
})

// 监听外部modelValue变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal) {
    // 重置表单
    form.value = { folderName: '' }
  }
})

// 监听内部visible变化
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

const handleConfirm = async () => {
  if (!form.value.folderName) {
    ElMessage.error('请填写文件夹名')
    return
  }
  
  loading.value = true
  try {
    emit('confirm', form.value.folderName)
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

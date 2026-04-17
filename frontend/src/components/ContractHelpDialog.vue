/* 使用帮助弹窗 - 从Contract.vue中提取 */

<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    @close="handleClose"
  >
    <div class="help-content">
      <h4>功能介绍</h4>
      <p>合同智能诊断功能基于AI技术和本地法律知识库，能够自动分析合同文档中的潜在风险，并提供专业的修改建议。</p>
      
      <h4>使用步骤</h4>
      <ol>
        <li>上传合同文件（支持.docx、.doc、.txt格式）</li>
        <li>确认合同基本信息和类型</li>
        <li>AI基于知识库进行风险识别</li>
        <li>查看诊断报告和修改建议</li>
      </ol>
      
      <h4>注意事项</h4>
      <ul>
        <li>确保上传的合同文件内容清晰可读</li>
        <li>分析过程可能需要1-3分钟，请耐心等待</li>
        <li>AI建议仅供参考，重要合同请咨询专业律师</li>
        <li>系统支持本地Ollama模型和云端SiliconFlow模型</li>
      </ul>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  width?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '合同诊断使用帮助',
  width: '50%'
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'close': []
}>()

const visible = ref(props.modelValue)

// 监听外部modelValue变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

// 监听内部visible变化
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

const handleClose = () => {
  visible.value = false
  emit('close')
}
</script>


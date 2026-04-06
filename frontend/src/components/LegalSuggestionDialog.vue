/* 法律建议弹窗 - 从Survey.vue中提取 */

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="aiGenerating ? 'AI正在生成法律建议...' : 'AI法律建议'"
    width="900px"
    :close-on-click-modal="false"
    :show-close="!aiGenerating"
    @close="handleClose"
  >
    <div v-if="aiGenerating" class="ai-generating-content">
      <div class="loading-container">
        <el-icon class="loading-icon" :size="48" color="#409eff"><Loading /></el-icon>
        <h3>AI正在分析您的调查表...</h3>
        <p>系统正在根据您的企业信息生成个性化的法律建议，请稍候。</p>
        <el-progress :percentage="aiProgress" :status="aiProgressStatus" :stroke-width="8" />
        <p class="loading-tip">这通常需要10-30秒，请耐心等待</p>
      </div>
    </div>
    
    <div v-else class="suggestion-content">
      <div class="suggestion-body">
        <div v-if="suggestion?.suggestion" v-html="formatSuggestion(suggestion.suggestion)"></div>
        <div v-else class="no-suggestion">
          <el-empty description="未生成法律建议" :image-size="60" />
          <p class="no-suggestion-tip">AI分析已完成，但未生成具体的法律建议。这可能是因为您的调查表信息没有显著变更。</p>
        </div>
        
        <!-- 显示触发变更的字段 -->
        <div v-if="suggestion?.trigger_changes && Object.keys(suggestion.trigger_changes).length > 0" class="trigger-changes-section">
          <el-divider>触发变更的字段</el-divider>
          <div class="trigger-changes-list">
            <div v-for="(change, field) in suggestion.trigger_changes" :key="field" class="change-item">
              <div class="change-field">{{ getFieldLabel(field) }}:</div>
              <div class="change-values">
                <span class="previous-value">之前: {{ formatChangeValue(change.previous) }}</span>
                <el-icon><Right /></el-icon>
                <span class="current-value">现在: {{ formatChangeValue(change.current) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="suggestion-footer">
        <p class="generated-time">生成时间: {{ formatTime(suggestion?.created_at) }}</p>
        <p class="suggestion-tip">此建议基于您的企业信息和最新法律法规生成，仅供参考。</p>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button v-if="!aiGenerating" @click="handleClose">关闭</el-button>
        <el-button v-if="aiGenerating" disabled>AI生成中...</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Loading, Right } from '@element-plus/icons-vue'
import type { LegalSuggestion } from '@/types/survey'
// 导入弹窗样式
import '@/assets/css/dialog.css'

interface Props {
  modelValue: boolean
  aiGenerating?: boolean
  aiProgress?: number
  suggestion?: LegalSuggestion | null
  templateFields?: Record<string, any> | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  aiGenerating: false,
  aiProgress: 0,
  suggestion: null,
  templateFields: null
})

const emit = defineEmits<Emits>()

// 计算属性：弹窗显示状态
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 计算属性：AI进度状态
const aiProgressStatus = computed(() => {
  if (props.aiProgress >= 100) return 'success'
  if (props.aiProgress >= 70) return 'warning'
  return 'success'
})

// 方法：关闭弹窗
const handleClose = () => {
  dialogVisible.value = false
  emit('close')
}

// 方法：格式化建议内容
const formatSuggestion = (suggestion: string = '') => {
  // 将文本转换为HTML格式，保留换行
  return suggestion.replace(/\n/g, '<br>').replace(/1\./g, '<br>1.').replace(/2\./g, '<br>2.').replace(/3\./g, '<br>3.').replace(/4\./g, '<br>4.')
}

// 方法：格式化时间
const formatTime = (time: string = '') => {
  if (!time) return '刚刚'
  return new Date(time).toLocaleString('zh-CN')
}

// 方法：获取字段标签
const getFieldLabel = (field: string) => {
  if (props.templateFields && props.templateFields[field]) {
    return props.templateFields[field].label || field
  }
  return field
}

// 方法：格式化变更值
const formatChangeValue = (value: any) => {
  if (value === null || value === undefined) {
    return '未填写'
  }
  if (typeof value === 'boolean') {
    return value ? '是' : '否'
  }
  if (Array.isArray(value)) {
    return value.length > 0 ? value.join(', ') : '无'
  }
  return String(value)
}
</script>
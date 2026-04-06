/**
 * 图标集中管理文件
 * 包含项目中使用的所有Element Plus图标
 * 每个图标都有对应的中文名称和来源文件备注
 */

// 从Element Plus图标库导入所有使用的图标
import {
  ScaleToOriginal,  // 系统logo图标
  Document,         // 文档/企业调查表图标
  ChatDotRound,     // 法务咨询图标
  Files,            // 文件/合同诊断图标
  Clock,            // 时钟/咨询历史图标
  Reading,          // 阅读/知识库图标
  Upload,           // 上传图标
  UploadFilled,     // 上传填充图标
  Position,         // 位置图标
  ChatLineRound,    // 聊天线条图标
  Refresh,          // 刷新图标
  Search,           // 搜索图标
  Warning,          // 警告图标
  TrendCharts,      // 趋势图表图标
  InfoFilled,       // 信息填充图标
} from '@element-plus/icons-vue'

// 图标信息映射表
export const iconInfo = {
  // App.vue 使用的图标
  ScaleToOriginal: {
    name: '系统logo图标',
    description: '系统主logo，代表法律咨询系统',
    source: 'App.vue, Home.vue',
    component: ScaleToOriginal
  },
  Document: {
    name: '文档图标',
    description: '代表企业调查表、文档等',
    source: 'App.vue, Survey.vue, Knowledge.vue',
    component: Document
  },
  ChatDotRound: {
    name: '法务咨询图标',
    description: '代表聊天咨询功能',
    source: 'App.vue, Home.vue',
    component: ChatDotRound
  },
  Files: {
    name: '文件图标',
    description: '代表合同诊断、文件管理',
    source: 'App.vue, Contract.vue, History.vue, Knowledge.vue',
    component: Files
  },
  Clock: {
    name: '时钟图标',
    description: '代表咨询历史、时间相关功能',
    source: 'App.vue, History.vue',
    component: Clock
  },
  Reading: {
    name: '阅读图标',
    description: '代表知识库、阅读功能',
    source: 'App.vue, Knowledge.vue',
    component: Reading
  },

  // Contract.vue 使用的图标
  Upload: {
    name: '上传图标',
    description: '代表上传合同功能',
    source: 'Contract.vue',
    component: Upload
  },
  UploadFilled: {
    name: '上传填充图标',
    description: '上传区域的填充图标',
    source: 'Contract.vue',
    component: UploadFilled
  },
  Position: {
    name: '位置图标',
    description: '代表条款位置',
    source: 'Contract.vue',
    component: Position
  },

  // History.vue 使用的图标
  ChatLineRound: {
    name: '聊天线条图标',
    description: '代表聊天会话历史',
    source: 'History.vue',
    component: ChatLineRound
  },
  Refresh: {
    name: '刷新图标',
    description: '代表刷新、更新功能',
    source: 'History.vue, Knowledge.vue',
    component: Refresh
  },

  // Knowledge.vue 使用的图标
  Search: {
    name: '搜索图标',
    description: '代表搜索功能',
    source: 'Knowledge.vue',
    component: Search
  },
  Warning: {
    name: '警告图标',
    description: '代表警告、不支持的功能',
    source: 'Knowledge.vue',
    component: Warning
  },
}

// 按来源文件分组导出
export const iconsByFile = {
  'App.vue': [
    { icon: 'ScaleToOriginal', name: '系统logo图标' },
    { icon: 'Document', name: '企业调查表图标' },
    { icon: 'ChatDotRound', name: '法务咨询图标' },
    { icon: 'Files', name: '合同诊断图标' },
    { icon: 'Clock', name: '咨询历史图标' },
    { icon: 'Reading', name: '知识库图标' },
  ],
  'Home.vue': [
    { icon: 'ScaleToOriginal', name: '系统logo图标' },
    { icon: 'Plus', name: '新建对话图标' },
    { icon: 'ChatDotRound', name: '法务咨询图标' },
  ],
  'Survey.vue': [
    { icon: 'Document', name: '企业调查表图标' },
    { icon: 'Select', name: '选定企业调查表图标' },
    { icon: 'Plus', name: '创建企业调查表图标' },
  ],
  'Contract.vue': [
    { icon: 'Files', name: '合同诊断图标' },
    { icon: 'Upload', name: '上传合同图标' },
    { icon: 'UploadFilled', name: '上传区域图标' },
    { icon: 'Position', name: '位置图标' },
  ],
  'History.vue': [
    { icon: 'Clock', name: '咨询历史图标' },
    { icon: 'ChatLineRound', name: '聊天会话图标' },
    { icon: 'Plus', name: '新建会话/调查表图标' },
    { icon: 'Refresh', name: '刷新记录图标' },
    { icon: 'Files', name: '合同分析历史图标' },
  ],
  'Knowledge.vue': [
    { icon: 'Reading', name: '知识库图标' },
    { icon: 'Refresh', name: '刷新文档图标' },
    { icon: 'Files', name: '文档列表图标' },
    { icon: 'Search', name: '搜索图标' },
    { icon: 'Document', name: '文档图标' },
    { icon: 'Warning', name: '警告图标' },
  ],
}

// 导出所有图标组件
export {
  ScaleToOriginal,
  Document,
  ChatDotRound,
  Files,
  Clock,
  Reading,
  Upload,
  UploadFilled,
  Position,
  ChatLineRound,
  Refresh,
  Search,
  Warning,
  TrendCharts,
  InfoFilled,
}

// 默认导出所有图标
export default {
  ScaleToOriginal,
  Document,
  ChatDotRound,
  Files,
  Clock,
  Reading,
  Upload,
  UploadFilled,
  Position,
  ChatLineRound,
  Refresh,
  Search,
  Warning,
  TrendCharts,
  InfoFilled,
}
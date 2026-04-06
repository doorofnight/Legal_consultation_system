<template>
  <div class="contract-container">
    <el-card class="contract-header-card">
      <div class="contract-header">
        <div class="header-left">
          <el-icon><Files /></el-icon>
          <h2>合同智能诊断</h2>
        </div>
        <div class="header-right">
          <el-tag type="warning" size="large">开发中</el-tag>
          <el-button type="primary" size="small" disabled>
            <el-icon><Upload /></el-icon>
            上传合同
          </el-button>
        </div>
      </div>
      <div class="contract-subtitle">
        <p>上传合同文件，系统将基于本地知识库进行离线风险识别，标注风险条款并给出修改建议。</p>
      </div>
    </el-card>

    <div class="contract-content">
      <!-- 上传区域 -->
      <el-card class="upload-card">
        <template #header>
          <div class="upload-header">
            <h3>合同文件上传</h3>
            <p class="upload-description">支持Word(.doc/.docx)和PDF格式，最大文件大小10MB</p>
          </div>
        </template>
        
        <div class="upload-area">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            multiple
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="fileList"
            accept=".doc,.docx,.pdf"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 Word 和 PDF 格式文件，单个文件不超过10MB
              </div>
            </template>
          </el-upload>
          
          <div class="upload-actions" v-if="fileList.length > 0">
            <el-button type="primary" @click="analyzeContract" :loading="isAnalyzing">
              开始分析
            </el-button>
            <el-button @click="clearFiles">清空文件</el-button>
          </div>
        </div>
      </el-card>

      <!-- 分析结果 -->
      <div class="analysis-section">
        <el-card class="analysis-card">
          <template #header>
            <div class="analysis-header">
              <h3>合同分析结果</h3>
              <el-tag type="info">示例数据</el-tag>
            </div>
          </template>
          
          <div class="analysis-content">
            <div class="contract-info">
              <div class="info-item">
                <span class="info-label">合同名称：</span>
                <span class="info-value">劳动合同示例</span>
              </div>
              <div class="info-item">
                <span class="info-label">文件类型：</span>
                <span class="info-value">Word文档</span>
              </div>
              <div class="info-item">
                <span class="info-label">分析时间：</span>
                <span class="info-value">2026-03-11 10:30:00</span>
              </div>
              <div class="info-item">
                <span class="info-label">风险等级：</span>
                <el-tag type="warning">中等风险</el-tag>
              </div>
            </div>
            
            <div class="risk-items">
              <h4>风险条款识别</h4>
              <div class="risk-list">
                <div class="risk-item" v-for="(risk, index) in riskItems" :key="index">
                  <div class="risk-header">
                    <div class="risk-title">
                      <el-tag :type="risk.type" size="small">{{ risk.level }}</el-tag>
                      <strong>{{ risk.title }}</strong>
                    </div>
                    <div class="risk-position">
                      <el-icon><Position /></el-icon>
                      <span>第{{ risk.position }}条</span>
                    </div>
                  </div>
                  <div class="risk-content">
                    <div class="risk-original">
                      <p class="content-label">原文内容：</p>
                      <p class="content-text">{{ risk.original }}</p>
                    </div>
                    <div class="risk-analysis">
                      <p class="content-label">风险分析：</p>
                      <p class="content-text">{{ risk.analysis }}</p>
                    </div>
                    <div class="risk-suggestion">
                      <p class="content-label">修改建议：</p>
                      <p class="content-text">{{ risk.suggestion }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
// 从图标集中管理文件导入图标
import {
  Files,
  Upload,
  UploadFilled,
  Position
} from '@/icons'

import { ElMessage, type UploadProps, type UploadUserFile } from 'element-plus'

// 导入共享CSS
import '@/assets/css/variables.css'
import '@/assets/css/utilities.css'

const fileList = ref<UploadUserFile[]>([])
const isAnalyzing = ref(false)

const handleFileChange: UploadProps['onChange'] = (_uploadFile, uploadFiles) => {
  fileList.value = uploadFiles
}

const analyzeContract = () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先上传合同文件')
    return
  }
  
  isAnalyzing.value = true
  // 模拟分析过程
  setTimeout(() => {
    ElMessage.success('合同分析完成！')
    isAnalyzing.value = false
  }, 2000)
}

const clearFiles = () => {
  fileList.value = []
}

// 示例风险条款
const riskItems = ref([
  {
    title: '试用期过长',
    level: '高风险',
    type: 'danger',
    position: '3',
    original: '试用期为6个月，试用期工资为正式工资的80%。',
    analysis: '根据《劳动合同法》第十九条规定，劳动合同期限一年以上不满三年的，试用期不得超过二个月。',
    suggestion: '建议将试用期修改为不超过二个月，试用期工资不得低于本单位相同岗位最低档工资或者劳动合同约定工资的百分之八十。'
  },
  {
    title: '违约金条款不合理',
    level: '中等风险',
    type: 'warning',
    position: '8',
    original: '员工提前解除劳动合同需支付违约金，金额为三个月工资。',
    analysis: '根据《劳动合同法》第二十五条规定，除专项培训费用和竞业限制外，用人单位不得与劳动者约定由劳动者承担违约金。',
    suggestion: '建议删除该违约金条款，或仅针对专项培训费用和竞业限制约定违约金。'
  },
  {
    title: '工作地点约定不明确',
    level: '低风险',
    type: 'info',
    position: '5',
    original: '工作地点为公司指定地点。',
    analysis: '工作地点约定过于模糊，可能引发劳动争议。',
    suggestion: '建议明确具体工作地点，如"工作地点为XX市XX区XX路XX号"。'
  }
])

</script>

<style scoped>
.contract-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.contract-header-card {
  width: 100%;
}

.contract-header {
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

.contract-subtitle p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.contract-content {
  display: flex;
  gap: 20px;
}

.upload-card {
  flex: 1;
}

.upload-header h3 {
  margin: 0 0 8px;
  color: #303133;
}

.upload-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.upload-area {
  padding: 20px;
}

.upload-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

.analysis-section {
  flex: 2;
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.analysis-header h3 {
  margin: 0;
  color: #303133;
}

.analysis-content {
  padding: 20px 0;
}

.contract-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  font-weight: 500;
  color: #606266;
}

.info-value {
  color: #303133;
}

.risk-items h4 {
  margin: 0 0 20px;
  color: #303133;
  font-size: 18px;
}

.risk-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.risk-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s;
}

.risk-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.risk-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.risk-title strong {
  font-size: 16px;
  color: #303133;
}

.risk-position {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 14px;
}

.risk-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.content-label {
  font-weight: 500;
  color: #606266;
  margin: 0 0 8px;
  font-size: 14px;
}

.content-text {
  margin: 0;
  color: #303133;
  line-height: 1.6;
  font-size: 14px;
}

.risk-original,
.risk-analysis,
.risk-suggestion {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 6px;
}

.risk-suggestion {
  background-color: #f0f9ff;
  border-left: 4px solid #409eff;
}

.contract-sidebar {
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.knowledge-card,
.progress-card {
  height: auto;
}

.knowledge-header,
.progress-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.knowledge-header h3,
.progress-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.knowledge-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.knowledge-item {
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.knowledge-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.knowledge-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.knowledge-title strong {
  font-size: 14px;
  color: #303133;
}

.knowledge-desc {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.progress-content {
  padding: 10px 0;
}
</style>
  padding-bottom: 0;
}

<style>
.knowledge-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.knowledge-title strong {
  font-size: 14px;
  color: #303133;
}

.knowledge-desc {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.progress-content {
  padding: 10px 0;
}
</style>
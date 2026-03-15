<template>
  <div class="survey-container">
    <el-card class="survey-header-card">
      <div class="survey-header">
        <div class="header-left">
          <el-icon size="28" color="#409eff"><Document /></el-icon>
          <h2>企业调查表</h2>
        </div>
        <div class="header-right">
          <el-tag type="warning" size="large">开发中</el-tag>
          <el-button type="primary" size="small" disabled>
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
        </div>
      </div>
      <div class="survey-subtitle">
        <p>填写企业基本信息，系统将根据您的企业情况提供个性化的法律建议。</p>
      </div>
    </el-card>

    <div class="survey-content">
      <el-card class="survey-form-card">
        <template #header>
          <div class="form-header">
            <h3>企业基本信息调查表</h3>
            <p class="form-description">请填写以下信息，所有字段均为必填项</p>
          </div>
        </template>
        
        <el-form :model="surveyForm" label-width="120px" class="survey-form">
          <el-form-item label="企业名称">
            <el-input v-model="surveyForm.companyName" placeholder="请输入企业全称" />
          </el-form-item>
          
          <el-form-item label="企业类型">
            <el-select v-model="surveyForm.companyType" placeholder="请选择企业类型">
              <el-option label="有限责任公司" value="limited" />
              <el-option label="股份有限公司" value="joint_stock" />
              <el-option label="合伙企业" value="partnership" />
              <el-option label="个人独资企业" value="sole_proprietorship" />
              <el-option label="外商投资企业" value="foreign_invested" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="所属行业">
            <el-select v-model="surveyForm.industry" placeholder="请选择所属行业">
              <el-option label="制造业" value="manufacturing" />
              <el-option label="信息技术" value="it" />
              <el-option label="金融业" value="finance" />
              <el-option label="建筑业" value="construction" />
              <el-option label="批发零售" value="retail" />
              <el-option label="服务业" value="service" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="员工人数">
            <el-input-number v-model="surveyForm.employeeCount" :min="1" :max="10000" />
          </el-form-item>
          
          <el-form-item label="注册资本">
            <el-input v-model="surveyForm.registeredCapital" placeholder="请输入注册资本（万元）">
              <template #append>万元</template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="成立时间">
            <el-date-picker
              v-model="surveyForm.establishmentDate"
              type="date"
              placeholder="选择成立日期"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          
          <el-form-item label="经营范围">
            <el-input
              v-model="surveyForm.businessScope"
              type="textarea"
              :rows="3"
              placeholder="请输入企业经营范围"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="法律需求">
            <el-checkbox-group v-model="surveyForm.legalNeeds">
              <el-checkbox label="劳动合同管理" />
              <el-checkbox label="知识产权保护" />
              <el-checkbox label="合同审查" />
              <el-checkbox label="公司治理" />
              <el-checkbox label="税务合规" />
              <el-checkbox label="风险防控" />
            </el-checkbox-group>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" size="large" @click="submitSurvey" :loading="isSubmitting">
              提交调查表
            </el-button>
            <el-button size="large" @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  Document, 
  Download, 
  InfoFilled, 
  TrendCharts 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const surveyForm = ref({
  companyName: '',
  companyType: '',
  industry: '',
  employeeCount: 10,
  registeredCapital: '',
  establishmentDate: '',
  businessScope: '',
  legalNeeds: []
})

const isSubmitting = ref(false)

const submitSurvey = () => {
  isSubmitting.value = true
  // 模拟提交
  setTimeout(() => {
    ElMessage.success('调查表提交成功！系统将开始分析您的企业情况')
    isSubmitting.value = false
  }, 1500)
}

const resetForm = () => {
  surveyForm.value = {
    companyName: '',
    companyType: '',
    industry: '',
    employeeCount: 10,
    registeredCapital: '',
    establishmentDate: '',
    businessScope: '',
    legalNeeds: []
  }
}
</script>

<style scoped>
.survey-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.survey-header-card {
  width: 100%;
}

.survey-header {
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

.survey-subtitle p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.survey-content {
  display: flex;
  gap: 20px;
}

.survey-form-card {
  flex: 1;
}

.form-header h3 {
  margin: 0 0 8px;
  color: #303133;
}

.form-description {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.survey-form {
  max-width: 800px;
}

.survey-sidebar {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tips-card,
.progress-card {
  height: auto;
}

.tips-header,
.progress-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tips-header h3,
.progress-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.tips-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.tips-content p {
  margin: 8px 0;
}

.progress-content {
  padding: 10px 0;
}
</style>
<template>
  <div id="app">
    <el-header class="app-header">
      <div class="header-container">
        <!-- 左侧 -->
        <div class="header-left">
          <el-icon size="28" color="#409eff"><ScaleToOriginal /></el-icon>
          <h1>AI 法律咨询系统</h1>
        </div>
        
        <!-- 中间 -->
        <div class="header-center">
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            :ellipsis="false"
            @select="handleMenuSelect"
            class="nav-menu"
          >
            <el-menu-item index="/survey">
              <el-icon><Document /></el-icon>
              <span>企业调查表</span>
            </el-menu-item>
            <el-menu-item index="/">
              <el-icon><ChatDotRound /></el-icon>
              <span>法务咨询</span>
            </el-menu-item>
            <el-menu-item index="/contract">
              <el-icon><Files /></el-icon>
              <span>合同诊断</span>
            </el-menu-item>
            <el-menu-item index="/history">
              <el-icon><Clock /></el-icon>
              <span>咨询历史</span>
            </el-menu-item>
            <el-menu-item index="/knowledge">
              <el-icon><Reading /></el-icon>
              <span>知识库</span>
            </el-menu-item>
          </el-menu>
        </div>
        
        <!-- 右侧占位（可选，保持视觉平衡） -->
        <div class="header-right"></div>
      </div>
    </el-header>

    <el-main class="app-main">
      <router-view />
    </el-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ScaleToOriginal,
  Document,
  ChatDotRound,
  Files,
  Clock,
  Reading
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 计算当前激活的菜单
const activeMenu = computed(() => route.path)

// 菜单选择处理
const handleMenuSelect = (index: string) => {
  router.push(index)
}

// 初始化
onMounted(() => {
})
</script>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-menu {
  background: transparent;
  border-bottom: none;
}

.nav-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  height: 60px;
  line-height: 60px;
  border-bottom: 3px solid transparent;
}

.nav-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-menu :deep(.el-menu-item.is-active) {
  color: white;
  border-bottom-color: white;
  background: rgba(255, 255, 255, 0.1);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-main {
  flex: 1;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  background: white;
  border-top: 1px solid #ebeef5;
  padding: 20px 24px;
  text-align: center;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
}

.footer-content p {
  margin: 8px 0;
  color: #909399;
  font-size: 14px;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 12px;
}

.form-tip {
  margin-left: 8px;
  color: #909399;
  font-size: 14px;
}
</style>
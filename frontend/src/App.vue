<template>
  <div id="app">
    <el-header class="app-header">
      <div class="header-container">
        <!-- 左侧 -->
        <div class="header-left">
          <el-icon ><ScaleToOriginal /></el-icon>
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
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
// 从图标集中管理文件导入图标
import {
  ScaleToOriginal,
  Document,
  ChatDotRound,
  Files,
  Clock,
  Reading
} from '@/icons'

// 导入全局样式
import '@/assets/css/variables.css'
import '@/assets/css/utilities.css'

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

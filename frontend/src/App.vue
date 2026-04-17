<template>
  <div id="app" :class="['min-h-screen transition-colors duration-300', isDark ? 'bg-gray-900' : 'bg-gray-50']">
    <!-- Orthogonal Grid Background -->
    <div class="fixed inset-0 pointer-events-none">
      <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern
            id="grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              :stroke="isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'"
              stroke-width="1"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>
    </div>

    <!-- Animated Menu Header -->
    <header class="relative z-20 px-6 py-4 flex items-center justify-between">
      <button
        @click="toggleMenu"
        :class="['p-2 rounded-lg transition-colors shadow-lg animated-menu-button', 
          isDark ? 'bg-gray-800 text-white hover:bg-gray-700' : 'bg-white text-gray-900 hover:bg-gray-100',
          isMenuOpen ? 'bg-black text-white' : ''
        ]"
        :style="{
          backgroundColor: isMenuOpen ? '#000000' : '',
          transition: 'background-color 0.3s ease, transform 0.2s ease'
        }"
      >
         <component :is="isMenuOpen ? XIcon : MenuIcon" :size="24" />
      </button>

      <h1
        :class="['text-2xl font-bold', isDark ? 'text-white' : 'text-gray-900']"
        class="animated-title"
      >
        AI 法律咨询系统
      </h1>

      <button
        @click="toggleTheme"
        :class="['p-2 rounded-lg transition-colors shadow-lg',
          isDark ? 'bg-gray-800 text-yellow-400 hover:bg-gray-700' : 'bg-white text-gray-900 hover:bg-gray-100'
        ]"
        class="animated-button"
      >
        <component :is="isDark ? SunIcon : MoonIcon" :size="24" />
      </button>
    </header>

    <!-- Overlay -->
    <transition
      enter-active-class="duration-400"
      leave-active-class="duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isMenuOpen"
        @click="closeMenu"
        class="fixed inset-0 bg-black bg-opacity-50 z-30"
      />
    </transition>

    <!-- Side Menu -->
    <div
      :class="['fixed top-0 left-0 h-full w-64 z-40 shadow-2xl transition-transform duration-300',
        isDark ? 'bg-gray-800' : 'bg-white',
        isMenuOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
      @mousedown="startDrag"
      @touchstart="startDrag"
      @mousemove="handleDrag"
      @touchmove="handleDrag"
      @mouseup="endDrag"
      @touchend="endDrag"
      ref="menuRef"
    >
      <!-- Close Button -->
      <button
        @click="closeMenu"
        :class="['absolute top-6 right-6 p-2 rounded-full transition-colors',
          isDark ? 'bg-gray-700 text-white hover:bg-gray-600' : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
        ]"
        class="animated-button"
      >
        <XIcon :size="24" />
      </button>

      <div class="p-8 pt-20">
        <div class="mb-8">
          <div class="header-left">
            <el-icon :size="30" :class="['page-title-icon', isDark ? 'text-white' : 'text-gray-900']">
              <MenuIcon />
            </el-icon>
            <h2
              :class="['text-2xl font-bold', isDark ? 'text-white' : 'text-gray-900']"
            >
              导航菜单
            </h2>
          </div>
          <div
            :class="['h-1 mt-2 rounded', isDark ? 'bg-blue-500' : 'bg-blue-600']"
            :style="{ width: isMenuOpen ? '60px' : '0', transition: 'width 0.6s ease-out' }"
          />
        </div>

        <ul class="list-none p-0 m-0">
          <li v-for="(item, i) in menuItems" :key="item.index">
            <a
              @click="handleMenuSelect(item.index)"
              :class="['flex items-center space-x-3 p-3 rounded-lg transition-all group menu-item',
                isDark ? 'hover:bg-gray-700 text-gray-200' : 'hover:bg-gray-100 text-gray-800',
                activeMenu === item.index ? (isDark ? 'bg-gray-700' : 'bg-gray-100') : ''
              ]"
              :style="{
                opacity: isMenuOpen ? 1 : 0,
                transform: isMenuOpen ? 'translateX(0)' : 'translateX(-50px)',
                transition: `opacity 0.3s ${0.1 + i * 0.08}s, transform 0.3s ${0.1 + i * 0.08}s, background-color 0.2s`
              }"
            >
              <div
                :class="['p-2 rounded-lg transition-all duration-300 flex items-center justify-center',
                  isDark ? 'bg-gray-700' : 'bg-gray-200',
                  'group-hover:bg-blue-500 group-hover:text-white',
                   activeMenu === item.index ? (isDark ? 'bg-blue-600' : 'bg-blue-500 text-white') : ''
                ]"
              >
                <el-icon :size="20">
                  <component :is="item.icon" />
                </el-icon>
              </div>
              <span class="font-medium">{{ item.label }}</span>
            </a>
          </li>
        </ul>

        <div
          :class="['absolute bottom-8 left-8 right-8 p-4 rounded-lg',
            isDark ? 'bg-gray-700' : 'bg-gray-100'
          ]"
          :style="{
            opacity: isMenuOpen ? 1 : 0,
            transform: isMenuOpen ? 'translateY(0)' : 'translateY(20px)',
            transition: 'opacity 0.5s 0.7s, transform 0.5s 0.7s'
          }"
        >
          <p
            :class="['text-sm', isDark ? 'text-gray-300' : 'text-gray-600']"
          >
            💡 向左拖动关闭菜单
          </p>
        </div>
      </div>
    </div>

    <!-- Main Content with left margin for menu icon -->
    <main class="relative z-10 px-6 py-8 ml-16 transition-all duration-300" :style="{ marginLeft: isMenuOpen ? '16rem' : '4rem' }">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Menu as MenuIcon,
  X as XIcon,
  Sun as SunIcon,
  Moon as MoonIcon,
  ChatDotRound,
  Document,
  Files,
  Clock,
  Reading,
  ScaleToOriginal
} from './icons'

// 导入全局样式
import '@/assets/css/main.scss'

const route = useRoute()
const router = useRouter()

const isMenuOpen = ref(false)
const isDark = ref(false)
const isDragging = ref(false)
const startX = ref(0)
const currentX = ref(0)
const menuRef = ref<HTMLElement | null>(null)

const menuItems = [
  { icon: ChatDotRound, label: '法务咨询', index: '/' },
  { icon: Document, label: '企业调查表', index: '/survey' },
  { icon: Files, label: '合同诊断', index: '/contract' },
  { icon: Clock, label: '咨询历史', index: '/history' },
  { icon: Reading, label: '知识库', index: '/knowledge' },
]

// 计算当前激活的菜单
const activeMenu = computed(() => route.path)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
}

const toggleTheme = () => {
  isDark.value = !isDark.value
}

// 菜单选择处理
const handleMenuSelect = (index: string) => {
  router.push(index)
  closeMenu()
}

// 拖动功能
const startDrag = (e: MouseEvent | TouchEvent) => {
  if (!isMenuOpen.value) return
  isDragging.value = true
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
  startX.value = clientX
  currentX.value = 0
}

const handleDrag = (e: MouseEvent | TouchEvent) => {
  if (!isDragging.value || !isMenuOpen.value) return
  
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
  const deltaX = clientX - startX.value
  currentX.value = Math.min(0, deltaX)
  
  if (menuRef.value) {
    menuRef.value.style.transform = `translateX(${currentX.value}px)`
  }
}

const endDrag = () => {
  if (!isDragging.value) return
  
  isDragging.value = false
  
  if (currentX.value < -100) {
    closeMenu()
  }
  
  // 清除内联transform样式，让CSS类控制位置
  if (menuRef.value) {
    menuRef.value.style.transform = ''
  }
  currentX.value = 0
}

// 添加键盘事件支持
const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && isMenuOpen.value) {
    closeMenu()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* 动画菜单按钮样式 */
.animated-menu-button {
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.animated-menu-button:hover {
  transform: scale(1.1);
}

.animated-menu-button:active {
  transform: scale(0.95);
}

/* 菜单项样式 */
.menu-item {
  cursor: pointer;
}

/* 标题动画 */
.animated-title {
  animation: fadeInDown 0.5s ease;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

</style>

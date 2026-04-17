<template>
  <div :class="['w-full min-h-screen transition-colors duration-300', isDark ? 'bg-gray-900' : 'bg-gray-50']">
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

    <!-- Header -->
    <header class="relative z-20 px-6 py-4 flex items-center justify-between">
      <button
        @click="toggleMenu"
        :class="['p-2 rounded-lg transition-colors shadow-lg', 
          isDark ? 'bg-gray-800 text-white hover:bg-gray-700' : 'bg-white text-gray-900 hover:bg-gray-100'
        ]"
        class="animated-button"
      >
        <component :is="isOpen ? XIcon : MenuIcon" :size="24" />
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
        v-if="isOpen"
        @click="closeMenu"
        class="fixed inset-0 bg-black bg-opacity-50 z-30"
      />
    </transition>

    <!-- Side Menu -->
    <div
      :class="['fixed top-0 left-0 h-full w-80 z-40 shadow-2xl transition-transform duration-300',
        isDark ? 'bg-gray-800' : 'bg-white',
        isOpen ? 'translate-x-0' : '-translate-x-full'
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

      <!-- Drag Indicator -->
      <div
        :class="['absolute top-1/2 right-4 -translate-y-1/2 pointer-events-none',
          isDark ? 'text-gray-600' : 'text-gray-400'
        ]"
        :style="{ opacity: dragOpacity }"
      >
        <ChevronLeftIcon :size="32" />
      </div>

      <div class="p-8 pt-20">
        <div
          class="mb-12"
        >
          <h2
            :class="['text-3xl font-bold', isDark ? 'text-white' : 'text-gray-900']"
          >
            导航菜单
          </h2>
          <div
            :class="['h-1 mt-2 rounded', isDark ? 'bg-blue-500' : 'bg-blue-600']"
            :style="{ width: isOpen ? '80px' : '0', transition: 'width 0.6s ease-out' }"
          />
        </div>

        <ul class="space-y-4">
          <li v-for="(item, i) in menuItems" :key="item.label">
            <a
              :href="item.href"
              @click="closeMenu"
              :class="['flex items-center space-x-4 p-4 rounded-lg transition-all group',
                isDark ? 'hover:bg-gray-700 text-gray-200' : 'hover:bg-gray-100 text-gray-800'
              ]"
              :style="{
                opacity: isOpen ? 1 : 0,
                transform: isOpen ? 'translateX(0)' : 'translateX(-50px)',
                transition: `opacity 0.3s ${0.1 + i * 0.08}s, transform 0.3s ${0.1 + i * 0.08}s`
              }"
            >
              <div
                :class="['p-2 rounded-lg transition-all duration-300',
                  isDark ? 'bg-gray-700' : 'bg-gray-200',
                  'group-hover:bg-blue-500 group-hover:text-white'
                ]"
              >
                <component :is="item.icon" :size="24" />
              </div>
              <span class="text-lg font-medium">{{ item.label }}</span>
            </a>
          </li>
        </ul>

        <div
          :class="['absolute bottom-8 left-8 right-8 p-4 rounded-lg',
            isDark ? 'bg-gray-700' : 'bg-gray-100'
          ]"
          :style="{
            opacity: isOpen ? 1 : 0,
            transform: isOpen ? 'translateY(0)' : 'translateY(20px)',
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

    <!-- Main Content -->
    <main class="relative z-10 px-6 py-12 max-w-4xl mx-auto">
      <div
        :class="['p-8 rounded-2xl shadow-xl',
          isDark ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'
        ]"
        :style="{
          opacity: 1,
          transform: 'translateY(0)',
          transition: 'opacity 0.6s 0.4s, transform 0.6s 0.4s'
        }"
      >
        <h2 class="text-3xl font-bold mb-4">
          欢迎使用动画菜单
        </h2>
        <p :class="['text-lg mb-4', isDark ? 'text-gray-300' : 'text-gray-600']">
          点击左上角的菜单按钮打开动画导航菜单。使用右上角的主题按钮在亮色和暗色模式之间切换。
        </p>
        <p :class="['text-lg', isDark ? 'text-gray-300' : 'text-gray-600']">
          背景采用正交网格图案，可根据当前主题自适应。您也可以向左拖动菜单来关闭它！
        </p>
      </div>

      <div
        :class="['mt-8 p-8 rounded-2xl shadow-xl',
          isDark ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'
        ]"
        :style="{
          opacity: 1,
          transform: 'translateY(0)',
          transition: 'opacity 0.6s 0.6s, transform 0.6s 0.6s'
        }"
      >
        <h3 class="text-2xl font-bold mb-4">功能特性</h3>
        <ul :class="['space-y-2', isDark ? 'text-gray-300' : 'text-gray-600']">
          <li>• 电影级弹簧动画效果</li>
          <li>• 拖动关闭功能</li>
          <li>• 交错式菜单项动画</li>
          <li>• 带旋转动画的关闭按钮</li>
          <li>• 响应式设计，适配所有屏幕尺寸</li>
          <li>• 亮色和暗色模式支持</li>
          <li>• 正交网格背景</li>
          <li>• 交互式悬停效果</li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  Menu as MenuIcon,
  X as XIcon,
  Home as HomeIcon,
  User as UserIcon,
  Briefcase as BriefcaseIcon,
  Mail as MailIcon,
  Sun as SunIcon,
  Moon as MoonIcon,
  ChevronLeft as ChevronLeftIcon
} from 'lucide-vue-next'

const isOpen = ref(false)
const isDark = ref(false)
const isDragging = ref(false)
const startX = ref(0)
const currentX = ref(0)
const menuRef = ref<HTMLElement | null>(null)

const menuItems = [
  { icon: HomeIcon, label: '首页', href: '#home' },
  { icon: UserIcon, label: '关于', href: '#about' },
  { icon: BriefcaseIcon, label: '服务', href: '#services' },
  { icon: MailIcon, label: '联系', href: '#contact' },
]

const dragOpacity = computed(() => {
  const offset = currentX.value
  return Math.max(0, Math.min(1, (offset + 200) / 200))
})

const toggleMenu = () => {
  isOpen.value = !isOpen.value
}

const closeMenu = () => {
  isOpen.value = false
}

const toggleTheme = () => {
  isDark.value = !isDark.value
}

const startDrag = (e: MouseEvent | TouchEvent) => {
  isDragging.value = true
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
  startX.value = clientX
  currentX.value = 0
}

const handleDrag = (e: MouseEvent | TouchEvent) => {
  if (!isDragging.value || !isOpen.value) return
  
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
  if (e.key === 'Escape' && isOpen.value) {
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

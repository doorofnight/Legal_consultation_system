<template>
  <div class="background-paths-container">
    <div class="absolute inset-0 pointer-events-none">
      <svg
        class="w-full h-full text-slate-950"
        viewBox="0 0 696 316"
        fill="none"
      >
        <title>Background Paths</title>
        <path
          v-for="path in paths"
          :key="path.id"
          :d="path.d"
          stroke="currentColor"
          :stroke-width="path.width"
          :stroke-opacity="path.opacity"
          class="animated-path"
        />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Path {
  id: number
  d: string
  width: number
  opacity: number
}

const paths = ref<Path[]>([])
const animationFrame = ref<number | null>(null)
const time = ref(0)

// 生成路径数据
const generatePaths = (position: number): Path[] => {
  return Array.from({ length: 36 }, (_, i) => ({
    id: i,
    d: `M-${380 - i * 5 * position} -${189 + i * 6}C-${
      380 - i * 5 * position
    } -${189 + i * 6} -${312 - i * 5 * position} ${216 - i * 6} ${
      152 - i * 5 * position
    } ${343 - i * 6}C${616 - i * 5 * position} ${470 - i * 6} ${
      684 - i * 5 * position
    } ${875 - i * 6} ${684 - i * 5 * position} ${875 - i * 6}`,
    width: 0.5 + i * 0.03,
    opacity: 0.1 + i * 0.03
  }))
}

// 动画循环
const animate = () => {
  time.value += 0.01
  
  // 更新路径的 stroke-dasharray 和 stroke-dashoffset 来创建动画效果
  const pathsElements = document.querySelectorAll('.animated-path')
  pathsElements.forEach((path, index) => {
    const element = path as SVGPathElement
    const length = element.getTotalLength()
    const offset = Math.sin(time.value + index * 0.1) * length
    
    element.style.strokeDasharray = `${length} ${length}`
    element.style.strokeDashoffset = `${offset}`
  })
  
  animationFrame.value = requestAnimationFrame(animate)
}

onMounted(() => {
  // 生成两组路径
  const paths1 = generatePaths(1)
  const paths2 = generatePaths(-1)
  paths.value = [...paths1, ...paths2]
  
  // 开始动画
  animate()
})

onUnmounted(() => {
  if (animationFrame.value) {
    cancelAnimationFrame(animationFrame.value)
  }
})
</script>

<style scoped>
.background-paths-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
}

.animated-path {
  transition: stroke-dashoffset 0.3s ease;
}
</style>
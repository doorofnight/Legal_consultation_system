<template>
  <button
    :style="buttonStyles"
    :class="buttonClasses"
    @click="$emit('click', $event)"
  >
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/utils/cn'

const props = defineProps<{
  glowColor?: string
  className?: string
}>()

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

function hexToRgba(hex: string, alpha: number = 1): string {
  let hexValue = hex.replace("#", "")

  if (hexValue.length === 3) {
    hexValue = hexValue
      .split("")
      .map((char) => char + char)
      .join("")
  }

  const r = parseInt(hexValue.substring(0, 2), 16)
  const g = parseInt(hexValue.substring(2, 4), 16)
  const b = parseInt(hexValue.substring(4, 6), 16)

  if (isNaN(r) || isNaN(g) || isNaN(b)) {
    console.error("Invalid hex color:", hex)
    return "rgba(0, 0, 0, 1)"
  }

  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

const glowColorRgba = computed(() => hexToRgba(props.glowColor || "#a3e635"))
const glowColorVia = computed(() => hexToRgba(props.glowColor || "#a3e635", 0.075))
const glowColorTo = computed(() => hexToRgba(props.glowColor || "#a3e635", 0.2))

const buttonStyles = computed(() => ({
  '--glow-color': glowColorRgba.value,
  '--glow-color-via': glowColorVia.value,
  '--glow-color-to': glowColorTo.value,
}))

const buttonClasses = computed(() => cn(
  "glowing-button",
  props.className
))
</script>

<style scoped>
.glowing-button {
  min-width: min-content;
  height: 2.5rem;
  padding-left: 1.25rem !important;
  padding-right: 1.25rem !important;
  font-size: 0.875rem;
  line-height: 1.25rem;
  border-radius: 0.375rem;
  border: 1px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke, transform;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
  overflow: hidden;
  background-color: #ffffff;
  border-right: 0;
  transition-duration: 200ms;
  white-space: nowrap;
  color: #111827;
  border-color: #e5e7eb;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.glowing-button:hover {
  background-color: #f3f4f6;
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.glowing-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.glowing-button::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(to right, 
    transparent 0%, 
    transparent 40%, 
    var(--glow-color-via) 70%, 
    var(--glow-color-to) 100%);
  box-shadow: inset 0 1px 0 0 hsla(var(--foreground, 0, 0%, 0%) / 0.15);
  z-index: 20;
}

.glowing-button::before {
  content: '';
  position: absolute;
  width: 5px;
  height: 60%;
  background: var(--glow-color);
  right: 0;
  border-top-left-radius: 0.25rem;
  border-bottom-left-radius: 0.25rem;
  box-shadow: -2px 0 10px var(--glow-color);
  z-index: 10;
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

.glowing-button:hover::before {
  transform: translateX(100%);
}
</style>
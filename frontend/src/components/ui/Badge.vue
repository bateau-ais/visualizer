<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'default'
  size?: 'sm' | 'md' | 'lg'
  dot?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  dot: false
})

const classes = computed(() => {
  const base = 'inline-flex items-center font-medium rounded-full'
  
  const variants = {
    success: 'bg-vessel-normal/20 text-vessel-normal border border-vessel-normal/30',
    warning: 'bg-vessel-warning/20 text-vessel-warning border border-vessel-warning/30',
    danger: 'bg-vessel-danger/20 text-vessel-danger border border-vessel-danger/30',
    info: 'bg-accent-primary/20 text-accent-primary border border-accent-primary/30',
    default: 'bg-bg-tertiary text-text-secondary border border-gray-700'
  }
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  }
  
  return [base, variants[props.variant], sizes[props.size]].join(' ')
})

const dotColor = computed(() => {
  const colors = {
    success: 'bg-vessel-normal',
    warning: 'bg-vessel-warning',
    danger: 'bg-vessel-danger',
    info: 'bg-accent-primary',
    default: 'bg-gray-500'
  }
  return colors[props.variant]
})
</script>

<template>
  <span :class="classes">
    <span
      v-if="dot"
      :class="[dotColor, 'w-2 h-2 rounded-full mr-1.5']"
    />
    <slot />
  </span>
</template>

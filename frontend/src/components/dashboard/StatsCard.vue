<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value: number
  label: string
  trend?: number
  icon?: any
  variant?: 'default' | 'success' | 'warning' | 'danger'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default'
})

const trendColor = computed(() => {
  if (!props.trend) return ''
  return props.trend > 0 ? 'text-accent-success' : 'text-accent-danger'
})

const variantColors = computed(() => {
  const colors = {
    default: 'border-gray-700',
    success: 'border-vessel-normal/30 bg-vessel-normal/5',
    warning: 'border-vessel-warning/30 bg-vessel-warning/5',
    danger: 'border-vessel-danger/30 bg-vessel-danger/5'
  }
  return colors[props.variant]
})
</script>

<template>
  <div :class="['glass rounded-lg p-6 border', variantColors]">
    <div class="flex items-start justify-between">
      <div class="flex-1">
        <p class="text-sm text-text-muted mb-1">{{ label }}</p>
        <p class="text-3xl font-bold text-text-primary">
          {{ value.toLocaleString() }}
        </p>
        
        <div v-if="trend !== undefined && value > 0" class="mt-2 flex items-center space-x-1">
          <span :class="['text-sm font-medium', trendColor]">
            {{ trend > 0 ? '+' : '' }}{{ trend.toFixed(1) }}%
          </span>
          <span class="text-xs text-text-muted">vs yesterday</span>
        </div>
      </div>
      
      <div v-if="icon" class="p-3 rounded-lg bg-bg-tertiary">
        <component :is="icon" class="w-6 h-6 text-accent-primary" />
      </div>
    </div>
  </div>
</template>

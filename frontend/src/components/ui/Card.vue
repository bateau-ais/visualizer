<script setup lang="ts">
interface Props {
  title?: string
  variant?: 'default' | 'glass'
  padding?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'default',
  padding: true
})
</script>

<template>
  <div 
    :class="[
      'rounded-lg shadow-lg',
      variant === 'glass' ? 'glass' : 'bg-bg-secondary border border-gray-700',
      padding ? 'p-6' : ''
    ]"
  >
    <div v-if="title" class="mb-4">
      <h3 class="text-lg font-semibold text-text-primary">{{ title }}</h3>
    </div>
    <slot />
  </div>
</template>

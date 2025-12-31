<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string | number
  type?: 'text' | 'number' | 'search'
  placeholder?: string
  disabled?: boolean
  error?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const inputClasses = computed(() => {
  const base = 'w-full px-3 py-2 bg-bg-tertiary border rounded-lg text-text-primary placeholder-text-muted transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-bg-primary'
  
  const state = props.error
    ? 'border-accent-danger focus:ring-accent-danger'
    : 'border-gray-700 focus:ring-accent-primary'
  
  const disabled = props.disabled ? 'opacity-50 cursor-not-allowed' : ''
  
  return [base, state, disabled].join(' ')
})
</script>

<template>
  <div class="space-y-1">
    <input
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="inputClasses"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <p v-if="error" class="text-sm text-accent-danger">
      {{ error }}
    </p>
  </div>
</template>

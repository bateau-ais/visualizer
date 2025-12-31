<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronDown } from 'lucide-vue-next'

interface Option {
  value: string | number
  label: string
}

interface Props {
  modelValue: string | number
  options: Option[]
  placeholder?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Select an option',
  disabled: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

const isOpen = ref(false)

const selectedLabel = computed(() => {
  const selected = props.options.find(opt => opt.value === props.modelValue)
  return selected?.label || props.placeholder
})

function selectOption(value: string | number) {
  emit('update:modelValue', value)
  isOpen.value = false
}
</script>

<template>
  <div class="relative">
    <button
      type="button"
      :disabled="disabled"
      :class="[
        'w-full px-3 py-2 bg-bg-tertiary border border-gray-700 rounded-lg text-text-primary text-left flex items-center justify-between transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-accent-primary focus:ring-offset-2 focus:ring-offset-bg-primary',
        disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-bg-tertiary/80'
      ]"
      @click="isOpen = !isOpen"
    >
      <span :class="modelValue ? 'text-text-primary' : 'text-text-muted'">
        {{ selectedLabel }}
      </span>
      <ChevronDown :class="['w-4 h-4 transition-transform', isOpen ? 'rotate-180' : '']" />
    </button>
    
    <div
      v-if="isOpen"
      class="absolute z-50 w-full mt-1 bg-bg-tertiary border border-gray-700 rounded-lg shadow-lg max-h-60 overflow-auto"
    >
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        :class="[
          'w-full px-3 py-2 text-left hover:bg-bg-primary transition-colors',
          option.value === modelValue ? 'bg-bg-primary text-accent-primary' : 'text-text-primary'
        ]"
        @click="selectOption(option.value)"
      >
        {{ option.label }}
      </button>
    </div>
    
    <!-- Backdrop to close dropdown -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-40"
      @click="isOpen = false"
    />
  </div>
</template>

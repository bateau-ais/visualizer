<script setup lang="ts">
import { ref } from 'vue'
import { Filter, X } from 'lucide-vue-next'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'

interface Props {
  open?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  open: false
})

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

// Vessel type filters
const vesselTypes = ref({
  cargo: true,
  tanker: true,
  passenger: false,
  fishing: false
})

// Status filters
const statuses = ref({
  normal: true,
  anomaly: true,
  critical: false
})

// Speed range
const speedRange = ref([0, 50])

function resetFilters() {
  vesselTypes.value = {
    cargo: true,
    tanker: true,
    passenger: true,
    fishing: true
  }
  statuses.value = {
    normal: true,
    anomaly: true,
    critical: true
  }
  speedRange.value = [0, 50]
}
</script>

<template>
  <div
    :class="[
      'fixed top-16 left-0 h-[calc(100vh-4rem)] bg-bg-secondary border-r border-gray-700 transition-transform duration-300 z-40',
      open ? 'translate-x-0' : '-translate-x-full',
      'w-80'
    ]"
  >
    <div class="h-full flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-gray-700 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <Filter class="w-5 h-5 text-accent-primary" />
          <h2 class="text-lg font-semibold text-text-primary">Filters</h2>
        </div>
        <button
          class="p-1 hover:bg-bg-tertiary rounded transition-colors"
          @click="emit('update:open', false)"
        >
          <X class="w-5 h-5 text-text-secondary" />
        </button>
      </div>
      
      <!-- Filters content -->
      <div class="flex-1 overflow-y-auto p-4 space-y-6">
        <!-- Vessel Type -->
        <div>
          <h3 class="text-sm font-semibold text-text-primary mb-3">Vessel Type</h3>
          <div class="space-y-2">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input
                v-model="vesselTypes.cargo"
                type="checkbox"
                class="rounded border-gray-600 bg-bg-tertiary text-accent-primary focus:ring-accent-primary focus:ring-offset-bg-primary"
              />
              <span class="text-sm text-text-secondary">Cargo</span>
            </label>
            <label class="flex items-center space-x-2 cursor-pointer">
              <input
                v-model="vesselTypes.tanker"
                type="checkbox"
                class="rounded border-gray-600 bg-bg-tertiary text-accent-primary focus:ring-accent-primary focus:ring-offset-bg-primary"
              />
              <span class="text-sm text-text-secondary">Tanker</span>
            </label>
            <label class="flex items-center space-x-2 cursor-pointer">
              <input
                v-model="vesselTypes.passenger"
                type="checkbox"
                class="rounded border-gray-600 bg-bg-tertiary text-accent-primary focus:ring-accent-primary focus:ring-offset-bg-primary"
              />
              <span class="text-sm text-text-secondary">Passenger</span>
            </label>
            <label class="flex items-center space-x-2 cursor-pointer">
              <input
                v-model="vesselTypes.fishing"
                type="checkbox"
                class="rounded border-gray-600 bg-bg-tertiary text-accent-primary focus:ring-accent-primary focus:ring-offset-bg-primary"
              />
              <span class="text-sm text-text-secondary">Fishing</span>
            </label>
          </div>
        </div>
        
        <!-- Status -->
        <div>
          <h3 class="text-sm font-semibold text-text-primary mb-3">Status</h3>
          <div class="space-y-2">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input
                v-model="statuses.normal"
                type="checkbox"
                class="rounded border-gray-600 bg-bg-tertiary text-vessel-normal focus:ring-vessel-normal focus:ring-offset-bg-primary"
              />
              <span class="text-sm text-text-secondary">Normal</span>
            </label>
            <label class="flex items-center space-x-2 cursor-pointer">
              <input
                v-model="statuses.anomaly"
                type="checkbox"
                class="rounded border-gray-600 bg-bg-tertiary text-vessel-warning focus:ring-vessel-warning focus:ring-offset-bg-primary"
              />
              <span class="text-sm text-text-secondary">Anomaly</span>
            </label>
            <label class="flex items-center space-x-2 cursor-pointer">
              <input
                v-model="statuses.critical"
                type="checkbox"
                class="rounded border-gray-600 bg-bg-tertiary text-vessel-danger focus:ring-vessel-danger focus:ring-offset-bg-primary"
              />
              <span class="text-sm text-text-secondary">Critical</span>
            </label>
          </div>
        </div>
        
        <!-- Speed Range -->
        <div>
          <h3 class="text-sm font-semibold text-text-primary mb-3">Speed Range</h3>
          <div class="space-y-2">
            <input
              v-model.number="speedRange[1]"
              type="range"
              min="0"
              max="50"
              class="w-full accent-accent-primary"
            />
            <div class="flex justify-between text-xs text-text-muted">
              <span>0 kt</span>
              <span class="text-accent-primary font-semibold">{{ speedRange[1] }} kt</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Footer -->
      <div class="p-4 border-t border-gray-700 space-y-2">
        <Button variant="primary" class="w-full">
          Apply Filters
        </Button>
        <Button variant="ghost" class="w-full" @click="resetFilters">
          Reset
        </Button>
      </div>
    </div>
  </div>
  
  <!-- Backdrop -->
  <div
    v-if="open"
    class="fixed inset-0 bg-black/50 z-30 lg:hidden"
    @click="emit('update:open', false)"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Badge from './Badge.vue'
import { AlertTriangle, TrendingUp, Navigation, Radio, MapPin, Wifi } from 'lucide-vue-next'

interface Props {
  reasons: string[]
  linkToDetails?: boolean
  maxDisplay?: number
}

const props = withDefaults(defineProps<Props>(), {
  linkToDetails: false,
  maxDisplay: 99
})

// Map anomaly types to colors and icons
const anomalyConfig: Record<string, { color: string, icon: any, label: string }> = {
  'speed': { color: 'warning', icon: TrendingUp, label: 'Speed Anomaly' },
  'course': { color: 'warning', icon: Navigation, label: 'Course Anomaly' },
  'heading': { color: 'warning', icon: Navigation, label: 'Heading Anomaly' },
  'spoofing': { color: 'danger', icon: AlertTriangle, label: 'Spoofing Suspected' },
  'position': { color: 'danger', icon: MapPin, label: 'Position Anomaly' },
  'communication': { color: 'warning', icon: Wifi, label: 'Communication Gap' },
  'zone': { color: 'danger', icon: Radio, label: 'Zone Violation' }
}

function getAnomalyConfig(reason: string) {
  const reasonLower = reason.toLowerCase()
  
  for (const [key, config] of Object.entries(anomalyConfig)) {
    if (reasonLower.includes(key)) {
      return config
    }
  }
  
  return { color: 'warning', icon: AlertTriangle, label: reason }
}

const displayedReasons = computed(() => {
  return props.reasons.slice(0, props.maxDisplay)
})

const remainingCount = computed(() => {
  return Math.max(0, props.reasons.length - props.maxDisplay)
})
</script>

<template>
  <div class="flex flex-wrap gap-2 items-center">
    <Badge 
      v-for="(reason, index) in displayedReasons" 
      :key="index"
      :variant="getAnomalyConfig(reason).color as any"
      size="sm"
    >
      <component :is="getAnomalyConfig(reason).icon" class="w-3 h-3 mr-1" />
      {{ getAnomalyConfig(reason).label }}
    </Badge>
    
    <Badge v-if="remainingCount > 0" variant="default" size="sm">
      +{{ remainingCount }} more
    </Badge>
    
    <a 
      v-if="linkToDetails" 
      href="/docs/anomalies"
      class="text-xs text-accent-primary hover:underline ml-1"
      target="_blank"
    >
      Learn more →
    </a>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Vessel } from '@/types/vessel'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import { Navigation, Gauge, Ship, ExternalLink } from 'lucide-vue-next'
import { formatCoordinates, formatSpeed, formatCourse, getCardinalDirection } from '@/utils/format'

interface Props {
  vessel: Vessel
}

const props = defineProps<Props>()
const router = useRouter()

const badgeVariant = computed(() => {
  if (!props.vessel.is_anomaly) return 'success'
  if (props.vessel.anomaly_score >= 0.8) return 'danger'
  return 'warning'
})

function viewDetails() {
  router.push(`/vessel/${props.vessel.mmsi}`)
}
</script>

<template>
  <div class="w-80 max-w-sm">
    <!-- Header -->
    <div class="mb-3">
      <div class="flex items-start justify-between mb-2">
        <div class="flex-1">
          <h3 class="text-lg font-bold text-text-primary">
            {{ vessel.name || 'Unknown Vessel' }}
          </h3>
          <p class="text-xs text-text-muted">MMSI: {{ vessel.mmsi }}</p>
        </div>
        <Ship class="w-5 h-5 text-accent-primary flex-shrink-0 ml-2" />
      </div>
      
      <Badge :variant="badgeVariant" dot size="sm">
        {{ vessel.is_anomaly ? `Anomaly (${(vessel.anomaly_score * 100).toFixed(0)}%)` : 'Normal' }}
      </Badge>
    </div>
    
    <!-- Info Grid -->
    <div class="space-y-2 mb-4">
      <div class="flex items-start space-x-2">
        <Navigation class="w-4 h-4 text-accent-primary mt-0.5 flex-shrink-0" />
        <div class="flex-1 min-w-0">
          <p class="text-xs text-text-muted">Position</p>
          <p class="text-sm text-text-primary font-mono">
            {{ formatCoordinates(vessel.lat, vessel.lon) }}
          </p>
        </div>
      </div>
      
      <div class="grid grid-cols-2 gap-2">
        <div class="flex items-start space-x-2">
          <Gauge class="w-4 h-4 text-accent-primary mt-0.5 flex-shrink-0" />
          <div>
            <p class="text-xs text-text-muted">Speed</p>
            <p class="text-sm text-text-primary font-semibold">
              {{ formatSpeed(vessel.sog) }}
            </p>
          </div>
        </div>
        
        <div class="flex items-start space-x-2">
          <Navigation class="w-4 h-4 text-accent-primary mt-0.5 flex-shrink-0" />
          <div>
            <p class="text-xs text-text-muted">Course</p>
            <p class="text-sm text-text-primary font-semibold">
              {{ formatCourse(vessel.cog) }} {{ getCardinalDirection(vessel.cog) }}
            </p>
          </div>
        </div>
      </div>
      
      <div v-if="vessel.type" class="flex items-center space-x-2">
        <span class="text-xs text-text-muted">Type:</span>
        <span class="text-sm text-text-primary capitalize">{{ vessel.type }}</span>
      </div>
    </div>
    
    <!-- Actions -->
    <div class="flex space-x-2">
      <Button variant="primary" size="sm" class="flex-1" @click="viewDetails">
        <ExternalLink class="w-3 h-3 mr-1" />
        View Details
      </Button>
    </div>
  </div>
</template>

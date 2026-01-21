<script setup lang="ts">
import { ref, computed } from 'vue'
import { useVesselsStore } from '@/stores/vessels'
import type { Vessel } from '@/types/vessel'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import AnomalyReasons from '@/components/ui/AnomalyReasons.vue'
import { Navigation, Gauge, Ship, ExternalLink, CheckCircle } from 'lucide-vue-next'
import { formatCoordinates, formatSpeed, formatCourse, getCardinalDirection } from '@/utils/format'

interface Props {
  vessel: Vessel
  onNavigate?: (mmsi: number) => void
}

const props = defineProps<Props>()
const vesselsStore = useVesselsStore()
const acknowledging = ref(false)

const badgeVariant = computed(() => {
  if (!props.vessel.is_anomaly) return 'success'
  if (props.vessel.anomaly_score >= 0.8) return 'danger'
  return 'warning'
})

const showPulsing = computed(() => {
  return props.vessel.is_anomaly && !props.vessel.acknowledged
})

function viewDetails() {
  if (props.onNavigate) {
    props.onNavigate(props.vessel.mmsi)
  } else {
    window.location.href = `/vessel/${props.vessel.mmsi}`
  }
}

const vesselDetails = ref<any>(null)
const anomalyReason = computed(() => {
    if (!vesselDetails.value?.anomalies?.length) return null
    // Get the most recent high score anomaly reason
    const anomaly = vesselDetails.value.anomalies[0]
    return anomaly.reasons && anomaly.reasons.length > 0 ? anomaly.reasons[0] : 'Unknown Anomaly'
})

import { onMounted } from 'vue'

onMounted(async () => {
    if (props.vessel.is_anomaly) {
        try {
            vesselDetails.value = await vesselsStore.fetchVesselDetails(props.vessel.mmsi)
        } catch (e) {
            console.error(e)
        }
    }
})

async function acknowledge() {
  acknowledging.value = true
  try {
    await vesselsStore.acknowledgeVessel(props.vessel.mmsi)
  } finally {
    acknowledging.value = false
  }
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
      
      <div class="flex items-center gap-2">
        <Badge :variant="badgeVariant" :dot="showPulsing" size="sm">
          <span v-if="vessel.is_anomaly">
           {{ anomalyReason || 'Anomaly Detected' }}
          </span>
          <span v-else>Normal</span>
        </Badge>
        <Badge v-if="vessel.acknowledged" variant="success" size="sm">
          <CheckCircle class="w-3 h-3 mr-1" />
          Acknowledged
        </Badge>
      </div>
    </div>
    
    <!-- Info Grid -->
    <div class="space-y-2 mb-4">
      <!-- Anomaly Details (if anomaly detected) -->
      <div v-if="vessel.is_anomaly && vesselDetails?.anomalies?.length" class="p-3 bg-bg-tertiary rounded-lg border border-accent-warning/20">
        <p class="text-xs font-semibold text-text-muted mb-2">Detected Anomalies:</p>
        <AnomalyReasons 
          :reasons="vesselDetails.anomalies[0].reasons" 
          :linkToDetails="true"
          :maxDisplay="3"
        />
      </div>
      
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
    <div class="flex gap-2">
      <Button 
        v-if="vessel.is_anomaly && !vessel.acknowledged" 
        variant="secondary" 
        size="sm" 
        class="flex-1"
        :loading="acknowledging"
        @click="acknowledge"
      >
        <CheckCircle class="w-3 h-3 mr-1" />
        Acknowledge
      </Button>
      <Button variant="primary" size="sm" :class="vessel.is_anomaly && !vessel.acknowledged ? 'flex-1' : 'w-full'" @click="viewDetails">
        <ExternalLink class="w-3 h-3 mr-1" />
        View Details
      </Button>
    </div>
  </div>
</template>

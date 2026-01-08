<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useVesselsStore } from '@/stores/vessels'
import { useMap } from '@/composables/useMap'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import { Ship, Navigation, Gauge, Clock, AlertTriangle, MapPin, CheckCircle } from 'lucide-vue-next'
import { formatCoordinates, formatSpeed, formatCourse, formatRelativeTime, formatDateTime } from '@/utils/format'
import L from 'leaflet'

const route = useRoute()
const vesselsStore = useVesselsStore()
const mmsi = ref<number>(parseInt(route.params.mmsi as string))
const loading = ref(true)
const acknowledging = ref(false)

// Map for trajectory
const { map: trajectoryMap, initMap: initTrajectoryMap } = useMap('trajectory-map')

onMounted(async () => {
  try {
    await vesselsStore.fetchVesselDetails(mmsi.value)
    
    // Initialize trajectory map
    if (vessel.value && vessel.value.trajectory && vessel.value.trajectory.length > 0) {
      setTimeout(() => {
        initTrajectoryMap([vessel.value!.lat, vessel.value!.lon], 10)
        renderTrajectory()
      }, 100)
    }
  } finally {
    loading.value = false
  }
})

const vessel = computed(() => vesselsStore.selectedVessel)

const badgeVariant = computed(() => {
  if (!vessel.value?.is_anomaly) return 'success'
  if (vessel.value.anomaly_score >= 0.8) return 'danger'
  return 'warning'
})

function renderTrajectory() {
  if (!trajectoryMap.value || !vessel.value?.trajectory) return
  
  const trajectory = vessel.value.trajectory
  const latLngs = trajectory.map(p => [p.lat, p.lon] as [number, number])
  
  // Draw trajectory line
  L.polyline(latLngs, {
    color: '#00d4ff',
    weight: 3,
    opacity: 0.7
  }).addTo(trajectoryMap.value)
  
  // Add start marker (oldest position)
  L.circleMarker(latLngs[0], {
    radius: 8,
    fillColor: '#10b981',
    color: '#fff',
    weight: 2,
    fillOpacity: 0.8
  }).bindPopup('Start').addTo(trajectoryMap.value)
  
  // Add end marker (current position)
  L.circleMarker(latLngs[latLngs.length - 1], {
    radius: 10,
    fillColor: '#ef4444',
    color: '#fff',
    weight: 2,
    fillOpacity: 1
  }).bindPopup('Current').addTo(trajectoryMap.value)
  
  // Fit bounds
  trajectoryMap.value.fitBounds(latLngs, { padding: [50, 50] })
}

// Speed/Course chart options
const speedChartOptions = computed(() => {
  if (!vessel.value?.trajectory) return {}
  
  const trajectory = vessel.value.trajectory
  const times = trajectory.map(p => formatDateTime(p.timestamp).split(' ')[1])
  const speeds = trajectory.map(p => p.sog)
  
  return {
    darkMode: true,
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e293b',
      borderColor: '#374151',
      textStyle: { color: '#f1f5f9' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: times,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#94a3b8', rotate: 45 }
    },
    yAxis: {
      type: 'value',
      name: 'Speed (kt)',
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#94a3b8' },
      nameTextStyle: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#374151', type: 'dashed' } }
    },
    series: [{
      data: speeds,
      type: 'line',
      smooth: true,
      itemStyle: { color: '#00d4ff' },
      lineStyle: { width: 2 },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0)' }
          ]
        }
      }
    }]
  }
})

const courseChartOptions = computed(() => {
  if (!vessel.value?.trajectory) return {}
  
  const trajectory = vessel.value.trajectory
  const times = trajectory.map(p => formatDateTime(p.timestamp).split(' ')[1])
  const courses = trajectory.map(p => p.cog)
  
  return {
    darkMode: true,
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e293b',
      borderColor: '#374151',
      textStyle: { color: '#f1f5f9' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: times,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#94a3b8', rotate: 45 }
    },
    yAxis: {
      type: 'value',
      name: 'Course (°)',
      min: 0,
      max: 360,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#94a3b8' },
      nameTextStyle: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#374151', type: 'dashed' } }
    },
    series: [{
      data: courses,
      type: 'line',
      smooth: true,
      itemStyle: { color: '#f59e0b' },
      lineStyle: { width: 2 }
    }]
  }
})

async function acknowledge() {
  acknowledging.value = true
  try {
    await vesselsStore.acknowledgeVessel(mmsi.value)
  } finally {
    acknowledging.value = false
  }
}
</script>

<template>
  <div class="p-6 space-y-6">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="text-center">
        <Ship class="w-12 h-12 text-accent-primary mx-auto mb-3 animate-pulse" />
        <p class="text-text-secondary">Loading vessel data...</p>
      </div>
    </div>
    
    <!-- Content -->
    <template v-else-if="vessel">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-3xl font-bold text-text-primary mb-2">
            {{ vessel.name || 'Unknown Vessel' }}
          </h1>
          <div class="flex items-center gap-4 text-text-secondary">
            <span>MMSI: {{ vessel.mmsi }}</span>
            <span v-if="vessel.imo">IMO: {{ vessel.imo }}</span>
            <Badge :variant="badgeVariant" dot>
              {{ vessel.is_anomaly ? 'Anomaly Detected' : 'Normal' }}
            </Badge>
            <Badge v-if="vessel.acknowledged" variant="success">
              <CheckCircle class="w-3 h-3 mr-1" />
              Acknowledged
            </Badge>
          </div>
        </div>
        
        <div class="flex gap-2">
          <Button 
            v-if="vessel.is_anomaly && !vessel.acknowledged"
            variant="secondary"
            :loading="acknowledging"
            @click="acknowledge"
          >
            <CheckCircle class="w-4 h-4 mr-2" />
            Acknowledge Anomaly
          </Button>
          <div v-if="vessel.photo_url" class="w-48 h-32 rounded-lg overflow-hidden border border-gray-700">
            <img :src="vessel.photo_url" :alt="vessel.name || 'Vessel'" class="w-full h-full object-cover" />
          </div>
        </div>
      </div>
      
      <!-- Current Position Info -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <div class="flex items-start space-x-3">
            <Navigation class="w-5 h-5 text-accent-primary mt-0.5" />
            <div class="flex-1">
              <p class="text-xs text-text-muted mb-1">Position</p>
              <p class="text-sm font-medium text-text-primary">
                {{ formatCoordinates(vessel.lat, vessel.lon) }}
              </p>
            </div>
          </div>
        </Card>
        
        <Card>
          <div class="flex items-start space-x-3">
            <Gauge class="w-5 h-5 text-accent-primary mt-0.5" />
            <div class="flex-1">
              <p class="text-xs text-text-muted mb-1">Speed</p>
              <p class="text-sm font-medium text-text-primary">
                {{ formatSpeed(vessel.sog) }}
              </p>
            </div>
          </div>
        </Card>
        
        <Card>
          <div class="flex items-start space-x-3">
            <Navigation class="w-5 h-5 text-accent-primary mt-0.5" />
            <div class="flex-1">
              <p class="text-xs text-text-muted mb-1">Course</p>
              <p class="text-sm font-medium text-text-primary">
                {{ formatCourse(vessel.cog) }}
              </p>
            </div>
          </div>
        </Card>
        
        <Card>
          <div class="flex items-start space-x-3">
            <Clock class="w-5 h-5 text-accent-primary mt-0.5" />
            <div class="flex-1">
              <p class="text-xs text-text-muted mb-1">Last Update</p>
              <p class="text-sm font-medium text-text-primary">
                {{ formatRelativeTime(vessel.timestamp) }}
              </p>
            </div>
          </div>
        </Card>
      </div>
      
      <!-- Anomaly Alert -->
      <Card v-if="vessel.is_anomaly" variant="glass">
        <div class="flex items-start space-x-4">
          <AlertTriangle class="w-6 h-6 text-accent-danger flex-shrink-0" />
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-accent-danger mb-2">
              Anomaly Detected (Severity Score: {{ (vessel.anomaly_score * 100).toFixed(0) }}%)
            </h3>
            <p class="text-sm text-text-secondary mb-3">
              This vessel has been flagged for unusual behavior. Review the trajectory and speed history below for analysis.
            </p>
            <div class="flex flex-wrap gap-2">
              <Badge variant="warning">High Priority</Badge>
              <Badge variant="warning">Requires Investigation</Badge>
            </div>
          </div>
        </div>
      </Card>
      
      <!-- Trajectory Map -->
      <Card title="24-Hour Trajectory">
        <div class="h-96 relative">
          <div v-if="!vessel.trajectory || vessel.trajectory.length === 0" class="h-full flex items-center justify-center bg-bg-primary rounded-lg border border-gray-700">
            <div class="text-center">
              <MapPin class="w-12 h-12 text-accent-primary mx-auto mb-3" />
              <p class="text-text-secondary">No trajectory data available</p>
            </div>
          </div>
          <div v-else id="trajectory-map" class="h-full rounded-lg overflow-hidden border border-gray-700"></div>
        </div>
      </Card>
      
      <!-- Speed & Course History Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Speed History (24h)">
          <v-chart
            v-if="vessel.trajectory && vessel.trajectory.length > 0"
            :option="speedChartOptions"
            class="h-64"
            autoresize
          />
          <div v-else class="h-64 flex items-center justify-center">
            <p class="text-text-muted">No speed data available</p>
          </div>
        </Card>
        
        <Card title="Course History (24h)">
          <v-chart
            v-if="vessel.trajectory && vessel.trajectory.length > 0"
            :option="courseChartOptions"
            class="h-64"
            autoresize
          />
          <div v-else class="h-64 flex items-center justify-center">
            <p class="text-text-muted">No course data available</p>
          </div>
        </Card>
      </div>
      
      <!-- Vessel Details Table -->
      <Card title="Vessel Information">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex justify-between py-2 border-b border-gray-700">
            <span class="text-text-muted">MMSI</span>
            <span class="text-text-primary font-semibold">{{ vessel.mmsi }}</span>
          </div>
          <div v-if="vessel.imo" class="flex justify-between py-2 border-b border-gray-700">
            <span class="text-text-muted">IMO</span>
            <span class="text-text-primary font-semibold">{{ vessel.imo }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-700">
            <span class="text-text-muted">Type</span>
            <span class="text-text-primary font-semibold capitalize">{{ vessel.type }}</span>
          </div>
          <div v-if="vessel.flag" class="flex justify-between py-2 border-b border-gray-700">
            <span class="text-text-muted">Flag</span>
            <span class="text-text-primary font-semibold">{{ vessel.flag }}</span>
          </div>
          <div v-if="vessel.status" class="flex justify-between py-2 border-b border-gray-700">
            <span class="text-text-muted">Status</span>
            <span class="text-text-primary font-semibold capitalize">{{ vessel.status.replace('_', ' ') }}</span>
          </div>
          <div class="flex justify-between py-2 border-b border-gray-700">
            <span class="text-text-muted">Heading</span>
            <span class="text-text-primary font-semibold">{{ vessel.heading }}°</span>
          </div>
        </div>
      </Card>
    </template>
    
    <!-- Error State -->
    <Card v-else>
      <div class="text-center py-12">
        <AlertTriangle class="w-12 h-12 text-accent-danger mx-auto mb-3" />
        <p class="text-text-primary font-semibold mb-1">Vessel Not Found</p>
        <p class="text-text-secondary">No data available for MMSI {{ mmsi }}</p>
      </div>
    </Card>
  </div>
</template>

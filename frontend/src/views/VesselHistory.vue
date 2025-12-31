<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useVesselsStore } from '@/stores/vessels'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import { Ship, Navigation, Gauge, Clock, AlertTriangle } from 'lucide-vue-next'
import { formatCoordinates, formatSpeed, formatCourse, formatRelativeTime } from '@/utils/format'

const route = useRoute()
const vesselsStore = useVesselsStore()
const mmsi = ref<number>(parseInt(route.params.mmsi as string))
const loading = ref(true)

onMounted(async () => {
  try {
    await vesselsStore.fetchVesselDetails(mmsi.value)
  } finally {
    loading.value = false
  }
})

const vessel = ref(vesselsStore.selectedVessel)

// Mock chart data for speed/course
const speedChartOptions = ref({
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
    data: ['00h', '04h', '08h', '12h', '16h', '20h', '24h'],
    axisLine: { lineStyle: { color: '#374151' } },
    axisLabel: { color: '#94a3b8' }
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
    data: [10, 10.5, 11, 25, 12, 11.5, 12],
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
    },
    markPoint: {
      data: [{ type: 'max', name: 'Anomaly' }],
      itemStyle: { color: '#ef4444' }
    }
  }]
})
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
          <div class="flex items-center space-x-4 text-text-secondary">
            <span>MMSI: {{ vessel.mmsi }}</span>
            <span v-if="vessel.imo">IMO: {{ vessel.imo }}</span>
            <Badge :variant="vessel.is_anomaly ? 'danger' : 'success'" dot>
              {{ vessel.is_anomaly ? 'Anomaly Detected' : 'Normal' }}
            </Badge>
          </div>
        </div>
        
        <div v-if="vessel.photo_url" class="w-48 h-32 rounded-lg overflow-hidden border border-gray-700">
          <img :src="vessel.photo_url" :alt="vessel.name || 'Vessel'" class="w-full h-full object-cover" />
        </div>
      </div>
      
      <!-- Current Position -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <div class="flex items-start space-x-3">
            <Navigation class="w-5 h-5 text-accent-primary mt-0.5" />
            <div>
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
            <div>
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
            <div>
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
            <div>
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
              Anomaly Detected (Score: {{ (vessel.anomaly_score * 100).toFixed(0) }}%)
            </h3>
            <div class="space-y-1">
              <p class="text-sm text-text-secondary">Detected anomaly types:</p>
              <div class="flex flex-wrap gap-2 mt-2">
                <Badge variant="warning" v-for="(reason, i) in ['SPEED_SPIKE', 'IMPOSSIBLE_SPEED']" :key="i">
                  {{ reason }}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </Card>
      
      <!-- Speed History Chart -->
      <Card title="Speed History (24h)">
        <v-chart
          :option="speedChartOptions"
          class="h-64"
          autoresize
        />
      </Card>
      
      <!-- Trajectory Map Placeholder -->
      <Card title="Trajectory">
        <div class="h-96 bg-bg-primary rounded-lg border border-gray-700 flex items-center justify-center">
          <div class="text-center">
            <Navigation class="w-12 h-12 text-accent-primary mx-auto mb-3" />
            <p class="text-text-secondary">Trajectory map will be displayed here</p>
            <p class="text-text-muted text-sm mt-1">Last 24 hours of movement</p>
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

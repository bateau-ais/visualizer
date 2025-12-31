<script setup lang="ts">
import { ref, onMounted } from 'vue'
import LeafletMap from '@/components/map/LeafletMap.vue'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Select from '@/components/ui/Select.vue'
import { Flame, Download } from 'lucide-vue-next'
import api from '@/utils/api'

const resolution = ref(0.1)
const period = ref('24h')
const anomalyType = ref('all')
const loading = ref(false)
const heatmapData = ref<any>(null)

const resolutionOptions = [
  { value: 0.01, label: 'High (1 km / 0.01°)' },
  { value: 0.1, label: 'Medium (10 km / 0.1°)' },
  { value: 1, label: 'Low (100 km / 1°)' }
]

const periodOptions = [
  { value: '24h', label: 'Last 24 hours' },
  { value: '7d', label: 'Last 7 days' },
  { value: '30d', label: 'Last 30 days' }
]

const typeOptions = [
  { value: 'all', label: 'All types' },
  { value: 'SPEED_SPIKE', label: 'Speed anomalies' },
  { value: 'HEADING_CHANGE', label: 'Heading anomalies' },
  { value: 'SPOOFING', label: 'Spoofing detection' }
]

async function generateHeatmap() {
  loading.value = true
  try {
    const response = await api.get('/anomalies/heatmap', {
      params: {
        resolution: resolution.value,
        period: period.value,
        anomaly_type: anomalyType.value === 'all' ? null : anomalyType.value
      }
    })
    heatmapData.value = response.data
    console.log('Heatmap data:', heatmapData.value)
  } catch (error) {
    console.error('Error generating heatmap:', error)
  } finally {
    loading.value = false
  }
}

function exportData() {
  if (!heatmapData.value) return
  
  const csv = convertToCSV(heatmapData.value.cells)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `heatmap_${period.value}_${resolution.value}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

function convertToCSV(cells: any[]) {
  const headers = ['lat_min', 'lat_max', 'lon_min', 'lon_max', 'count', 'avg_score', 'top_types']
  const rows = cells.map(cell => [
    cell.lat_min,
    cell.lat_max,
    cell.lon_min,
    cell.lon_max,
    cell.count,
    cell.avg_score,
    cell.top_types.join(';')
  ])
  
  return [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')
}

onMounted(() => {
  generateHeatmap()
})
</script>

<template>
  <div class="p-6 space-y-6">
    <div>
      <h1 class="text-3xl font-bold text-text-primary mb-2">Anomaly Heatmap</h1>
      <p class="text-text-secondary">
        Visualize geographical distribution of anomalies
      </p>
    </div>
    
    <!-- Configuration Panel -->
    <Card title="Configuration">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-2">
            Grid Resolution
          </label>
          <Select
            v-model="resolution"
            :options="resolutionOptions"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-2">
            Time Period
          </label>
          <Select
            v-model="period"
            :options="periodOptions"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-text-secondary mb-2">
            Anomaly Type
          </label>
          <Select
            v-model="anomalyType"
            :options="typeOptions"
          />
        </div>
      </div>
      
      <div class="mt-4 flex space-x-3">
        <Button variant="primary" :loading="loading" @click="generateHeatmap">
          <Flame class="w-4 h-4 mr-2" />
          Generate Heatmap
        </Button>
        <Button variant="secondary" :disabled="!heatmapData" @click="exportData">
          <Download class="w-4 h-4 mr-2" />
          Export CSV
        </Button>
      </div>
    </Card>
    
    <!-- Heatmap Display -->
    <Card>
      <div class="h-[600px] relative">
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-bg-primary/50 z-10">
          <Flame class="w-12 h-12 text-accent-warning animate-pulse" />
        </div>
        
        <div v-else-if="!heatmapData || heatmapData.cells.length === 0" class="h-full flex items-center justify-center bg-bg-primary rounded-lg border border-gray-700">
          <div class="text-center">
            <Flame class="w-16 h-16 text-accent-warning mx-auto mb-4" />
            <h3 class="text-xl font-semibold text-text-primary mb-2">
              No Anomalies Found
            </h3>
            <p class="text-text-secondary">
              No anomalies detected for the selected period and filters
            </p>
          </div>
        </div>
        
        <div v-else class="h-full">
          <p class="text-center text-text-muted mb-2">
            Heatmap visualization: {{ heatmapData.cells.length }} cells with anomalies
          </p>
          <div class="h-[calc(100%-2rem)] bg-bg-primary rounded-lg border border-gray-700 flex items-center justify-center">
            <div class="text-center">
              <Flame class="w-12 h-12 text-accent-warning mx-auto mb-3" />
              <p class="text-text-secondary text-sm">
                Leaflet heatmap layer integration<br />
                will render {{ heatmapData.cells.length }} hotspot zones here
              </p>
            </div>
          </div>
        </div>
        
        <!-- Legend -->
        <div class="absolute bottom-4 right-4 glass rounded-lg px-6 py-3 border border-gray-700">
          <div class="flex items-center space-x-4">
            <span class="text-sm text-text-muted">Intensity:</span>
            <div class="flex items-center space-x-2">
              <div class="w-24 h-4 rounded" style="background: linear-gradient(90deg, #1e40af 0%, #fbbf24 50%, #ef4444 100%)"></div>
            </div>
            <div class="flex items-center space-x-4 text-xs text-text-muted">
              <span>Low</span>
              <span>High</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
    
    <!-- Stats -->
    <div v-if="heatmapData" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card>
        <div class="text-center">
          <p class="text-3xl font-bold text-accent-warning">{{ heatmapData.cells.length }}</p>
          <p class="text-sm text-text-muted mt-1">Hotspot Zones</p>
        </div>
      </Card>
      
      <Card>
        <div class="text-center">
          <p class="text-3xl font-bold text-accent-danger">
            {{ heatmapData.cells.filter((c: any) => c.count > 10).length }}
          </p>
          <p class="text-sm text-text-muted mt-1">High Density Areas</p>
        </div>
      </Card>
      
      <Card>
        <div class="text-center">
          <p class="text-3xl font-bold text-accent-primary">
            {{ heatmapData.cells.reduce((sum: number, c: any) => sum + c.count, 0) }}
          </p>
          <p class="text-sm text-text-muted mt-1">Total Anomalies</p>
        </div>
      </Card>
    </div>
  </div>
</template>

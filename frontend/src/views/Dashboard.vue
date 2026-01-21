<script setup lang="ts">
import { onMounted, onUnmounted, computed } from 'vue'
import { useAnomaliesStore } from '@/stores/anomalies'
import { useVesselsStore } from '@/stores/vessels'
import Card from '@/components/ui/Card.vue'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import { Ship, AlertTriangle, TrendingUp, AlertCircle } from 'lucide-vue-next'
import { useWebSocket } from '@/composables/useWebSocket'

const anomaliesStore = useAnomaliesStore()
const vesselsStore = useVesselsStore()
const { connect, disconnect } = useWebSocket()

onMounted(async () => {
  await anomaliesStore.fetchDashboardStats()
  await anomaliesStore.fetchAnomalies(24, 0)
  // Also fetch vessels summary to ensure stats or other components have current vessel data if needed
  await vesselsStore.fetchVesselsSummary()
  
  // Real-time updates
  connect()
})

onUnmounted(() => {
  disconnect()
})

// ECharts options for timeline - now using real data
const timelineOptions = computed(() => {
  const hourLabels = Array.from({ length: 24 }, (_, i) => `${i}h`)
  
  return {
    darkMode: true,
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e293b',
      borderColor: '#374151',
      textStyle: { color: '#f1f5f9' },
      formatter: (params: any) => {
        const data = params[0]
        return `${data.name}: ${data.value} anomal${data.value > 1 ? 'ies' : 'y'}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: hourLabels,
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#94a3b8', interval: 3 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#374151' } },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#374151', type: 'dashed' } }
    },
    series: [{
      data: anomaliesStore.anomaliesByHour,
      type: 'bar',
      itemStyle: {
        color: '#00d4ff',
        borderRadius: [4, 4, 0, 0]
      }
    }]
  }
})

// Pie chart for anomaly types - now using real data
const pieOptions = computed(() => {
  // Transform anomaly types data into pie chart format
  // Enhanced color palette for distinct anomaly types
  // Ultra-distinct color palette for maritime anomaly types
  const typeColors: Record<string, string> = {
    'speed': '#FF4D00',    // Vivid Orange
    'heading': '#00EAFF',  // Electric Cyan
    'course': '#007CFF',   // Modern Blue
    'spoofing': '#FF0055', // Shocking Pink/Red
    'position': '#2DFF00', // Neon Green
    'draft': '#7000FF',    // Deep Purple
    'length': '#FFD000',   // Bright Yellow
    'width': '#00FFAA',    // Seafoam Green
    'gap': '#FF00D4',      // Magenta
    'time': '#5500FF'      // Electric Indigo
  }
  
  // High contrast rotating palette for unknown types
  const extraColors = ['#FFBF00', '#00FFBF', '#BF00FF', '#FF00BF', '#00BFFF']
  
  const typesData = Object.entries(anomaliesStore.anomaliesByType)
    .sort((a, b) => b[1] - a[1]) // Sort by count first
    .map(([name, value], index) => {
      let color = ''
      const nameLower = name.toLowerCase()
      
      // Try to find a specific color based on keyword
      for (const [key, col] of Object.entries(typeColors)) {
        if (nameLower.includes(key)) {
          color = col
          break
        }
      }
      
      // Fallback to rotating extra palette if no keyword match
      if (!color) {
        color = extraColors[index % extraColors.length]
      }
      
      return { value, name, itemStyle: { color } }
    })
    .slice(0, 10) // Show top 10 instead of 6 for better distribution
  
  return {
    darkMode: true,
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e293b',
      borderColor: '#374151',
      textStyle: { color: '#f1f5f9' },
      formatter: (params: any) => {
        return `${params.name}: ${params.value} (${params.percent}%)`
      }
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: { color: '#94a3b8' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold',
          color: '#f1f5f9'
        }
      },
      labelLine: {
        show: false
      },
      data: typesData.length > 0 ? typesData : [
        { value: 1, name: 'No data yet', itemStyle: { color: '#6b7280' } }
      ]
    }]
  }
})

function navigateToVessel(mmsi: number) {
  window.location.href = `/vessel/${mmsi}`
}
</script>

<template>
  <div class="space-y-6 p-6">
    <div>
      <h1 class="text-3xl font-bold text-text-primary mb-2">Dashboard</h1>
      <p class="text-text-secondary">Real-time maritime anomaly detection overview</p>
    </div>
    
    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatsCard
        :value="vesselsStore.vesselsCount"
        label="Active Vessels"
        :icon="Ship"
        variant="default"
      />
      
      <StatsCard
        :value="anomaliesStore.dashboardStats?.anomalies_24h || 0"
        label="Anomalies (24h)"
        :icon="AlertTriangle"
        variant="warning"
      />
      
      <StatsCard
        :value="anomaliesStore.dashboardStats?.detection_rate || 0"
        label="Detection Rate (%)"
        :icon="TrendingUp"
        variant="success"
      />
      
      <StatsCard
        :value="vesselsStore.criticalCount"
        label="Critical Alerts"
        :icon="AlertCircle"
        variant="danger"
      />
    </div>
    
    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Timeline Chart -->
      <Card title="Anomalies by Hour (24h)">
        <v-chart
          :option="timelineOptions"
          class="h-80"
          autoresize
        />
      </Card>
      
      <!-- Pie Chart -->
      <Card title="Anomaly Types Distribution">
        <v-chart
          :option="pieOptions"
          class="h-80"
          autoresize
        />
      </Card>
    </div>
    
    <!-- Recent Anomalies Table -->
    <Card title="Recent Anomalies (24h)">
      <p class="text-xs text-text-muted mb-4 -mt-2">
        History of detected anomalies. Note: listed vessels may not be currently active on the Live Map.
      </p>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-700">
              <th class="text-left py-3 px-4 text-sm font-semibold text-text-secondary">Time</th>
              <th class="text-left py-3 px-4 text-sm font-semibold text-text-secondary">Vessel</th>
              <th class="text-left py-3 px-4 text-sm font-semibold text-text-secondary">Type</th>
              <th class="text-left py-3 px-4 text-sm font-semibold text-text-secondary">Score</th>
              <th class="text-right py-3 px-4 text-sm font-semibold text-text-secondary">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="anomaly in anomaliesStore.recentAnomalies.filter(a => a.score > 0.05)"
              :key="anomaly.data_id"
              class="border-b border-gray-700/50 hover:bg-bg-tertiary/30 transition-colors"
            >
              <td class="py-3 px-4 text-sm text-text-secondary">
                {{ new Date(anomaly.timestamp).toLocaleTimeString() }}
              </td>
              <td class="py-3 px-4">
                <div class="flex flex-col">
                  <span class="text-sm font-medium text-text-primary">
                    {{ anomaly.vessel_name || 'Unknown' }}
                  </span>
                  <span class="text-xs text-text-muted">{{ anomaly.mmsi }}</span>
                </div>
              </td>
              <td class="py-3 px-4">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="(reason, i) in anomaly.reasons.slice(0, 2)"
                    :key="i"
                    class="text-xs px-2 py-0.5 rounded-full bg-accent-warning/20 text-accent-warning"
                  >
                    {{ reason }}
                  </span>
                </div>
              </td>
              <td class="py-3 px-4">
                <span
                  :class="[
                    'text-sm font-semibold',
                    anomaly.score >= 0.8 ? 'text-vessel-danger' : 
                    anomaly.score >= 0.5 ? 'text-vessel-warning' : 'text-text-muted'
                  ]"
                >
                  {{ Math.max(1, Math.round(anomaly.score * 100)) }}%
                </span>
              </td>
              <td class="py-3 px-4 text-right">
                <button 
                  class="text-sm text-accent-primary hover:underline"
                  @click="navigateToVessel(anomaly.mmsi)"
                >
                  View Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="anomaliesStore.recentAnomalies.length === 0" class="text-center py-12">
          <AlertTriangle class="w-12 h-12 text-text-muted mx-auto mb-3" />
          <p class="text-text-secondary">No anomalies detected in the last 24 hours</p>
        </div>
      </div>
    </Card>
  </div>
</template>

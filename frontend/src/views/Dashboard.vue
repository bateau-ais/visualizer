<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAnomaliesStore } from '@/stores/anomalies'
import Card from '@/components/ui/Card.vue'
import StatsCard from '@/components/dashboard/StatsCard.vue'
import { Ship, AlertTriangle, TrendingUp, AlertCircle } from 'lucide-vue-next'

const anomaliesStore = useAnomaliesStore()

onMounted(async () => {
  await anomaliesStore.fetchDashboardStats()
  await anomaliesStore.fetchAnomalies(24, 0)
})

// ECharts options for timeline
const timelineOptions = ref({
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
    axisLine: { lineStyle: { color: '#374151' } },
    axisLabel: { color: '#94a3b8' },
    splitLine: { lineStyle: { color: '#374151', type: 'dashed' } }
  },
  series: [{
    data: [12, 8, 15, 22, 18, 25, 19],
    type: 'bar',
    itemStyle: {
      color: '#00d4ff',
      borderRadius: [4, 4, 0, 0]
    }
  }]
})

// Pie chart for anomaly types
const pieOptions = ref({
  darkMode: true,
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    backgroundColor: '#1e293b',
    borderColor: '#374151',
    textStyle: { color: '#f1f5f9' }
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
    data: [
      { value: 45, name: 'Speed', itemStyle: { color: '#ff6b35' } },
      { value: 30, name: 'Heading', itemStyle: { color: '#00d4ff' } },
      { value: 15, name: 'Spoofing', itemStyle: { color: '#ef4444' } },
      { value: 10, name: 'Others', itemStyle: { color: '#6b7280' } }
    ]
  }]
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
        :value="anomaliesStore.dashboardStats?.vessels_active || 0"
        label="Active Vessels"
        :icon="Ship"
        variant="default"
      />
      
      <StatsCard
        :value="anomaliesStore.dashboardStats?.anomalies_24h || 0"
        label="Anomalies (24h)"
        :icon="AlertTriangle"
        variant="warning"
        :trend="0.3"
      />
      
      <StatsCard
        :value="anomaliesStore.dashboardStats?.detection_rate || 0"
        label="Detection Rate (%)"
        :icon="TrendingUp"
        variant="success"
        :trend="-0.2"
      />
      
      <StatsCard
        :value="anomaliesStore.dashboardStats?.critical_count || 0"
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
    <Card title="Recent Anomalies">
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
              v-for="anomaly in anomaliesStore.recentAnomalies"
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
                    anomaly.score >= 0.5 ? 'text-vessel-warning' : 'text-vessel-normal'
                  ]"
                >
                  {{ (anomaly.score * 100).toFixed(0) }}%
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

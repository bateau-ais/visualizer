<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CheckCircle, AlertTriangle, Clock, MapPin, Ship, Activity } from 'lucide-vue-next'
import { useNotificationStore } from '@/stores/notifications'
import { storeToRefs } from 'pinia'

const router = useRouter()
const store = useNotificationStore()
const { notifications, loading } = storeToRefs(store)

onMounted(() => {
  store.fetchNotifications()
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString()
}

function getScoreColor(score: number) {
  if (score >= 0.8) return 'text-accent-danger'
  if (score >= 0.5) return 'text-accent-warning'
  return 'text-accent-primary'
}

function getScoreBg(score: number) {
  if (score >= 0.8) return 'bg-accent-danger/10 border-accent-danger/30'
  if (score >= 0.5) return 'bg-accent-warning/10 border-accent-warning/30'
  return 'bg-accent-primary/10 border-accent-primary/30'
}

async function handleAcknowledge(mmsi: number) {
  await store.acknowledge(mmsi)
}

function navigateToVessel(mmsi: number) {
  router.push(`/vessel/${mmsi}`)
}
</script>

<template>
  <div class="min-h-screen bg-bg-primary pt-20 px-4 sm:px-6 lg:px-8 pb-10">
    <div class="max-w-4xl mx-auto">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-3xl font-bold text-text-primary">Notifications</h1>
          <p class="text-text-secondary mt-1">
            All detected anomalies and alerts
          </p>
        </div>
        
        <button 
          @click="store.fetchNotifications()" 
          class="p-2 text-text-muted hover:text-text-primary transition-colors"
          title="Refresh"
        >
          <Clock class="w-5 h-5" />
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-primary"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="notifications.length === 0" class="text-center py-16 bg-bg-secondary rounded-xl border border-gray-800">
        <div class="bg-bg-tertiary w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle class="w-8 h-8 text-accent-success" />
        </div>
        <h3 class="text-xl font-medium text-text-primary">All Clear</h3>
        <p class="text-text-secondary mt-2">No anomalies detected in the last 24 hours.</p>
      </div>

      <!-- Notification List -->
      <div v-else class="space-y-4">
        <div 
          v-for="notification in notifications" 
          :key="notification.data_id"
          class="relative bg-bg-secondary rounded-lg border p-5 transition-all hover:border-gray-600"
          :class="[
            notification.acknowledged ? 'border-gray-800 opacity-75' : 'border-gray-700 shadow-lg'
          ]"
        >
          <div class="flex items-start gap-4">
            <!-- Icon -->
            <div class="flex-shrink-0">
              <div class="w-10 h-10 rounded-full flex items-center justify-center" :class="getScoreBg(notification.score)">
                <AlertTriangle class="w-5 h-5" :class="getScoreColor(notification.score)" />
              </div>
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between">
                <div>
                  <h3 class="text-lg font-medium text-text-primary flex items-center gap-2">
                    {{ notification.vessel_name || `Vessel ${notification.mmsi}` }}
                    <span v-if="notification.acknowledged" class="bg-bg-tertiary text-text-muted text-xs px-2 py-0.5 rounded-full border border-gray-700">
                      Acknowledged
                    </span>
                  </h3>
                  <p class="text-sm text-text-secondary mt-1 flex items-center gap-4">
                    <span class="flex items-center gap-1">
                      <Ship class="w-3 h-3" /> MMSI: {{ notification.mmsi }}
                    </span>
                    <span class="flex items-center gap-1">
                      <Clock class="w-3 h-3" /> {{ formatDate(String(notification.timestamp)) }}
                    </span>
                  </p>
                </div>
                
                <!-- Action Buttons -->
                <div class="flex items-center gap-2">
                  <button 
                    @click="navigateToVessel(notification.mmsi)"
                    class="p-2 text-text-secondary hover:text-accent-primary hover:bg-bg-tertiary rounded-lg transition-colors"
                    title="View Vessel History"
                  >
                    <Activity class="w-4 h-4" />
                  </button>
                  
                  <button 
                    v-if="!notification.acknowledged"
                    @click="handleAcknowledge(notification.mmsi)"
                    class="px-3 py-1.5 text-xs font-medium bg-accent-primary/10 text-accent-primary hover:bg-accent-primary/20 border border-accent-primary/30 rounded-lg transition-colors"
                  >
                    Acknowledge
                  </button>
                </div>
              </div>

              <!-- Reasons -->
              <div class="mt-3 flex flex-wrap gap-2">
                <span 
                  v-for="reason in notification.reasons" 
                  :key="reason"
                  class="px-2 py-1 text-xs font-medium rounded-md bg-bg-tertiary text-text-secondary border border-gray-700"
                >
                  {{ reason }}
                </span>
                <span class="px-2 py-1 text-xs font-medium rounded-md bg-bg-tertiary text-text-secondary border border-gray-700">
                  Score: {{ notification.score.toFixed(2) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

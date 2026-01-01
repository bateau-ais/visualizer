<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useVesselsStore } from '@/stores/vessels'
import { useWebSocket } from '@/composables/useWebSocket'
import { Filter, MapPin, Layers } from 'lucide-vue-next'
import Sidebar from '@/components/layout/Sidebar.vue'
import LeafletMap from '@/components/map/LeafletMap.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'

const vesselsStore = useVesselsStore()
const { connect, disconnect, connected } = useWebSocket()
const sidebarOpen = ref(false)
const legendOpen = ref(true)
const mapRef = ref()

onMounted(async () => {
  await vesselsStore.fetchVessels()
  connect()
})

onUnmounted(() => {
  disconnect()
})

// Watch for vessel updates from WebSocket
watch(() => vesselsStore.vessels, () => {
  if (mapRef.value && vesselsStore.vessels.length > 0) {
    // Map will auto-update via props reactivity
  }
}, { deep: true })
</script>

<template>
  <div class="relative h-[calc(100vh-4rem)]">
    <!-- Sidebar -->
    <Sidebar v-model:open="sidebarOpen" />
    
    <!-- Main Map Container -->
    <div class="h-full bg-bg-primary">
      <LeafletMap
        ref="mapRef"
        container-id="main-map"
        :vessels="vesselsStore.vessels"
        :center="[48.8566, 2.3522]"
        :zoom="6"
      />
      
      <!-- Floating Controls -->
      <div class="absolute top-4 left-4 z-[1000] space-y-2">
        <Button
          variant="secondary"
          @click="sidebarOpen = !sidebarOpen"
        >
          <Filter class="w-4 h-4 mr-2" />
          Filters
        </Button>
        
        <Button
          variant="secondary"
          @click="legendOpen = !legendOpen"
        >
          <Layers class="w-4 h-4 mr-2" />
          Layers
        </Button>
      </div>
      
      <!-- Status Badges -->
      <div class="absolute bottom-4 left-4 z-[1000] space-y-2">
        <!-- Vessel Count -->
        <div class="glass rounded-lg px-4 py-2 border border-gray-700">
          <div class="flex items-center space-x-2">
            <MapPin class="w-4 h-4 text-accent-primary" />
            <span class="text-sm font-medium text-text-primary">
              {{ vesselsStore.vesselsCount }} vessels
            </span>
          </div>
        </div>
        
        <!-- Connection Status -->
        <div class="glass rounded-lg px-4 py-2 border border-gray-700">
          <div class="flex items-center space-x-2">
            <div :class="['w-2 h-2 rounded-full', connected ? 'bg-vessel-normal animate-pulse' : 'bg-vessel-stale']" />
            <span class="text-xs text-text-muted">
              {{ connected ? 'Live' : 'Offline' }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Legend -->
      <div v-if="legendOpen" class="absolute bottom-4 right-4 z-[1000] glass rounded-lg p-4 border border-gray-700 max-w-xs">
        <h3 class="text-sm font-semibold text-text-primary mb-3 flex items-center">
          <Layers class="w-4 h-4 mr-2" />
          Legend
        </h3>
        <div class="space-y-2">
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-vessel-normal" />
            <span class="text-xs text-text-secondary">Normal ({{ vesselsStore.vesselsCount - vesselsStore.anomalyCount }})</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-vessel-warning" />
            <span class="text-xs text-text-secondary">Warning</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-vessel-danger" />
            <span class="text-xs text-text-secondary">Critical ({{ vesselsStore.anomalyCount }})</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useVesselsStore } from '@/stores/vessels'
import { useWebSocket } from '@/composables/useWebSocket'
import { Filter, MapPin, Layers } from 'lucide-vue-next'
import Sidebar from '@/components/layout/Sidebar.vue'
import LeafletMap from '@/components/map/LeafletMap.vue'
import Button from '@/components/ui/Button.vue'

const vesselsStore = useVesselsStore()
const { connect, disconnect, connected } = useWebSocket()
const sidebarOpen = ref(false)
const legendOpen = ref(true)

onMounted(async () => {
  await vesselsStore.fetchVessels()
  connect()
})

const handleMapMove = (payload: { center: any, zoom: number }) => {
  vesselsStore.mapCenter = [payload.center.lat, payload.center.lng]
  vesselsStore.mapZoom = payload.zoom
}

onUnmounted(() => {
  disconnect()
})

    function toggleLevel(level: 'normal' | 'warning' | 'critical') {
      if (vesselsStore.visibleLevels.has(level)) {
        vesselsStore.visibleLevels.delete(level)
      } else {
        vesselsStore.visibleLevels.add(level)
      }
    }
    </script>
    
    <template>
      <div class="relative h-[calc(100vh-4rem)]">
        <!-- Sidebar -->
        <Sidebar v-model:open="sidebarOpen" />
        
        <!-- Main Map Container -->
        <div class="h-full bg-bg-primary">
          <LeafletMap
            container-id="main-map"
            :vessels="vesselsStore.vessels"
            :center="vesselsStore.mapCenter"
            :zoom="vesselsStore.mapZoom"
            @move="handleMapMove"
          />
          
          <!-- Floating Controls -->
          <div class="absolute top-4 left-4 z-[1000] space-y-2">
            <!-- Inactive buttons removed as requested -->
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
          
          <!-- Legend and Filtering -->
          <div class="absolute bottom-4 right-4 z-[1000] glass rounded-lg p-4 border border-gray-700 max-w-xs">
            <h3 class="text-sm font-semibold text-text-primary mb-3 flex items-center">
              <Layers class="w-4 h-4 mr-2" />
              Filter Visibility
            </h3>
            <div class="space-y-3">
              <label class="flex items-center space-x-2 cursor-pointer group">
                <input 
                  type="checkbox" 
                  :checked="vesselsStore.visibleLevels.has('normal')"
                  @change="toggleLevel('normal')"
                  class="rounded border-gray-600 bg-bg-tertiary text-accent-primary focus:ring-accent-primary"
                />
                <div class="w-3 h-3 rounded-full bg-vessel-normal" />
                <span class="text-xs text-text-secondary group-hover:text-text-primary transition-colors">
                  Normal ({{ vesselsStore.vesselsCount - vesselsStore.anomalyCount }})
                </span>
              </label>
              
              <label class="flex items-center space-x-2 cursor-pointer group">
                <input 
                  type="checkbox" 
                  :checked="vesselsStore.visibleLevels.has('warning')"
                  @change="toggleLevel('warning')"
                  class="rounded border-gray-600 bg-bg-tertiary text-accent-primary focus:ring-accent-primary"
                />
                <div class="w-3 h-3 rounded-full bg-vessel-warning" />
                <span class="text-xs text-text-secondary group-hover:text-text-primary transition-colors">
                  Warning ({{ vesselsStore.warningCount }})
                </span>
              </label>
              
              <label class="flex items-center space-x-2 cursor-pointer group">
                <input 
                  type="checkbox" 
                  :checked="vesselsStore.visibleLevels.has('critical')"
                  @change="toggleLevel('critical')"
                  class="rounded border-gray-600 bg-bg-tertiary text-accent-primary focus:ring-accent-primary"
                />
                <div class="w-3 h-3 rounded-full bg-vessel-danger" />
                <span class="text-xs text-text-secondary group-hover:text-text-primary transition-colors">
                  Critical ({{ vesselsStore.criticalCount }})
                </span>
              </label>
            </div>
          </div>
        </div>
      </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch, createApp, ref, shallowRef } from 'vue'
import { useCanvasMap } from '@/composables/useCanvasMap'
import { useVesselsStore } from '@/stores/vessels'
import type { Vessel } from '@/types/vessel'
import VesselPopup from './VesselPopup.vue'
import L from 'leaflet'

interface Props {
  containerId: string
  vessels: Vessel[]
  center?: [number, number]
  zoom?: number
}

const props = withDefaults(defineProps<Props>(), {
  center: () => [48.8566, 2.3522],
  zoom: 6
})

const emit = defineEmits<{
  (e: 'move', payload: { center: L.LatLng, zoom: number }): void
}>()

const vesselsStore = useVesselsStore()
const { 
  map, 
  initMap, 
  initCanvasLayer, 
  updateVessels, 
  setTrajectory, 
  removeTrajectory, 
  fitBounds, 
  getVisibleVessels,
  getVesselAtPoint 
} = useCanvasMap(props.containerId)

// onMounted moved below to include map click listener setup

// Redundant watcher removed to prevent state conflicts and performance overhead

const renderRequest = ref<number | null>(null)
const lastVesselHash = ref<string>('')
const hoveredMMSI = ref<number | null>(null)

function getVesselHash(vessels: Vessel[]): string {
  // Create a simple hash from vessel count and first/last MMSIs
  if (vessels.length === 0) return '0'
  return `${vessels.length}-${vessels[0]?.mmsi}-${vessels[vessels.length - 1]?.mmsi}`
}

// Optimized watch for vessels: only trigger canvas update if data actually changed
// and use a throttled approach for position updates
const hasAutoFitted = ref(false)

// Throttled watcher for vessel updates
watch(() => props.vessels, (newVessels) => {
  const newHash = getVesselHash(newVessels)
  
  if (newHash !== lastVesselHash.value || !renderRequest.value) {
    lastVesselHash.value = newHash
    
    if (renderRequest.value) cancelAnimationFrame(renderRequest.value)
    
    renderRequest.value = requestAnimationFrame(() => {
      // Sync canvas with all state: vessels, selection, AND hover
      updateVessels(newVessels, vesselsStore.selectedVessel?.mmsi ?? null, hoveredMMSI.value)
      
      // Auto-fit bounds on first load if vessels exist
      if (!hasAutoFitted.value && newVessels.length > 0) {
        fitBounds(newVessels)
        hasAutoFitted.value = true
      }

      renderRequest.value = null
      
      // Update popup position if it exists (follow moving vessel)
      // GUARD: Check if popup is still valid and attached to map to avoid animation crashes
      if (currentPopup.value && vesselsStore.selectedVessel && map.value) {
        const selected = newVessels.find(v => v.mmsi === vesselsStore.selectedVessel?.mmsi)
        // Ensure coordinates are valid and popup is still in the DOM
        if (selected && isFinite(selected.lat) && isFinite(selected.lon)) {
           try {
             currentPopup.value.setLatLng([selected.lat, selected.lon])
           } catch (e) {
             console.warn('[LeafletMap] Failed to update popup position safely:', e)
           }
        } else if (!selected) {
           // Selected vessel disappeared
           closeSelection()
        }
      }
    })
  }
}, { deep: false })

// Watch for selection changes (from outside or clicks)
watch(() => vesselsStore.selectedVessel, (vessel) => {
  // Update palette/trajectory
  if (vessel) {
    if ('trajectory' in vessel && Array.isArray(vessel.trajectory)) {
       setTrajectory(vessel.trajectory)
    }
  } else {
    removeTrajectory()
  }
  // Force a redraw to show selection circle
  updateVessels(props.vessels, vessel?.mmsi ?? null, hoveredMMSI.value)
})

// USE shallowRef for Leaflet objects
const currentPopup = shallowRef<L.Popup | null>(null)
let currentPopupApp: any = null

function closeSelection() {
  if (currentPopup.value) {
    const popup = currentPopup.value
    currentPopup.value = null
    popup.remove()
  }
  
  if (currentPopupApp) {
    currentPopupApp.unmount()
    currentPopupApp = null
  }
  
  vesselsStore.selectVessel(null)
}

function onVesselClick(vessel: Vessel) {
  if (!map.value) return
  
  // Close previous selection properly
  closeSelection()
  
  const popupContainer = document.createElement('div')
  const popupApp = createApp(VesselPopup, { 
    vessel, 
    onNavigate: (mmsi: number) => {
      window.location.href = `/vessel/${mmsi}`
    }
  })
  popupApp.mount(popupContainer)
  currentPopupApp = popupApp
  
  const popup = L.popup({
    className: 'vessel-popup',
    maxWidth: 320,
    closeButton: true,
    autoClose: false,
    closeOnClick: false
  })
    .setLatLng([vessel.lat, vessel.lon])
    .setContent(popupContainer)
  
  popup.on('remove', () => {
    // If THIS popup is being removed (e.g. via X button) and we haven't already
    // nullified currentPopup, trigger full cleanup
    if (currentPopup.value === popup) {
       closeSelection()
    }
  })
  
  popup.openOn(map.value)
  currentPopup.value = popup
  
  vesselsStore.selectVessel(vessel.mmsi)
  vesselsStore.fetchVesselDetails(vessel.mmsi)
}

// Transparent Interaction Handlers (Map Layer Level)
function handleMapClick(e: L.LeafletMouseEvent) {
    // 1. Check if we hit a vessel
    const point = e.containerPoint
    const vessel = getVesselAtPoint(point)
    
    if (vessel) {
        // Vessel clicked
        onVesselClick(vessel)
    } else {
        // Background clicked
        closeSelection()
    }
}

function handleMapMouseMove(e: L.LeafletMouseEvent) {
    const point = e.containerPoint
    const vessel = getVesselAtPoint(point)
    const newMMSI = vessel?.mmsi ?? null
    
    if (newMMSI !== hoveredMMSI.value) {
        hoveredMMSI.value = newMMSI
        // Update canvas highlight
        updateVessels(props.vessels, vesselsStore.selectedVessel?.mmsi ?? null, newMMSI)
        
        // Update cursor
        if (map.value) {
            const container = map.value.getContainer()
            container.style.cursor = vessel ? 'pointer' : ''
        }
    }
}

onMounted(() => {
  console.log('[LeafletMap] Initializing with transparent interaction model')
  const m = initMap(props.center, props.zoom)
  
  if (m) {
    m.on('click', handleMapClick)
    m.on('mousemove', handleMapMouseMove)
    m.on('moveend', () => {
      emit('move', {
        center: m.getCenter(),
        zoom: m.getZoom()
      })
    })
  }
  
  initCanvasLayer()
  updateVessels(props.vessels)
})

// Clean up
onUnmounted(() => {
    if (renderRequest.value) {
        cancelAnimationFrame(renderRequest.value)
    }
})

// Expose methods for parent components
defineExpose({
  updateVessels,
  fitBounds,
  map,
  getVisibleVessels
})
</script>

<template>
  <div :id="containerId" class="w-full h-full rounded-lg overflow-hidden border border-gray-700" />
</template>

<style>
/* Leaflet popup customization */
.vessel-popup .leaflet-popup-content-wrapper {
  background-color: #1e293b;
  border: 1px solid #374151;
  border-radius: 0.5rem;
  padding: 0.75rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
}

.vessel-popup .leaflet-popup-tip {
  background-color: #1e293b;
  border: 1px solid #374151;
}

.vessel-popup .leaflet-popup-close-button {
  color: #94a3b8;
  font-size: 20px;
  padding: 4px 8px;
}

.vessel-popup .leaflet-popup-close-button:hover {
  color: #f1f5f9;
}

/* Vessel marker styles */
.vessel-marker {
  background: transparent !important;
  border: none !important;
}
</style>

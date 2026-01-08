<script setup lang="ts">
import { onMounted, watch, createApp, ref } from 'vue'
import { useMap } from '@/composables/useMap'
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

const vesselsStore = useVesselsStore()
const { map, markers, initMap, addVesselMarker, updateVesselPosition, removeVesselMarker, clearAllMarkers, setTrajectory, removeTrajectory, fitBounds } = useMap(props.containerId)

onMounted(() => {
  initMap(props.center, props.zoom)
  renderVessels()
})

const renderRequest = ref<number | null>(null)

watch(() => props.vessels, () => {
  if (renderRequest.value) {
    cancelAnimationFrame(renderRequest.value)
  }
  renderRequest.value = requestAnimationFrame(() => {
    renderVessels()
    renderRequest.value = null
  })
}, { deep: true }) // Re-enabled deep watch for reliability in demo

// Watch for selected vessel to draw trajectory
watch(() => vesselsStore.selectedVessel, async (vessel) => {
  if (vessel) {
    // If we have trajectory data, draw it
    if ('trajectory' in vessel && Array.isArray(vessel.trajectory)) {
       setTrajectory(vessel.trajectory)
    } else {
       // Fetch details if not present (handled by store usually, but let's be safe)
       // Actually store.selectVessel doesn't fetch details automatically unless onVesselClick calls it?
       // onVesselClick calls store.selectVessel.
       // We should fetch details here if missing? 
       // Better: onVesselClick triggers fetch.
       removeTrajectory()
    }
  } else {
    removeTrajectory()
  }
}, { deep: true })

function renderVessels() {
  if (!map.value) return
  
  // Get current marker MMSIs
  const currentMMSIs = new Set(Array.from(markers.value.keys()))
  const vesselMMSIs = new Set(props.vessels.map(v => v.mmsi))
  
  // Add or update vessels
  props.vessels.forEach(vessel => {
    if (markers.value.has(vessel.mmsi)) {
      // Update existing marker
      updateVesselPosition(vessel)
    } else {
      // Add new marker
      addVesselMarker(vessel, onVesselClick)
    }
  })
  
  // Remove vessels that are no longer present
  currentMMSIs.forEach(mmsi => {
    if (!vesselMMSIs.has(mmsi)) {
      removeVesselMarker(mmsi)
    }
  })
}

function onVesselClick(vessel: Vessel) {
  if (!map.value) return
  
  // Create Vue component instance for popup with router
  const popupContainer = document.createElement('div')
  const popupApp = createApp(VesselPopup, { 
    vessel,
    onNavigate: (mmsi: number) => {
      // Navigate using the parent router
      import('vue-router').then(({ useRouter }) => {
        window.location.href = `/vessel/${mmsi}`
      })
    }
  })
  popupApp.mount(popupContainer)
  
  // Create Leaflet popup
  const popup = L.popup({
    className: 'vessel-popup',
    maxWidth: 320,
    closeButton: true
  })
    .setLatLng([vessel.lat, vessel.lon])
    .setContent(popupContainer)
    .openOn(map.value)
  
  // Store selected vessel and fetch details (trajectory)
  vesselsStore.selectVessel(vessel.mmsi)
  vesselsStore.fetchVesselDetails(vessel.mmsi).then((details) => {
      // Logic handled by watcher
  })
}

// Expose update method for parent components
defineExpose({
  updateVesselPosition,
  fitBounds,
  map
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

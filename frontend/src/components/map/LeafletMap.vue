<script setup lang="ts">
import { onMounted, watch, createApp } from 'vue'
import { useMap } from '@/composables/useMap'
import { useVesselsStore } from '@/stores/vessels'
import type { Vessel } from '@/types/vessel'
import VesselPopup from './VesselPopup.vue'

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
const { map, initMap, addVesselMarker, updateVesselPosition, clearAllMarkers, fitBounds } = useMap(props.containerId)

onMounted(() => {
  initMap(props.center, props.zoom)
  renderVessels()
})

watch(() => props.vessels, () => {
  renderVessels()
}, { deep: true })

function renderVessels() {
  if (!map.value) return
  
  clearAllMarkers()
  
  props.vessels.forEach(vessel => {
    addVesselMarker(vessel, onVesselClick)
  })
  
  if (props.vessels.length > 0) {
    fitBounds(props.vessels)
  }
}

function onVesselClick(vessel: Vessel) {
  if (!map.value) return
  
  // Create Vue component instance for popup
  const popupContainer = document.createElement('div')
  const popupApp = createApp(VesselPopup, { vessel })
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
  
  // Store selected vessel
  vesselsStore.selectVessel(vessel.mmsi)
}

// Expose update method for parent components
defineExpose({
  updateVesselPosition,
  fitBounds
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

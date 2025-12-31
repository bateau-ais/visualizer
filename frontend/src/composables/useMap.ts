import { ref, onUnmounted, type Ref } from 'vue'
import L from 'leaflet'
import type { Vessel } from '@/types/vessel'
import { getVesselStatusColor } from '@/utils/colors'

export function useMap(containerId: string) {
    const map: Ref<L.Map | null> = ref(null)
    const markers: Ref<Map<number, L.Marker>> = ref(new Map())

    function initMap(center: [number, number] = [48.8566, 2.3522], zoom: number = 6) {
        if (map.value) return map.value

        map.value = L.map(containerId, {
            center,
            zoom,
            zoomControl: true
        })

        // Add OpenStreetMap base layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map.value)

        // Add OpenSeaMap overlay
        L.tileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png', {
            attribution: '© OpenSeaMap contributors',
            maxZoom: 18
        }).addTo(map.value)

        return map.value
    }

    function createVesselIcon(vessel: Vessel): L.DivIcon {
        const color = getVesselStatusColor(vessel.anomaly_score, vessel.is_anomaly)
        const rotation = vessel.heading || vessel.cog

        return L.divIcon({
            className: 'vessel-marker',
            html: `
        <div class="relative" style="transform: rotate(${rotation}deg)">
          <div class="absolute -inset-2 rounded-full opacity-30 animate-pulse" style="background: ${color}"></div>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="${color}" stroke="white" stroke-width="1.5">
            <path d="M12 2L4 20h16L12 2z"/>
          </svg>
          ${vessel.is_anomaly ? `<div class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-red-500 animate-ping"></div>` : ''}
        </div>
      `,
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        })
    }

    function addVesselMarker(vessel: Vessel, onClick?: (vessel: Vessel) => void) {
        if (!map.value) return

        // Remove existing marker if present
        const existingMarker = markers.value.get(vessel.mmsi)
        if (existingMarker) {
            map.value.removeLayer(existingMarker)
        }

        // Create new marker
        const icon = createVesselIcon(vessel)
        const marker = L.marker([vessel.lat, vessel.lon], { icon })

        // Tooltip (on hover)
        const tooltipContent = `
      <div class="text-xs">
        <strong>${vessel.name || 'Unknown'}</strong><br/>
        MMSI: ${vessel.mmsi}<br/>
        Speed: ${vessel.sog.toFixed(1)} kt<br/>
        Course: ${Math.round(vessel.cog)}°
      </div>
    `
        marker.bindTooltip(tooltipContent)

        // Click handler
        if (onClick) {
            marker.on('click', () => onClick(vessel))
        }

        marker.addTo(map.value)
        markers.value.set(vessel.mmsi, marker)
    }

    function updateVesselPosition(vessel: Vessel) {
        const marker = markers.value.get(vessel.mmsi)
        if (marker && map.value) {
            marker.setLatLng([vessel.lat, vessel.lon])
            marker.setIcon(createVesselIcon(vessel))
            marker.setTooltipContent(`
        <div class="text-xs">
          <strong>${vessel.name || 'Unknown'}</strong><br/>
          MMSI: ${vessel.mmsi}<br/>
          Speed: ${vessel.sog.toFixed(1)} kt<br/>
          Course: ${Math.round(vessel.cog)}°
        </div>
      `)
        } else {
            addVesselMarker(vessel)
        }
    }

    function removeVesselMarker(mmsi: number) {
        const marker = markers.value.get(mmsi)
        if (marker && map.value) {
            map.value.removeLayer(marker)
            markers.value.delete(mmsi)
        }
    }

    function clearAllMarkers() {
        markers.value.forEach((marker) => {
            if (map.value) {
                map.value.removeLayer(marker)
            }
        })
        markers.value.clear()
    }

    function fitBounds(vessels: Vessel[]) {
        if (!map.value || vessels.length === 0) return

        const bounds = L.latLngBounds(
            vessels.map(v => [v.lat, v.lon] as [number, number])
        )
        map.value.fitBounds(bounds, { padding: [50, 50] })
    }

    onUnmounted(() => {
        if (map.value) {
            map.value.remove()
            map.value = null
        }
    })

    return {
        map,
        markers,
        initMap,
        addVesselMarker,
        updateVesselPosition,
        removeVesselMarker,
        clearAllMarkers,
        fitBounds
    }
}

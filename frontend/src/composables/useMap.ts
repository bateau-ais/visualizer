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

    // State tracking for optimization
    const markerStates = new Map<number, { heading: number, is_anomaly: boolean, anomaly_score: number, lat: number, lon: number }>()

    function createVesselIcon(vessel: Vessel): L.DivIcon {
        const color = getVesselStatusColor(vessel.anomaly_score, vessel.is_anomaly)
        const rotation = vessel.heading || vessel.cog || 0

        return L.divIcon({
            className: 'vessel-marker',
            html: `
        <div class="relative" style="transform: rotate(${rotation}deg)">
          <div class="absolute -inset-2 rounded-full opacity-30 ${vessel.is_anomaly && !vessel.acknowledged ? 'animate-pulse' : ''}" style="background: ${color}"></div>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="${color}" stroke="white" stroke-width="1.5">
            <path d="M12 2L4 20h16L12 2z"/>
          </svg>
          ${vessel.is_anomaly && !vessel.acknowledged ? `<div class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-red-500 animate-ping"></div>` : ''}
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

        // Init state
        markerStates.set(vessel.mmsi, {
            heading: vessel.heading || vessel.cog || 0,
            is_anomaly: vessel.is_anomaly,
            anomaly_score: vessel.anomaly_score,
            lat: vessel.lat,
            lon: vessel.lon
        })
    }

    function updateVesselPosition(vessel: Vessel) {
        const marker = markers.value.get(vessel.mmsi)
        const prevState = markerStates.get(vessel.mmsi)

        if (marker && map.value) {
            // Check position change
            if (!prevState || Math.abs(prevState.lat - vessel.lat) > 0.000001 || Math.abs(prevState.lon - vessel.lon) > 0.000001) {
                marker.setLatLng([vessel.lat, vessel.lon])
            }

            // Check visual change (heading, anomaly status/score)
            const currentHeading = vessel.heading || vessel.cog || 0
            if (!prevState ||
                Math.abs(prevState.heading - currentHeading) > 1.0 ||
                prevState.is_anomaly !== vessel.is_anomaly ||
                prevState.anomaly_score !== vessel.anomaly_score) {

                marker.setIcon(createVesselIcon(vessel))
            }

            // Always update tooltip if data changed slightly? Maybe generic update is fine
            // Only update content if significant changes to avoid HTML parsing overhead?
            // For now, keep it simple, tooltip update is less expensive than Icon DOM thrashing
            marker.setTooltipContent(`
        <div class="text-xs">
          <strong>${vessel.name || 'Unknown'}</strong><br/>
          MMSI: ${vessel.mmsi}<br/>
          Speed: ${vessel.sog.toFixed(1)} kt<br/>
          Course: ${Math.round(vessel.cog)}°
        </div>
      `)

            // Update state
            markerStates.set(vessel.mmsi, {
                heading: currentHeading,
                is_anomaly: vessel.is_anomaly,
                anomaly_score: vessel.anomaly_score,
                lat: vessel.lat,
                lon: vessel.lon
            })

        } else {
            addVesselMarker(vessel)
        }
    }

    function removeVesselMarker(mmsi: number) {
        const marker = markers.value.get(mmsi)
        if (marker && map.value) {
            map.value.removeLayer(marker)
            markers.value.delete(mmsi)
            markerStates.delete(mmsi)
        }
    }

    const trajectoryLayer: Ref<L.Polyline | null> = ref(null)

    function setTrajectory(points: { lat: number, lon: number }[]) {
        if (!map.value) return

        removeTrajectory()

        if (points.length < 2) return

        const latlngs = points.map(p => [p.lat, p.lon] as [number, number])

        trajectoryLayer.value = L.polyline(latlngs, {
            color: '#00d4ff',
            weight: 3,
            opacity: 0.8,
            dashArray: '10, 10',
            lineCap: 'round'
        }).addTo(map.value)
    }

    function removeTrajectory() {
        if (trajectoryLayer.value && map.value) {
            map.value.removeLayer(trajectoryLayer.value)
            trajectoryLayer.value = null
        }
    }

    function clearAllMarkers() {
        markers.value.forEach((marker) => {
            if (map.value) {
                map.value.removeLayer(marker)
            }
        })
        markers.value.clear()
        markerStates.clear()
        removeTrajectory()
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
        markerStates.clear()
    })

    return {
        map,
        markers,
        initMap,
        addVesselMarker,
        updateVesselPosition,
        removeVesselMarker,
        clearAllMarkers,
        setTrajectory,
        removeTrajectory,
        fitBounds
    }
}

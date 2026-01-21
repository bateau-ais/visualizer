import { ref, onUnmounted, type Ref } from 'vue'
import L from 'leaflet'
import type { Vessel } from '@/types/vessel'
import { getVesselStatusColor } from '@/utils/colors'

interface VesselRenderCache {
    x: number
    y: number
    heading: number
    color: string
    isAnomaly: boolean
    acknowledged: boolean
}

export function useCanvasMap(containerId: string) {
    const map: Ref<L.Map | null> = ref(null)
    const canvasLayer: Ref<VesselCanvasLayer | null> = ref(null)
    const vesselCache = new Map<number, VesselRenderCache>()
    const visibleVessels = ref<Set<number>>(new Set())
    const trajectoryLayer: Ref<L.Polyline | null> = ref(null)

    // Canvas renderer with custom vessel drawing
    class VesselCanvasLayer extends L.Layer {
        private canvas: HTMLCanvasElement | null = null
        private ctx: CanvasRenderingContext2D | null = null
        private vessels: Vessel[] = []
        private bounds: L.LatLngBounds | null = null
        private selectedMMSI: number | null = null
        private hoveredMMSI: number | null = null

        constructor() {
            super()
        }

        onAdd(map: L.Map): this {
            const canvas = L.DomUtil.create('canvas', 'leaflet-canvas-layer')
            const size = map.getSize()
            canvas.width = size.x
            canvas.height = size.y
            canvas.style.position = 'absolute'

            // TRANSPARENT INTERACTION: Let events pass through to map and other UI
            canvas.style.pointerEvents = 'none'

            this.canvas = canvas
            this.ctx = canvas.getContext('2d')!

            map.getPanes().overlayPane!.appendChild(canvas)

            // Initial positioning
            this._updatePosition()

            // Handle map events
            map.on('move', this._updatePosition, this)
            map.on('zoom viewreset', this.redraw, this)
            map.on('resize', this.onResize, this)

            this.redraw()
            return this
        }

        onRemove(map: L.Map): this {
            if (this.canvas) {
                L.DomUtil.remove(this.canvas)
                map.off('move', this._updatePosition, this)
                map.off('zoom viewreset', this.redraw, this)
                map.off('resize', this.onResize, this)
            }
            return this
        }

        // Update Canvas position to match map position
        _updatePosition = () => {
            if (!this.canvas || !map.value) return

            const topLeft = map.value.containerPointToLayerPoint([0, 0])
            L.DomUtil.setPosition(this.canvas, topLeft)

            this.redraw()
        }

        onResize() {
            if (!this.canvas || !map.value) return
            const size = map.value.getSize()
            this.canvas.width = size.x
            this.canvas.height = size.y
            this.redraw()
        }

        updateState(vessels: Vessel[], selectedMMSI?: number | null, hoveredMMSI?: number | null) {
            this.vessels = vessels
            this.selectedMMSI = selectedMMSI ?? null
            this.hoveredMMSI = hoveredMMSI ?? null
            this.redraw()
        }

        redraw = () => {
            if (!this.ctx || !this.canvas || !map.value) return

            // Clear canvas
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)

            // Get current map bounds for virtualization
            this.bounds = map.value.getBounds()

            // Filter visible vessels (virtualization)
            const filteredVessels = this.vessels.filter(vessel =>
                this.bounds!.contains([vessel.lat, vessel.lon])
            )

            // Update visible vessels set
            visibleVessels.value.clear()
            filteredVessels.forEach(v => visibleVessels.value.add(v.mmsi))

            // Draw each visible vessel
            // Sort by latitude to handle overlap occlusion
            filteredVessels.sort((a, b) => b.lat - a.lat).forEach(vessel => {
                this.drawVessel(vessel)
            })
        }

        private drawVessel(vessel: Vessel) {
            if (!this.ctx || !map.value) return

            const point = map.value.latLngToContainerPoint([vessel.lat, vessel.lon])
            const heading = vessel.heading || vessel.cog || 0
            const color = getVesselStatusColor(vessel.anomaly_score, vessel.is_anomaly)
            const isSelected = this.selectedMMSI === vessel.mmsi
            const isHovered = this.hoveredMMSI === vessel.mmsi

            // Cache vessel render state for hit detection
            vesselCache.set(vessel.mmsi, {
                x: point.x,
                y: point.y,
                heading,
                color,
                isAnomaly: vessel.is_anomaly,
                acknowledged: vessel.acknowledged || false
            })

            this.ctx.save()
            this.ctx.translate(point.x, point.y)

            // Draw selection indicator (WHITE CIRCLE)
            if (isSelected) {
                this.ctx.beginPath()
                this.ctx.arc(0, 0, 22, 0, Math.PI * 2)
                this.ctx.strokeStyle = '#ffffff'
                this.ctx.lineWidth = 2
                this.ctx.shadowColor = 'rgba(0, 0, 0, 0.5)'
                this.ctx.shadowBlur = 4
                this.ctx.stroke()
            }

            // Draw hover indicator
            if (isHovered && !isSelected) {
                this.ctx.beginPath()
                this.ctx.arc(0, 0, 18, 0, Math.PI * 2)
                this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)'
                this.ctx.lineWidth = 1.5
                this.ctx.stroke()
            }

            this.ctx.rotate((heading * Math.PI) / 180)

            // Draw glow for anomalies
            if (vessel.is_anomaly && !vessel.acknowledged) {
                this.ctx.beginPath()
                this.ctx.arc(0, 0, 16, 0, Math.PI * 2)
                this.ctx.fillStyle = color
                this.ctx.globalAlpha = 0.3
                this.ctx.fill()
                this.ctx.globalAlpha = 1.0
            }

            // Draw vessel triangle
            this.ctx.beginPath()
            this.ctx.moveTo(0, -12)
            this.ctx.lineTo(-6, 8)
            this.ctx.lineTo(6, 8)
            this.ctx.closePath()

            this.ctx.fillStyle = color
            this.ctx.fill()

            this.ctx.strokeStyle = '#ffffff'
            this.ctx.lineWidth = 1.5
            this.ctx.stroke()

            // Draw alert indicator for unacknowledged anomalies
            if (vessel.is_anomaly && !vessel.acknowledged) {
                this.ctx.rotate(-(heading * Math.PI) / 180)
                this.ctx.beginPath()
                this.ctx.arc(8, -8, 4, 0, Math.PI * 2)
                this.ctx.fillStyle = '#ef4444'
                this.ctx.fill()
                this.ctx.strokeStyle = '#fff'
                this.ctx.lineWidth = 1
                this.ctx.stroke()
            }

            this.ctx.restore()
        }

        // Public method to find a vessel at a specific container point
        getVesselAtPoint(point: L.Point): Vessel | null {
            let closestVessel: Vessel | null = null
            let minDistance = 20 // Hit radius in pixels

            visibleVessels.value.forEach(mmsi => {
                const cached = vesselCache.get(mmsi)
                if (!cached) return

                const dx = cached.x - point.x
                const dy = cached.y - point.y
                const distance = Math.sqrt(dx * dx + dy * dy)

                if (distance < minDistance) {
                    minDistance = distance
                    closestVessel = this.vessels.find(v => v.mmsi === mmsi) || null
                }
            })
            return closestVessel
        }
    }

    function initMap(center: [number, number] = [48.8566, 2.3522], zoom: number = 6) {
        if (map.value) return map.value

        try {
            const newMap = L.map(containerId, {
                center,
                zoom,
                zoomControl: true,
                preferCanvas: true
            })

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }).addTo(newMap)

            map.value = newMap
        } catch (error) {
            console.error('[useCanvasMap] CRITICAL ERROR calling L.map:', error)
            return null
        }

        L.tileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png', {
            attribution: '© OpenSeaMap contributors',
            maxZoom: 18
        }).addTo(map.value)

        return map.value
    }

    function initCanvasLayer() {
        if (!map.value || canvasLayer.value) return

        canvasLayer.value = new VesselCanvasLayer()
        canvasLayer.value.addTo(map.value)
    }

    function updateVessels(vessels: Vessel[], selectedMMSI?: number | null, hoveredMMSI?: number | null) {
        if (!canvasLayer.value) return
        canvasLayer.value.updateState(vessels, selectedMMSI, hoveredMMSI)
    }

    function setTrajectory(points: { lat: number; lon: number }[]) {
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

    function fitBounds(vessels: Vessel[]) {
        if (!map.value || vessels.length === 0) return

        const bounds = L.latLngBounds(
            vessels.map(v => [v.lat, v.lon] as [number, number])
        )
        map.value.fitBounds(bounds, { padding: [50, 50] })
    }

    function getVisibleVessels(): Set<number> {
        return visibleVessels.value
    }

    function getVesselAtPoint(point: L.Point): Vessel | null {
        if (!canvasLayer.value) return null
        return canvasLayer.value.getVesselAtPoint(point)
    }

    onUnmounted(() => {
        if (canvasLayer.value && map.value) {
            map.value.removeLayer(canvasLayer.value)
        }
        if (map.value) {
            map.value.remove()
            map.value = null
        }
        vesselCache.clear()
        visibleVessels.value.clear()
    })

    return {
        map,
        initMap,
        initCanvasLayer,
        updateVessels,
        setTrajectory,
        removeTrajectory,
        fitBounds,
        getVisibleVessels,
        getVesselAtPoint
    }
}

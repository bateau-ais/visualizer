import { ref, shallowRef, onUnmounted } from 'vue'
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
    // USE shallowRef for Leaflet objects to prevent Proxy-related crashes
    const map = shallowRef<L.Map | null>(null)
    const canvasLayer = shallowRef<VesselCanvasLayer | null>(null)
    const vesselCache = new Map<number, VesselRenderCache>()
    const visibleVessels = ref<Set<number>>(new Set())
    const trajectoryLayer = shallowRef<L.Polyline | null>(null)

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

            const zoom = map.value.getZoom()
            const isDetailed = zoom >= 11
            const ctx = this.ctx

            // Clear canvas
            ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)

            // Get current map bounds for virtualization
            this.bounds = map.value.getBounds()

            // Filter visible vessels (virtualization)
            const filteredVessels = this.vessels.filter(vessel =>
                this.bounds!.contains([vessel.lat, vessel.lon])
            )

            // Update visible vessels set
            visibleVessels.value.clear()
            vesselCache.clear() // Clear cache before rebuild

            // Group by color for batching
            const groupedVessels = new Map<string, Vessel[]>()
            const anomalous: Vessel[] = []

            const vesselsStore = useVesselsStore()
            const visibleLevels = vesselsStore.visibleLevels

            for (const vessel of filteredVessels) {
                // Visibility Filtering logic
                let level: 'normal' | 'warning' | 'critical' = 'normal'
                if (vessel.is_anomaly && !vessel.acknowledged) {
                    if (vessel.anomaly_score >= 0.8) level = 'critical'
                    else if (vessel.anomaly_score >= 0.5) level = 'warning'
                }

                if (!visibleLevels.has(level)) continue

                visibleVessels.value.add(vessel.mmsi)

                // Prioritize anomaly status for grouping/ordering
                if (vessel.is_anomaly && !vessel.acknowledged) {
                    anomalous.push(vessel)
                } else {
                    const color = getVesselStatusColor(vessel.anomaly_score, vessel.is_anomaly)
                    if (!groupedVessels.has(color)) groupedVessels.set(color, [])
                    groupedVessels.get(color)!.push(vessel)
                }
            }

            // Draw Normal/Stable vessels in batches (lower priority)
            groupedVessels.forEach((vessels, color) => {
                ctx.fillStyle = color
                for (const vessel of vessels) {
                    this.drawVesselSimplified(vessel, color, isDetailed)
                }
            })

            // Draw Anomalies (higher priority, always detailed)
            for (const vessel of anomalous) {
                const color = getVesselStatusColor(vessel.anomaly_score, vessel.is_anomaly)
                this.drawVesselDetailed(vessel, color, true)
            }

            // Draw selected/hovered on top
            if (this.selectedMMSI || this.hoveredMMSI) {
                const special = filteredVessels.filter(v =>
                    v.mmsi === this.selectedMMSI || v.mmsi === this.hoveredMMSI
                )
                for (const vessel of special) {
                    const color = getVesselStatusColor(vessel.anomaly_score, vessel.is_anomaly)
                    this.drawVesselDetailed(vessel, color, false)
                }
            }
        }

        private drawVesselSimplified(vessel: Vessel, color: string, isDetailed: boolean) {
            if (!map.value || !this.ctx) return
            const point = map.value.latLngToContainerPoint([vessel.lat, vessel.lon])

            // Re-populate cache for hit detection
            vesselCache.set(vessel.mmsi, {
                x: point.x,
                y: point.y,
                heading: vessel.heading || vessel.cog || 0,
                color,
                isAnomaly: vessel.is_anomaly,
                acknowledged: vessel.acknowledged || false
            })

            if (isDetailed) {
                this.drawTriangle(point.x, point.y, vessel.heading || vessel.cog || 0, color)
            } else {
                this.ctx.fillRect(point.x - 2, point.y - 2, 4, 4)
            }
        }

        private drawVesselDetailed(vessel: Vessel, color: string, isAnomalyFlash: boolean) {
            if (!map.value || !this.ctx) return
            const point = map.value.latLngToContainerPoint([vessel.lat, vessel.lon])
            const heading = vessel.heading || vessel.cog || 0
            const isSelected = this.selectedMMSI === vessel.mmsi
            const isHovered = this.hoveredMMSI === vessel.mmsi

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

            if (isSelected) {
                this.ctx.beginPath()
                this.ctx.arc(0, 0, 22, 0, Math.PI * 2)
                this.ctx.strokeStyle = '#ffffff'
                this.ctx.lineWidth = 2
                this.ctx.stroke()
            } else if (isHovered) {
                this.ctx.beginPath()
                this.ctx.arc(0, 0, 18, 0, Math.PI * 2)
                this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)'
                this.ctx.lineWidth = 1.5
                this.ctx.stroke()
            }

            if (isAnomalyFlash) {
                this.ctx.beginPath()
                this.ctx.arc(0, 0, 16, 0, Math.PI * 2)
                this.ctx.fillStyle = color
                this.ctx.globalAlpha = 0.3
                this.ctx.fill()
                this.ctx.globalAlpha = 1.0
            }

            this.ctx.rotate((heading * Math.PI) / 180)
            this.drawTriangleShape(color)

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

        private drawTriangle(x: number, y: number, heading: number, color: string) {
            if (!this.ctx) return
            this.ctx.save()
            this.ctx.translate(x, y)
            this.ctx.rotate((heading * Math.PI) / 180)
            this.drawTriangleShape(color)
            this.ctx.restore()
        }

        private drawTriangleShape(color: string) {
            if (!this.ctx) return
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

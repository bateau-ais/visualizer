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
    const canvasLayer: Ref<any> = ref(null)
    const vesselCache = new Map<number, VesselRenderCache>()
    const visibleVessels = ref<Set<number>>(new Set())
    const trajectoryLayer: Ref<L.Polyline | null> = ref(null)

    // Canvas renderer with custom vessel drawing
    class VesselCanvasLayer extends L.Layer {
        private canvas: HTMLCanvasElement | null = null
        private ctx: CanvasRenderingContext2D | null = null
        private vessels: Vessel[] = []
        private bounds: L.LatLngBounds | null = null
        private onClick?: (vessel: Vessel) => void

        constructor(onClick?: (vessel: Vessel) => void) {
            super()
            this.onClick = onClick
        }

        onAdd(map: L.Map): this {
            const canvas = L.DomUtil.create('canvas', 'leaflet-canvas-layer')
            const size = map.getSize()
            canvas.width = size.x
            canvas.height = size.y
            canvas.style.position = 'absolute'
            canvas.style.pointerEvents = 'auto'

            this.canvas = canvas
            this.ctx = canvas.getContext('2d')!

            map.getPanes().overlayPane!.appendChild(canvas)

            // Handle map events
            map.on('move zoom viewreset', this.redraw, this)
            map.on('resize', this.onResize, this)

            // Handle click events
            L.DomEvent.on(canvas, 'click', this.handleClick, this)

            this.redraw()
            return this
        }

        onRemove(map: L.Map): this {
            if (this.canvas) {
                L.DomUtil.remove(this.canvas)
                map.off('move zoom viewreset', this.redraw, this)
                map.off('resize', this.onResize, this)
                L.DomEvent.off(this.canvas, 'click', this.handleClick, this)
            }
            return this
        }

        onResize(e: any) {
            if (!this.canvas || !map.value) return
            const size = map.value.getSize()
            this.canvas.width = size.x
            this.canvas.height = size.y
            this.redraw()
        }

        setVessels(vessels: Vessel[]) {
            this.vessels = vessels
            this.redraw()
        }

        redraw = () => {
            if (!this.ctx || !this.canvas || !map.value) return

            // Clear canvas
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)

            // Get current map bounds for virtualization
            this.bounds = map.value.getBounds()

            // Filter visible vessels (virtualization)
            const visibleVessels = this.vessels.filter(vessel =>
                this.bounds!.contains([vessel.lat, vessel.lon])
            )

            // Update visible vessels set
            const newVisibleSet = new Set(visibleVessels.map(v => v.mmsi))
            visibleVessels.length = 0
            visibleVessels.splice(0, visibleVessels.length, ...visibleVessels.map(v => v.mmsi))

            // Draw each visible vessel
            visibleVessels.forEach(vessel => {
                this.drawVessel(vessel)
            })
        }

        private drawVessel(vessel: Vessel) {
            if (!this.ctx || !map.value) return

            const point = map.value.latLngToContainerPoint([vessel.lat, vessel.lon])
            const heading = vessel.heading || vessel.cog || 0
            const color = getVesselStatusColor(vessel.anomaly_score, vessel.is_anomaly)

            // Cache vessel render state
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
            this.ctx.moveTo(0, -12)  // Top point
            this.ctx.lineTo(-6, 8)   // Bottom left
            this.ctx.lineTo(6, 8)    // Bottom right
            this.ctx.closePath()

            // Fill
            this.ctx.fillStyle = color
            this.ctx.fill()

            // Stroke
            this.ctx.strokeStyle = '#ffffff'
            this.ctx.lineWidth = 1.5
            this.ctx.stroke()

            // Draw alert indicator for unacknowledged anomalies
            if (vessel.is_anomaly && !vessel.acknowledged) {
                this.ctx.beginPath()
                this.ctx.arc(8, -8, 3, 0, Math.PI * 2)
                this.ctx.fillStyle = '#ef4444'
                this.ctx.fill()
            }

            this.ctx.restore()
        }

        private handleClick = (e: MouseEvent) => {
            if (!this.canvas || !this.onClick) return

            const rect = this.canvas.getBoundingClientRect()
            const x = e.clientX - rect.left
            const y = e.clientY - rect.top

            // Find clicked vessel using spatial proximity
            let closestVessel: Vessel | null = null
            let minDistance = 20 // Click tolerance in pixels

            this.vessels.forEach(vessel => {
                const cached = vesselCache.get(vessel.mmsi)
                if (!cached) return

                const dx = cached.x - x
                const dy = cached.y - y
                const distance = Math.sqrt(dx * dx + dy * dy)

                if (distance < minDistance) {
                    minDistance = distance
                    closestVessel = vessel
                }
            })

            if (closestVessel) {
                this.onClick(closestVessel)
            }
        }
    }

    function initMap(center: [number, number] = [48.8566, 2.3522], zoom: number = 6) {
        if (map.value) return map.value

        map.value = L.map(containerId, {
            center,
            zoom,
            zoomControl: true,
            preferCanvas: true // Enable Canvas rendering globally
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

    function initCanvasLayer(onClick?: (vessel: Vessel) => void) {
        if (!map.value || canvasLayer.value) return

        canvasLayer.value = new VesselCanvasLayer(onClick)
        canvasLayer.value.addTo(map.value)
    }

    function updateVessels(vessels: Vessel[]) {
        if (!canvasLayer.value) return
        canvasLayer.value.setVessels(vessels)
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
        getVisibleVessels
    }
}

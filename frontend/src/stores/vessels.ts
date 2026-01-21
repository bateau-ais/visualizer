import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Vessel, VesselFilter } from '@/types/vessel'
import api from '@/utils/api'
import { useNotificationStore } from './notifications'

export const useVesselsStore = defineStore('vessels', () => {
    // State
    const vessels = ref<Vessel[]>([])
    const mmsiToIndex = ref<Map<number, number>>(new Map()) // Optimization: O(1) lookup
    const selectedVessel = ref<Vessel | null>(null)
    const loading = ref(false)
    const error = ref<string | null>(null)

    // Filters
    const filters = ref<VesselFilter>({
        types: [],
        statuses: [],
        minSpeed: 0,
        maxSpeed: 50,
        period: '24h'
    })

    // Batching logic
    const pendingUpdates = new Map<number, Vessel>()
    let flushTimer: number | null = null

    // Computed
    const vesselsCount = computed(() => vessels.value.length)
    const anomalousVessels = computed(() =>
        vessels.value.filter(v => v.is_anomaly)
    )
    const anomalyCount = computed(() => anomalousVessels.value.length)

    // Split based on score thresholds (matching colors.ts)
    // Critical: score >= 0.8
    const criticalVessels = computed(() =>
        anomalousVessels.value.filter(v => v.anomaly_score >= 0.8)
    )
    const criticalCount = computed(() => criticalVessels.value.length)

    // Warning: 0.5 <= score < 0.8
    const warningVessels = computed(() =>
        anomalousVessels.value.filter(v => v.anomaly_score >= 0.5 && v.anomaly_score < 0.8)
    )
    const warningCount = computed(() => warningVessels.value.length)

    // Helper to rebuild index map
    function rebuildIndexMap() {
        mmsiToIndex.value.clear()
        vessels.value.forEach((v, idx) => {
            mmsiToIndex.value.set(v.mmsi, idx)
        })
    }

    // Actions
    async function fetchVessels() {
        loading.value = true
        error.value = null

        try {
            const params = new URLSearchParams()
            if (filters.value.types.length > 0) {
                params.append('vessel_type', filters.value.types.join(','))
            }
            if (filters.value.minSpeed > 0) {
                params.append('min_speed', filters.value.minSpeed.toString())
            }
            if (filters.value.maxSpeed < 50) {
                params.append('max_speed', filters.value.maxSpeed.toString())
            }

            const response = await api.get(`/vessels?${params}`)
            vessels.value = response.data.vessels
            rebuildIndexMap()
        } catch (err: any) {
            error.value = err.message
            console.error('Error fetching vessels:', err)
        } finally {
            loading.value = false
        }
    }

    // Cache logic
    interface CacheEntry {
        data: any
        timestamp: number
    }
    const detailsCache = new Map<number, CacheEntry>()
    const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

    async function fetchVesselDetails(mmsi: number) {
        // Check cache first
        const cached = detailsCache.get(mmsi)
        const now = Date.now()

        if (cached && (now - cached.timestamp < CACHE_TTL)) {
            selectedVessel.value = cached.data
            return cached.data
        }

        try {
            const response = await api.get(`/vessels/${mmsi}`)
            const data = response.data

            // Store in cache
            detailsCache.set(mmsi, {
                data: data,
                timestamp: now
            })

            selectedVessel.value = data
            return data
        } catch (err: any) {
            error.value = err.message
            console.error(`Error fetching vessel ${mmsi}:`, err)
            throw err
        }
    }

    function flushUpdates() {
        if (pendingUpdates.size === 0) return

        // Process all pending updates in one go
        pendingUpdates.forEach((vesselData, mmsi) => {
            const index = mmsiToIndex.value.get(mmsi)

            if (index !== undefined) {
                // Update existing
                vessels.value[index] = vesselData
            } else {
                // Add new
                const newIdx = vessels.value.push(vesselData) - 1
                mmsiToIndex.value.set(mmsi, newIdx)
            }

            // Update selected vessel if it's the same
            if (selectedVessel.value?.mmsi === mmsi) {
                selectedVessel.value = vesselData
            }
        })

        pendingUpdates.clear()
        flushTimer = null
    }

    function updateVessel(vesselData: Vessel) {
        // Queue update
        pendingUpdates.set(vesselData.mmsi, vesselData)

        // Schedule flush if not already scheduled
        if (!flushTimer) {
            flushTimer = window.setTimeout(flushUpdates, 500) // 500ms batch window
        }
    }

    function selectVessel(mmsi: number | null) {
        if (mmsi === null) {
            selectedVessel.value = null
            return
        }

        const index = mmsiToIndex.value.get(mmsi)
        if (index !== undefined) {
            selectedVessel.value = vessels.value[index]
        }
    }

    function setFilters(newFilters: Partial<VesselFilter>) {
        filters.value = { ...filters.value, ...newFilters }
    }

    async function acknowledgeVessel(mmsi: number) {
        try {
            await api.post(`/vessels/${mmsi}/acknowledge`)

            // Update local state and map
            const index = mmsiToIndex.value.get(mmsi)
            if (index !== undefined) {
                vessels.value[index].acknowledged = true
            }



            // Sync with notification store
            const notificationStore = useNotificationStore()
            notificationStore.markAsReadLocal(mmsi)
        } catch (err: any) {
            error.value = err.message
            console.error(`Error acknowledging vessel ${mmsi}:`, err)
            throw err
        }
    }

    async function searchVessels(query: string): Promise<Vessel[]> {
        if (!query || query.trim().length === 0) {
            return []
        }

        try {
            const response = await api.get(`/vessels/search?q=${encodeURIComponent(query)}`)
            return response.data.vessels
        } catch (err: any) {
            console.error('Error searching vessels:', err)
            return []
        }
    }

    return {
        // State
        vessels,
        selectedVessel,
        loading,
        error,
        filters,

        // Computed
        vesselsCount,
        anomalousVessels,
        anomalyCount,
        criticalCount,
        warningCount,

        // Actions
        fetchVessels,
        fetchVesselDetails,
        updateVessel,
        selectVessel,
        setFilters,
        acknowledgeVessel,
        searchVessels
    }
})

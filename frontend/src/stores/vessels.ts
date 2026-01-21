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
    const lastUpdate = ref(Date.now())
    const dataLevel = ref<'none' | 'summary' | 'full'>('none')

    // Map State (to persist view between navigations)
    const mapCenter = ref<[number, number]>([48.8566, 2.3522])
    const mapZoom = ref(6)

    // Filters
    const filters = ref<VesselFilter>({
        types: [],
        statuses: [],
        minSpeed: 0,
        maxSpeed: 50,
        period: '24h'
    })

    const visibleLevels = ref<Set<'normal' | 'warning' | 'critical'>>(new Set(['normal', 'warning', 'critical']))

    // Batching logic
    const pendingUpdates = new Map<number, Vessel>()
    let flushTimer: number | null = null

    // Computed
    const vesselsCount = computed(() => vessels.value.length)
    // Aggregated Stats (to avoid multiple filters on 10k+ arrays)
    const anomalyCount = ref(0)
    const criticalCount = ref(0)
    const warningCount = ref(0)

    function updateStats() {
        let aCount = 0
        let cCount = 0
        let wCount = 0

        for (const v of vessels.value) {
            if (v.is_anomaly) {
                aCount++
                if (v.anomaly_score >= 0.8) cCount++
                else if (v.anomaly_score >= 0.5) wCount++
            }
        }

        anomalyCount.value = aCount
        criticalCount.value = cCount
        warningCount.value = wCount
    }

    // Helper to rebuild index map
    function rebuildIndexMap() {
        mmsiToIndex.value.clear()
        vessels.value.forEach((v, idx) => {
            mmsiToIndex.value.set(v.mmsi, idx)
        })
    }

    // Actions
    async function fetchVessels(force = false) {
        // Skip only if already have FULL data and not forced
        if (!force && dataLevel.value === 'full' && vessels.value.length > 0) {
            return
        }

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
            updateStats()
            dataLevel.value = 'full'
            lastUpdate.value = Date.now()
        } catch (err: any) {
            error.value = err.message
            console.error('Error fetching vessels:', err)
        } finally {
            loading.value = false
        }
    }

    async function fetchVesselsSummary() {
        loading.value = true
        error.value = null

        try {
            const params = new URLSearchParams()
            params.append('summary', 'true')

            if (filters.value.types.length > 0) {
                params.append('vessel_type', filters.value.types.join(','))
            }

            const response = await api.get(`/vessels?${params}`)
            // Cast VesselSummary[] to Vessel[] as it is a subset
            vessels.value = response.data.vessels
            rebuildIndexMap()
            updateStats()
            dataLevel.value = 'summary'
        } catch (err: any) {
            error.value = err.message
            console.error('Error fetching vessels summary:', err)
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
        updateStats()
        lastUpdate.value = Date.now()
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
        mapCenter,
        mapZoom,

        // Computed / Ref
        vesselsCount,
        anomalyCount,
        criticalCount,
        warningCount,

        // Actions
        fetchVessels,
        fetchVesselsSummary,
        fetchVesselDetails,
        updateVessel,
        selectVessel,
        setFilters,
        acknowledgeVessel,
        searchVessels,
        lastUpdate,
        dataLevel,
        visibleLevels
    }
})

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Vessel, VesselFilter } from '@/types/vessel'
import api from '@/utils/api'

export const useVesselsStore = defineStore('vessels', () => {
    // State
    const vessels = ref<Vessel[]>([])
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

    // Computed
    const vesselsCount = computed(() => vessels.value.length)
    const anomalousVessels = computed(() =>
        vessels.value.filter(v => v.is_anomaly)
    )
    const anomalyCount = computed(() => anomalousVessels.value.length)

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
        } catch (err: any) {
            error.value = err.message
            console.error('Error fetching vessels:', err)
        } finally {
            loading.value = false
        }
    }

    async function fetchVesselDetails(mmsi: number) {
        try {
            const response = await api.get(`/vessels/${mmsi}`)
            selectedVessel.value = response.data
            return response.data
        } catch (err: any) {
            error.value = err.message
            console.error(`Error fetching vessel ${mmsi}:`, err)
            throw err
        }
    }

    function updateVessel(vesselData: Vessel) {
        const index = vessels.value.findIndex(v => v.mmsi === vesselData.mmsi)
        if (index !== -1) {
            vessels.value[index] = vesselData
        } else {
            vessels.value.push(vesselData)
        }

        // Update selected vessel if it's the same
        if (selectedVessel.value?.mmsi === vesselData.mmsi) {
            selectedVessel.value = vesselData
        }
    }

    function selectVessel(mmsi: number | null) {
        if (mmsi === null) {
            selectedVessel.value = null
            return
        }

        const vessel = vessels.value.find(v => v.mmsi === mmsi)
        if (vessel) {
            selectedVessel.value = vessel
        }
    }

    function setFilters(newFilters: Partial<VesselFilter>) {
        filters.value = { ...filters.value, ...newFilters }
    }

    async function acknowledgeVessel(mmsi: number) {
        try {
            await api.post(`/vessels/${mmsi}/acknowledge`)

            // Update local state
            const vessel = vessels.value.find(v => v.mmsi === mmsi)
            if (vessel) {
                vessel.acknowledged = true
            }
            if (selectedVessel.value?.mmsi === mmsi) {
                selectedVessel.value.acknowledged = true
            }
        } catch (err: any) {
            error.value = err.message
            console.error(`Error acknowledging vessel ${mmsi}:`, err)
            throw err
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

        // Actions
        fetchVessels,
        fetchVesselDetails,
        updateVessel,
        selectVessel,
        setFilters,
        acknowledgeVessel
    }
})

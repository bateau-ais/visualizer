import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AnomalyEvent, DashboardStats } from '@/types/anomaly'
import api from '@/utils/api'

export const useAnomaliesStore = defineStore('anomalies', () => {
    // State
    const anomalies = ref<AnomalyEvent[]>([])
    const dashboardStats = ref<DashboardStats | null>(null)
    const loading = ref(false)
    const error = ref<string | null>(null)

    // Computed
    const recentAnomalies = computed(() =>
        anomalies.value.slice(0, 10)
    )

    const criticalAnomalies = computed(() =>
        anomalies.value.filter(a => a.score >= 0.8)
    )

    // Actions
    async function fetchAnomalies(hours: number = 24, minScore: number = 0) {
        loading.value = true
        error.value = null

        try {
            const response = await api.get('/anomalies', {
                params: { hours, min_score: minScore }
            })
            anomalies.value = response.data
        } catch (err: any) {
            error.value = err.message
            console.error('Error fetching anomalies:', err)
        } finally {
            loading.value = false
        }
    }

    async function fetchDashboardStats() {
        try {
            const response = await api.get('/anomalies/stats')
            dashboardStats.value = response.data
        } catch (err: any) {
            error.value = err.message
            console.error('Error fetching stats:', err)
        }
    }

    function addAnomaly(anomaly: AnomalyEvent) {
        // Add to beginning
        anomalies.value.unshift(anomaly)

        // Keep only last 1000
        if (anomalies.value.length > 1000) {
            anomalies.value = anomalies.value.slice(0, 1000)
        }
    }

    return {
        // State
        anomalies,
        dashboardStats,
        loading,
        error,

        // Computed
        recentAnomalies,
        criticalAnomalies,

        // Actions
        fetchAnomalies,
        fetchDashboardStats,
        addAnomaly
    }
})

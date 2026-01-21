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

    // Batching logic
    const pendingAnomalies: AnomalyEvent[] = []
    let flushTimer: number | null = null

    // Computed
    const recentAnomalies = computed(() =>
        anomalies.value.slice(0, 10)
    )

    const criticalAnomalies = computed(() =>
        anomalies.value.filter(a => a.score >= 0.8)
    )

    const anomaliesByHour = computed(() => {
        // Group anomalies by hour for the last 24 hours
        const now = new Date()
        const hourCounts = Array(24).fill(0)

        anomalies.value.forEach(anomaly => {
            const aTime = new Date(anomaly.timestamp)
            const hoursAgo = Math.floor((now.getTime() - aTime.getTime()) / (1000 * 60 * 60))

            if (hoursAgo >= 0 && hoursAgo < 24) {
                hourCounts[23 - hoursAgo]++
            }
        })

        return hourCounts
    })

    const anomaliesByType = computed(() => {
        // Count anomalies by type (from reasons array)
        const typeCounts: Record<string, number> = {}

        anomalies.value.forEach(anomaly => {
            anomaly.reasons.forEach(reason => {
                const typeStr = String(reason)
                typeCounts[typeStr] = (typeCounts[typeStr] || 0) + 1
            })
        })

        return typeCounts
    })

    // Actions
    async function fetchAnomalies(hours: number = 24, minScore: number = 0) {
        loading.value = true
        error.value = null

        try {
            const response = await api.get('/anomalies', {
                params: { hours, min_score: minScore, limit: 100 } // Request limit if backend supports it
            })
            // Cap at 100 strictly
            anomalies.value = response.data.slice(0, 100)
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

    function flushUpdates() {
        if (pendingAnomalies.length === 0) return

        // Prepend all pending anomalies
        // Create new array to trigger reactivity once
        const newAnomalies = [...pendingAnomalies, ...anomalies.value]

        // Cap at 100 items to prevent memory leaks and UI lag
        anomalies.value = newAnomalies.slice(0, 100)

        // Clear buffer
        pendingAnomalies.length = 0 // Clear in place
        flushTimer = null
    }

    function addAnomaly(anomaly: AnomalyEvent) {
        // Queue update
        pendingAnomalies.unshift(anomaly) // Add to front of batch

        // Schedule flush if not already scheduled
        if (!flushTimer) {
            flushTimer = window.setTimeout(flushUpdates, 1000) // 1 second batch window (slower than vessels to allow reading)
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
        anomaliesByHour,
        anomaliesByType,

        // Actions
        fetchAnomalies,
        fetchDashboardStats,
        addAnomaly
    }
})

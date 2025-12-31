/**
 * Get color for vessel status
 */
export function getVesselStatusColor(anomalyScore: number, isAnomaly: boolean): string {
    if (!isAnomaly) return '#10b981' // Green - normal
    if (anomalyScore >= 0.8) return '#ef4444' // Red - critical
    if (anomalyScore >= 0.5) return '#f59e0b' // Orange - warning
    return '#10b981' // Green - normal
}

/**
 * Get heatmap color based on count
 */
export function getHeatmapColor(count: number): string {
    if (count === 0) return '#1e40af' // Blue - calm
    if (count < 5) return '#3b82f6' // Light blue
    if (count < 10) return '#fbbf24' // Yellow - monitored
    if (count < 20) return '#f59e0b' // Orange
    return '#ef4444' // Red - critical
}

/**
 * Maritime color palette
 */
export const colors = {
    // Vessel status
    vesselNormal: '#10b981',
    vesselWarning: '#f59e0b',
    vesselDanger: '#ef4444',
    vesselSelected: '#00d4ff',
    vesselStale: '#6b7280',

    // Backgrounds
    bgPrimary: '#0a0e1a',
    bgSecondary: '#141b2d',
    bgTertiary: '#1e293b',

    // Text
    textPrimary: '#f1f5f9',
    textSecondary: '#94a3b8',
    textMuted: '#64748b',

    // Accents
    accentPrimary: '#00d4ff',
    accentWarning: '#ff6b35',
    accentSuccess: '#10b981',
    accentDanger: '#ef4444',
}

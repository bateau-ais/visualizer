export interface AnomalyEvent {
    data_id: string
    mmsi: number
    timestamp: string
    score: number
    reasons: string[]
    confidence: number
    vessel_name?: string
    lat?: number
    lon?: number
}

export interface HeatmapCell {
    lat_min: number
    lat_max: number
    lon_min: number
    lon_max: number
    count: number
    avg_score: number
    top_types: string[]
}

export interface AnomalyFilter {
    minScore: number
    types: string[]
    period: string
}

export interface DashboardStats {
    vessels_active: number
    anomalies_24h: number
    detection_rate: number
    critical_count: number
}

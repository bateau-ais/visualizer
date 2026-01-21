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
    acknowledged: boolean
}

export interface Stats {
    vessels_active: number
    anomalies_24h: number
    detection_rate: number
    critical_count: number
    timestamp: string
}

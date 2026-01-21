export interface Vessel {
    mmsi: number
    name?: string
    imo?: number
    type: string
    flag?: string
    lat: number
    lon: number
    sog: number
    cog: number
    heading: number
    timestamp: string
    anomaly_score: number
    is_anomaly: boolean
    status?: string
    acknowledged?: boolean
    acknowledged_at?: string
    trajectory?: TrajectoryPoint[]
    photo_url?: string
}

export interface VesselSummary {
    mmsi: number
    name?: string
    type: string
    lat: number
    lon: number
    is_anomaly: boolean
    anomaly_score: number
    acknowledged: boolean
}

export interface VesselDetails extends Vessel {
    dimensions?: {
        length: number
        beam: number
        draft: number
    }
    trajectory?: TrajectoryPoint[]
    anomalies?: Anomaly[]
    photo_url?: string
}

export interface TrajectoryPoint {
    lat: number
    lon: number
    timestamp: string
    sog?: number
    cog?: number
}

export interface Anomaly {
    timestamp: string
    score: number
    reasons: string[]
    details?: string
    confidence: number
}

export interface VesselFilter {
    types: string[]
    statuses: string[]
    minSpeed: number
    maxSpeed: number
    period: string
}

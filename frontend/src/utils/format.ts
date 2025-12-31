import { format as dateFnsFormat, formatDistanceToNow, parseISO } from 'date-fns'

/**
 * Format coordinates to degrees/minutes format
 */
export function formatCoordinates(lat: number, lon: number): string {
    const latDir = lat >= 0 ? 'N' : 'S'
    const lonDir = lon >= 0 ? 'E' : 'W'

    const latAbs = Math.abs(lat)
    const lonAbs = Math.abs(lon)

    const latDeg = Math.floor(latAbs)
    const latMin = ((latAbs - latDeg) * 60).toFixed(3)

    const lonDeg = Math.floor(lonAbs)
    const lonMin = ((lonAbs - lonDeg) * 60).toFixed(3)

    return `${latDeg}°${latMin}'${latDir}, ${lonDeg}°${lonMin}'${lonDir}`
}

/**
 * Format speed in knots
 */
export function formatSpeed(knots: number): string {
    return `${knots.toFixed(1)} kt`
}

/**
 * Format course/heading in degrees
 */
export function formatCourse(degrees: number): string {
    return `${Math.round(degrees)}°`
}

/**
 * Format timestamp relative to now
 */
export function formatRelativeTime(timestamp: string | Date): string {
    const date = typeof timestamp === 'string' ? parseISO(timestamp) : timestamp
    return formatDistanceToNow(date, { addSuffix: true })
}

/**
 * Format timestamp absolute
 */
export function formatDateTime(timestamp: string | Date): string {
    const date = typeof timestamp === 'string' ? parseISO(timestamp) : timestamp
    return dateFnsFormat(date, 'yyyy-MM-dd HH:mm:ss')
}

/**
 * Get cardinal direction from degrees
 */
export function getCardinalDirection(degrees: number): string {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
        'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    const index = Math.round(degrees / 22.5) % 16
    return directions[index]
}

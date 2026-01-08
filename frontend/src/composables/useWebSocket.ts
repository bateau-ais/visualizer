import { ref } from 'vue'
import { useVesselsStore } from '@/stores/vessels'
import { useAnomaliesStore } from '@/stores/anomalies'

export function useWebSocket() {
    const socket = ref<WebSocket | null>(null)
    const connected = ref(false)

    const vesselsStore = useVesselsStore()
    const anomaliesStore = useAnomaliesStore()

    function connect() {
        // Determine correct WebSocket URL
        // In dev mode (Vite typically 5173), connect directly to backend (8000) to avoid proxy issues
        let wsUrl: string
        if (window.location.port === '5173') {
            wsUrl = 'ws://localhost:8000/ws'
        } else {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
            wsUrl = `${protocol}//${window.location.host}/ws`
        }

        socket.value = new WebSocket(wsUrl)

        socket.value.onopen = () => {
            connected.value = true
            console.log('✅ WebSocket connected')
        }

        socket.value.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                handleMessage(data)
            } catch (err) {
                console.error('Failed to parse WebSocket message:', err)
            }
        }

        socket.value.onerror = (error) => {
            console.error('❌ WebSocket error:', error)
            connected.value = false
        }

        socket.value.onclose = () => {
            connected.value = false
            console.log('🔌 WebSocket disconnected, reconnecting in 5s...')

            // Auto-reconnect after 5 seconds
            setTimeout(() => {
                if (!connected.value) {
                    connect()
                }
            }, 5000)
        }
    }

    function handleMessage(data: any) {
        if (data.type === 'vessel_update') {
            vesselsStore.updateVessel(data.data)
        } else if (data.type === 'anomaly_detection') {
            // Trigger refetch (composable doesn't have direct store methods)
            // The stores will auto-refresh via their own polling
        }
    }

    function disconnect() {
        if (socket.value) {
            socket.value.close()
            socket.value = null
            connected.value = false
        }
    }

    return {
        socket,
        connected,
        connect,
        disconnect
    }
}

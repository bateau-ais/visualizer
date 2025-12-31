import { ref, onMounted, onUnmounted } from 'vue'
import { io, Socket } from 'socket.io-client'
import { useVesselsStore } from '@/stores/vessels'
import { useAnomaliesStore } from '@/stores/anomalies'

export function useWebSocket() {
    const socket = ref<Socket | null>(null)
    const connected = ref(false)

    const vesselsStore = useVesselsStore()
    const anomaliesStore = useAnomaliesStore()

    function connect() {
        socket.value = io('ws://localhost:8000', {
            transports: ['websocket'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5
        })

        socket.value.on('connect', () => {
            connected.value = true
            console.log('✅ WebSocket connected')
        })

        socket.value.on('disconnect', () => {
            connected.value = false
            console.log('❌ WebSocket disconnected')
        })

        socket.value.on('vessel_update', (data: any) => {
            vesselsStore.updateVessel(data.data)
        })

        socket.value.on('anomaly_detected', (data: any) => {
            anomaliesStore.addAnomaly(data.data)

            // Show notification
            showNotification(data.data)
        })

        // Heartbeat
        const heartbeat = setInterval(() => {
            if (socket.value?.connected) {
                socket.value.send('ping')
            }
        }, 30000)

        return heartbeat
    }

    function disconnect() {
        if (socket.value) {
            socket.value.disconnect()
            socket.value = null
            connected.value = false
        }
    }

    function showNotification(anomaly: any) {
        // TODO: Implement toast notification
        console.log('🔴 Anomaly detected:', anomaly)
    }

    return {
        socket,
        connected,
        connect,
        disconnect
    }
}

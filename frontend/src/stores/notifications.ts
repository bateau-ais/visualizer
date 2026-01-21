import { defineStore } from 'pinia'
import axios from 'axios'
import type { AnomalyEvent } from '@/types/anomalies'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useNotificationStore = defineStore('notifications', {
    state: () => ({
        notifications: [] as AnomalyEvent[],
        loading: false,
        error: null as string | null
    }),

    getters: {
        // Unread (unacknowledged) notifications for the popup/badge
        unreadNotifications: (state) => {
            return state.notifications.filter(n => !n.acknowledged)
        },

        // Count of unread notifications
        unreadCount: (state) => {
            return state.notifications.filter(n => !n.acknowledged).length
        }
    },

    actions: {
        async fetchNotifications() {
            this.loading = true
            try {
                // Fetch last 24h of anomalies to populate notifications
                const response = await axios.get(`${API_URL}/api/anomalies`, {
                    params: {
                        hours: 24,
                        limit: 50
                    }
                })
                this.notifications = response.data
            } catch (err) {
                console.error('Failed to fetch notifications:', err)
                this.error = 'Failed to load notifications'
            } finally {
                this.loading = false
            }
        },

        async acknowledge(mmsi: number) {
            try {
                await axios.post(`${API_URL}/api/vessels/${mmsi}/acknowledge`)

                // Update local state immediately for UI responsiveness
                const notification = this.notifications.find(n => n.mmsi === mmsi)
                if (notification) {
                    notification.acknowledged = true
                }
            } catch (err) {
                console.error(`Failed to acknowledge vessel ${mmsi}:`, err)
                throw err
            }
        },

        // Update local state without API call (called from other components that already did the API call)
        markAsReadLocal(mmsi: number) {
            const notification = this.notifications.find(n => n.mmsi === mmsi)
            if (notification) {
                notification.acknowledged = true
            }
        },

        // Add new notification (from websocket)
        addNotification(notification: AnomalyEvent) {
            // Check if exists to avoid duplicates
            const exists = this.notifications.some(n => n.data_id === notification.data_id)
            if (!exists) {
                this.notifications.unshift(notification)
            }
        }
    }
})

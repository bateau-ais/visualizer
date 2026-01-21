import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'Dashboard', // Changed from 'dashboard'
            component: () => import('@/views/Dashboard.vue'), // Assuming Dashboard.vue is the correct component
            meta: { title: 'Dashboard' }
        },
        {
            path: '/map',
            name: 'Map', // Changed from 'map'
            component: () => import('@/views/MapView.vue'),
            meta: { title: 'Live Map' } // Kept existing meta title
        },

        {
            path: '/vessel/:mmsi',
            name: 'vessel-history',
            component: () => import('@/views/VesselHistory.vue'),
            meta: { title: 'Vessel History' }
        },
        {
            path: '/docs/anomalies',
            name: 'anomaly-docs',
            component: () => import('@/views/AnomalyDocs.vue'),
            meta: { title: 'Anomaly Guide' }
        },
        {
            path: '/notifications',
            name: 'Notifications',
            component: () => import('@/views/NotificationsView.vue'),
            meta: { title: 'Notifications' }
        }
    ]
})

router.afterEach((to) => {
    document.title = `NOVA - ${to.meta.title || 'Visualizer'}`
})

export default router

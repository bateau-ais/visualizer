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
            path: '/heatmap',
            name: 'Heatmap', // Changed from 'heatmap'
            component: () => import('@/views/Heatmap.vue'),
            meta: { title: 'Anomaly Heatmap' }
        },
        {
            path: '/vessel/:mmsi',
            name: 'vessel-history',
            component: () => import('@/views/VesselHistory.vue'),
            meta: { title: 'Vessel History' }
        }
    ]
})

router.afterEach((to) => {
    document.title = `NOVA - ${to.meta.title || 'Visualizer'}`
})

export default router

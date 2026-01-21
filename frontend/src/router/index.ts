import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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
        },
        {
            path: '/login',
            name: 'Login',
            component: () => import('@/views/Login.vue'),
            meta: { title: 'Sign In', requiresAuth: false }
        }
    ]
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    // Check if route requires authentication (default: true)
    const requiresAuth = to.meta.requiresAuth !== false

    if (requiresAuth && !authStore.isAuthenticated) {
        // Redirect to login with return URL
        next({
            name: 'Login',
            query: { redirect: to.fullPath }
        })
    } else if (to.name === 'Login' && authStore.isAuthenticated) {
        // Redirect to home if already logged in
        next({ name: 'Dashboard' })
    } else {
        next()
    }
})

router.afterEach((to) => {
    document.title = `NOVA - ${to.meta.title || 'Visualizer'}`
})

export default router

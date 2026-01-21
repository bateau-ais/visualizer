/**
 * NOVA Visualizer - Authentication Store
 * =======================================
 * 
 * Pinia store for managing user authentication state.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export interface User {
    username: string
    role: 'viewer' | 'operator' | 'admin'
    last_login?: string
}

export const useAuthStore = defineStore('auth', () => {
    // State
    const token = ref<string | null>(localStorage.getItem('auth_token'))
    const user = ref<User | null>(null)
    const isLoading = ref(false)
    const error = ref<string | null>(null)

    // Getters
    const isAuthenticated = computed(() => !!token.value)
    const isAdmin = computed(() => user.value?.role === 'admin')
    const isOperator = computed(() => user.value?.role === 'operator' || user.value?.role === 'admin')

    // Actions
    async function login(username: string, password: string): Promise<boolean> {
        isLoading.value = true
        error.value = null

        try {
            const response = await api.post('/auth/login', { username, password })

            token.value = response.data.access_token
            user.value = response.data.user

            // Persist token
            localStorage.setItem('auth_token', response.data.access_token)

            console.log('✅ Login successful:', user.value)
            return true

        } catch (err: any) {
            error.value = err.response?.data?.detail || 'Login failed'
            console.error('❌ Login failed:', error.value)
            return false

        } finally {
            isLoading.value = false
        }
    }

    async function logout() {
        try {
            // Notify backend (optional, since JWT can't be invalidated server-side)
            if (token.value) {
                await api.post('/auth/logout')
            }
        } catch (err) {
            console.warn('Logout API call failed:', err)
        } finally {
            // Clear local state
            token.value = null
            user.value = null
            localStorage.removeItem('auth_token')

            console.log('✅ Logged out')
        }
    }

    async function fetchCurrentUser() {
        if (!token.value) return

        try {
            const response = await api.get('/auth/me')
            user.value = response.data

        } catch (err) {
            console.error('Failed to fetch current user:', err)
            // Token might be invalid, clear auth
            await logout()
        }
    }

    // Initialize user on store creation
    if (token.value) {
        fetchCurrentUser()
    }

    return {
        // State
        token,
        user,
        isLoading,
        error,

        // Getters
        isAuthenticated,
        isAdmin,
        isOperator,

        // Actions
        login,
        logout,
        fetchCurrentUser
    }
})

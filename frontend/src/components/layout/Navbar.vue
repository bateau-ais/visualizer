<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { Search, Bell, Menu, X } from 'lucide-vue-next'
import Input from '@/components/ui/Input.vue'
import Badge from '@/components/ui/Badge.vue'
import { useNotificationStore } from '@/stores/notifications'
import { storeToRefs } from 'pinia'

const route = useRoute()
const router = useRouter()
const store = useNotificationStore()
const { unreadCount, unreadNotifications } = storeToRefs(store)

const searchQuery = ref('')
const mobileMenuOpen = ref(false)
const notificationsOpen = ref(false)

onMounted(() => {
  store.fetchNotifications()
  // Poll every 30 seconds
  setInterval(() => store.fetchNotifications(), 30000)
})

const navigation = [
  { name: 'Dashboard', path: '/' },
  { name: 'Live Map', path: '/map' },

  { name: 'Anomaly Guide', path: '/docs/anomalies' }
]

function isActive(path: string) {
  return route.path === path
}

function navigateToVessel(mmsi: number) {
  window.location.href = `/vessel/${mmsi}`
  notificationsOpen.value = false
}

function viewAllNotifications() {
  router.push('/notifications')
  notificationsOpen.value = false
}
</script>

<template>
  <nav class="fixed top-0 left-0 right-0 z-[2000] bg-bg-secondary/95 backdrop-blur-md border-b border-gray-700 h-16">
    <div class="max-w-full px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo & Brand -->
        <div class="flex items-center space-x-8">
          <RouterLink to="/" class="flex items-center space-x-3 group">
            <div class="w-8 h-8 bg-accent-primary rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <span class="text-bg-primary font-bold text-lg">N</span>
            </div>
            <span class="text-xl font-bold text-text-primary hidden sm:block">
              NOVA <span class="text-accent-primary">Visualizer</span>
            </span>
          </RouterLink>
          
          <!-- Desktop Navigation -->
          <div class="hidden md:flex space-x-1">
            <RouterLink
              v-for="item in navigation"
              :key="item.path"
              :to="item.path"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive(item.path)
                  ? 'bg-bg-tertiary text-accent-primary'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary/50'
              ]"
            >
              {{ item.name }}
            </RouterLink>
          </div>
        </div>
        
        <!-- Search & Actions -->
        <div class="flex items-center space-x-4">
          <!-- Search bar (desktop) -->
          <div class="hidden lg:block w-64">
            <div class="relative">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <Input
                v-model="searchQuery"
                type="search"
                placeholder="Search MMSI or name..."
                class="pl-10"
              />
            </div>
          </div>
          
          <!-- Notifications -->
          <button
            class="relative p-2 text-text-secondary hover:text-text-primary hover:bg-bg-tertiary rounded-lg transition-colors"
            @click="notificationsOpen = !notificationsOpen"
          >
            <Bell class="w-5 h-5" />
            <Badge
              v-if="unreadCount > 0"
              variant="danger"
              size="sm"
              class="absolute -top-1 -right-1"
            >
              {{ unreadCount }}
            </Badge>
          </button>
          
          <!-- Mobile menu button -->
          <button
            class="md:hidden p-2 text-text-secondary hover:text-text-primary hover:bg-bg-tertiary rounded-lg"
            @click="mobileMenuOpen = !mobileMenuOpen"
          >
            <Menu v-if="!mobileMenuOpen" class="w-6 h-6" />
            <X v-else class="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
    
    <!-- Mobile menu -->
    <div
      v-if="mobileMenuOpen"
      class="md:hidden border-t border-gray-700 bg-bg-secondary"
    >
      <div class="px-4 py-3 space-y-1">
        <RouterLink
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          :class="[
            'block px-4 py-2 rounded-lg text-base font-medium transition-colors',
            isActive(item.path)
              ? 'bg-bg-tertiary text-accent-primary'
              : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary/50'
          ]"
          @click="mobileMenuOpen = false"
        >
          {{ item.name }}
        </RouterLink>
      </div>
      
      <!-- Mobile search -->
      <div class="px-4 pb-3">
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <Input
            v-model="searchQuery"
            type="search"
            placeholder="Search MMSI or name..."
            class="pl-10"
          />
        </div>
      </div>
    </div>
    
    <!-- Notifications Panel -->
    <div
      v-if="notificationsOpen"
      class="absolute top-16 right-4 w-96 max-h-[500px] overflow-y-auto bg-bg-secondary border border-gray-700 rounded-lg shadow-xl z-50"
    >
      <div class="p-4 border-b border-gray-700 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-text-primary">Notifications</h3>
        <button
          @click="notificationsOpen = false"
          class="text-text-muted hover:text-text-primary"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
      
      <div class="divide-y divide-gray-700">
        <!-- Notification list -->
        <div v-if="unreadCount === 0" class="p-8 text-center text-text-muted">
          No new notifications
        </div>
        
        <!-- Only show unread notifications in popup -->
        <div 
          v-for="notification in unreadNotifications.slice(0, 5)" 
          :key="notification.data_id"
          class="p-4 hover:bg-bg-tertiary/50 transition-colors cursor-pointer group relative"
          @click="navigateToVessel(notification.mmsi)"
        >
          <div class="flex items-start gap-3 pr-6">
            <div class="w-2 h-2 rounded-full bg-accent-danger mt-1.5 shrink-0"></div>
            <div>
              <p class="text-sm font-medium text-text-primary">
                {{ notification.vessel_name || `Vessel ${notification.mmsi}` }}
              </p>
              <p class="text-xs text-text-secondary mt-1 line-clamp-2">
                {{ notification.reasons.join(', ') }}
              </p>
              <p class="text-xs text-text-muted mt-1">
                {{ new Date(notification.timestamp).toLocaleTimeString() }}
              </p>
            </div>
          </div>
          
          <!-- Dismiss Button -->
          <button 
            @click.stop="store.dismissNotification(notification.data_id)"
            class="absolute top-4 right-4 p-1 text-text-muted hover:text-text-primary opacity-0 group-hover:opacity-100 transition-opacity"
            title="Dismiss"
          >
            <X class="w-3 h-3" />
          </button>
        </div>
      </div>
      
      <div class="p-3 border-t border-gray-700 text-center">
        <button 
          @click="viewAllNotifications"
          class="text-xs text-accent-primary hover:underline"
        >
          View all notifications
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { Search, Bell, Menu, X } from 'lucide-vue-next'
import Input from '@/components/ui/Input.vue'
import Badge from '@/components/ui/Badge.vue'

const route = useRoute()
const searchQuery = ref('')
const mobileMenuOpen = ref(false)
const notificationCount = ref(3)

const navigation = [
  { name: 'Dashboard', path: '/' },
  { name: 'Live Map', path: '/map' },
  { name: 'Heatmap', path: '/heatmap' }
]

function isActive(path: string) {
  return route.path === path
}
</script>

<template>
  <nav class="fixed top-0 left-0 right-0 z-50 bg-bg-secondary/95 backdrop-blur-md border-b border-gray-700 h-16">
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
          >
            <Bell class="w-5 h-5" />
            <Badge
              v-if="notificationCount > 0"
              variant="danger"
              size="sm"
              class="absolute -top-1 -right-1"
            >
              {{ notificationCount }}
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
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { X, AlertTriangle, Info, CheckCircle } from 'lucide-vue-next'

interface Notification {
  id: string
  type: 'info' | 'warning' | 'danger' | 'success'
  title: string
  message: string
  timestamp: Date
}

const notifications = ref<Notification[]>([])

function addNotification(notification: Omit<Notification, 'id' | 'timestamp'>) {
  const newNotification: Notification = {
    ...notification,
    id: Math.random().toString(36).substr(2, 9),
    timestamp: new Date()
  }
  
  notifications.value.unshift(newNotification)
  
  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    removeNotification(newNotification.id)
  }, 5000)
}

function removeNotification(id: string) {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index !== -1) {
    notifications.value.splice(index, 1)
  }
}

function getIcon(type: string) {
  const icons = {
    info: Info,
    warning: AlertTriangle,
    danger: AlertTriangle,
    success: CheckCircle
  }
  return icons[type as keyof typeof icons] || Info
}

function getColors(type: string) {
  const colors = {
    info: 'bg-accent-primary/10 border-accent-primary/30 text-accent-primary',
    warning: 'bg-accent-warning/10 border-accent-warning/30 text-accent-warning',
    danger: 'bg-accent-danger/10 border-accent-danger/30 text-accent-danger',
    success: 'bg-accent-success/10 border-accent-success/30 text-accent-success'
  }
  return colors[type as keyof typeof colors] || colors.info
}

// Expose method to parent
defineExpose({
  addNotification
})
</script>

<template>
  <div class="fixed top-20 right-4 z-50 space-y-2 max-w-sm">
    <TransitionGroup name="slide-fade">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'glass rounded-lg border p-4 shadow-2xl',
          getColors(notification.type)
        ]"
      >
        <div class="flex items-start space-x-3">
          <component
            :is="getIcon(notification.type)"
            class="w-5 h-5 flex-shrink-0 mt-0.5"
          />
          
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-sm">{{ notification.title }}</p>
            <p class="text-sm opacity-90 mt-1">{{ notification.message }}</p>
          </div>
          
          <button
            class="flex-shrink-0 hover:opacity-70 transition-opacity"
            @click="removeNotification(notification.id)"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>

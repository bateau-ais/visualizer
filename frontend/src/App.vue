<script setup lang="ts">
import { RouterView } from 'vue-router'
import Navbar from '@/components/layout/Navbar.vue'
import NotificationCenter from '@/components/layout/NotificationCenter.vue'
</script>

<template>
  <div class="min-h-screen bg-bg-primary">
    <Navbar />
    
    <main class="pt-16">
      <RouterView v-slot="{ Component }">
        <KeepAlive include="MapView">
          <component :is="Component" />
        </KeepAlive>
      </RouterView>
    </main>
    
    <NotificationCenter />
  </div>
</template>

<style scoped>
/* App-specific styles */
</style>

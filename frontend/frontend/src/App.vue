<template>
  <div id="app">
    <!-- Loading state to prevent flash -->
    <div v-if="isLoading" class="app-loading">
      <div class="loading-spinner"></div>
    </div>
    
    <!-- Main content -->
    <template v-else>
      <Navbar v-show="!isAdminRoute" />
      <router-view />
      <Footer v-show="!isAdminRoute" />
    </template>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    Footer
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const isLoading = ref(true)
    const isAdminRoute = ref(false)

    // Check if current path is an admin route
    const checkAdminRoute = (path) => {
      const adminPrefixes = ['/admin', '/partner', '/tour-manager']
      return adminPrefixes.some(prefix => path.startsWith(prefix))
    }

    // Update admin route status
    const updateAdminStatus = (path) => {
      isAdminRoute.value = checkAdminRoute(path)
    }

    // Watch for route changes
    watch(
      () => route.path,
      (newPath) => {
        updateAdminStatus(newPath)
      },
      { immediate: true }
    )

    // Handle initial load
    onMounted(async () => {
      // Set initial admin status
      updateAdminStatus(route.path)
      
      // Wait for router to be ready
      await router.isReady()
      
      // Allow the app to render
      await nextTick()
      
      // Hide loading state
      isLoading.value = false
    })

    return {
      isLoading,
      isAdminRoute
    }
  }
}
</script>

<style>
/* Reset and base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f8fafc;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Loading state */
.app-loading {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  z-index: 9999;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
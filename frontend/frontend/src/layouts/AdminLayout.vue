<!-- frontend/src/layouts/AdminLayout.vue -->

<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <AdminSidebar 
      ref="sidebarRef"
      :components="userComponents" 
      :active-component="activeComponent"
      @navigate="handleNavigate"
      @toggle="handleSidebarToggle"
    />

    <!-- Main Content -->
    <div class="main-content" :class="{ 'sidebar-open': isMobileSidebarOpen }">
      <!-- Navbar -->
      <AdminNavbar 
        :user="user" 
        @toggle-sidebar="toggleSidebar"
      />

      <!-- Content -->
      <div class="content-area">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import authService from '@/services/auth'
import permissionService from '@/services/permissionService'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'

const router = useRouter()
const route = useRoute()
const sidebarRef = ref(null)
const user = ref(null)
const userComponents = ref([])
const activeComponent = ref('overview')
const isMobileSidebarOpen = ref(false)
const isMobile = ref(window.innerWidth < 768)
const isLoading = ref(true)

// Load user components based on role
const loadUserComponents = async () => {
  try {
    isLoading.value = true
    
    // ✅ Initialize permission service
    await permissionService.init()
    
    // ✅ Get components based on user's role
    const components = permissionService.getDashboardComponents()
    userComponents.value = components
    
    // ✅ Get the user's role for debugging
    const userRole = permissionService.getUserRole()
    console.log('📋 Current User Role:', userRole)
    console.log('📦 Available Components:', components.map(c => c.key))
    
    // ✅ Set default active component
    if (components.length > 0) {
      // Check if current tab is valid for this role
      const currentTab = route.query.tab
      const validTab = components.some(c => c.key === currentTab)
      
      if (!validTab || !currentTab) {
        activeComponent.value = components[0].key
        // Update URL if needed
        if (!currentTab || !validTab) {
          router.replace({
            path: '/admin/dashboard',
            query: { tab: components[0].key }
          })
        }
      } else {
        activeComponent.value = currentTab
      }
    }
  } catch (error) {
    console.error('Error loading components:', error)
    // Fallback: get default components for user's role
    const userData = authService.getUser()
    const role = userData?.role || 'user'
    userComponents.value = permissionService.getDefaultComponentsForRole(role)
  } finally {
    isLoading.value = false
  }
}

const handleNavigate = (componentKey) => {
  activeComponent.value = componentKey
  router.push({
    path: '/admin/dashboard',
    query: { tab: componentKey }
  })
}

const toggleSidebar = () => {
  if (isMobile.value) {
    if (sidebarRef.value) {
      sidebarRef.value.toggleMobile()
    }
  } else {
    if (sidebarRef.value) {
      sidebarRef.value.isCollapsed = !sidebarRef.value.isCollapsed
    }
  }
}

const handleSidebarToggle = (isOpen) => {
  isMobileSidebarOpen.value = isOpen
}

const handleResize = () => {
  const wasMobile = isMobile.value
  isMobile.value = window.innerWidth < 768
  
  if (wasMobile && !isMobile.value && isMobileSidebarOpen.value) {
    if (sidebarRef.value) {
      sidebarRef.value.closeMobile()
    }
  }
}

// Watch route changes to update active component
watch(() => route.query.tab, (tab) => {
  if (tab && userComponents.value.some(c => c.key === tab)) {
    activeComponent.value = tab
  }
})

// Also watch for route path changes
watch(() => route.path, () => {
  // Re-check if we need to update the active component
  const tab = route.query.tab
  if (tab && userComponents.value.some(c => c.key === tab)) {
    activeComponent.value = tab
  }
})

// Handle component reload after login
const handleComponentReload = () => {
  // Re-load components when user navigates back to admin
  if (authService.isAuthenticated()) {
    loadUserComponents()
  }
}

onMounted(() => {
  user.value = authService.getUser()
  loadUserComponents()
  window.addEventListener('resize', handleResize)
  
  // Listen for login/role changes
  window.addEventListener('storage', handleComponentReload)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('storage', handleComponentReload)
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #f8fafc;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 280px;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 100vh;
}

.main-content.sidebar-open {
  margin-left: 0;
}

.content-area {
  flex: 1;
  padding: 24px;
  background: #f8fafc;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0 !important;
  }
  
  .content-area {
    padding: 16px;
  }
}
</style>
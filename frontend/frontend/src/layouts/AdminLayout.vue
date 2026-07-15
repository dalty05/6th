<!-- frontend/src/layouts/AdminLayout.vue -->

<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <AdminSidebar 
      :components="userComponents" 
      :active-component="activeComponent"
      @navigate="handleNavigate"
    />

    <!-- Main Content -->
    <div class="main-content">
      <!-- Navbar -->
      <AdminNavbar 
        :user="user" 
        @logout="handleLogout"
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
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import authService from '@/services/auth'
import permissionService from '@/services/permissionService'
import AdminSidebar from '@/components/admin/AdminSidebar.vue'
import AdminNavbar from '@/components/admin/AdminNavbar.vue'

const router = useRouter()
const route = useRoute()
const user = ref(null)
const userComponents = ref([])
const activeComponent = ref('overview')
const sidebarCollapsed = ref(false)

const loadUserComponents = async () => {
  try {
    // Get components from permission service (which gets them from backend)
    await permissionService.loadPermissions()
    const components = permissionService.getDashboardComponents()
    userComponents.value = components
  } catch (error) {
  }
}

const handleNavigate = (componentKey) => {
  activeComponent.value = componentKey
  router.push({
    path: '/admin/dashboard',
    query: { tab: componentKey }
  })
}

const handleLogout = async () => {
  await authService.logout()
  router.push('/admin/login')
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

onMounted(() => {
  user.value = authService.getUser()
  loadUserComponents()
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #f1f5f9;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 280px;
  transition: margin-left 0.3s ease;
}

.content-area {
  padding: 24px;
  flex: 1;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
}
</style>
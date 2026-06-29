<template>
  <div class="tour-manager-layout">
    <!-- Navbar -->
    <TourManagerNavbar @toggleSidebar="toggleSidebar" />

    <!-- Sidebar -->
    <TourManagerSidebar 
      ref="sidebarRef"
      :activeTab="activeTab" 
      @navigate="handleNavigate"
    />

    <!-- Main Content -->
    <div class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <div class="content-wrapper">
        <router-view />
      </div>
    </div>
  </div>
</template>



<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import authService from '@/services/auth'
import TourManagerNavbar from '@/components/tour-manager/TourManagerNavbar.vue'
import TourManagerSidebar from '@/components/tour-manager/TourManagerSidebar.vue'

const route = useRoute()
const router = useRouter()
const sidebarCollapsed = ref(false)
const user = ref(null)

const activeTab = computed(() => {
  const path = route.path
  if (path.includes('/tour-manager/bookings')) return 'bookings'
  if (path.includes('/tour-manager/calendar')) return 'calendar'
  if (path.includes('/tour-manager/packages')) return 'packages'
  if (path.includes('/tour-manager/payments')) return 'payments'
  if (path.includes('/tour-manager/reports')) return 'reports'
  return 'dashboard'
})

const handleNavigate = (tab) => {
  router.push(`/tour-manager/${tab}`)
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

onMounted(() => {
  user.value = authService.getUser()
  console.log('🔍 Layout mounted - user:', user.value)
  
  // ✅ FIX: Check BOTH role AND flag
  const hasAccess = user.value?.role === 'tour_manager' ||
                    user.value?.role === 'tour_assistant' ||
                    user.value?.role === 'admin' ||
                    user.value?.role === 'super_admin' ||
                    user.value?.is_tour_manager === true ||
                    user.value?.is_tour_assistant === true
  
  if (!hasAccess) {
    console.log('❌ No tour access, redirecting')
    router.push('/admin/dashboard')
  } else {
    console.log('✅ Tour access granted')
  }
})
</script>

<style scoped>
.tour-manager-layout {
  min-height: 100vh;
  background: #f8fafc;
}

.main-content {
  margin-left: 260px;
  padding: 80px 1.5rem 0;
  transition: margin-left 0.3s ease;
  min-height: 100vh;
}

.main-content.sidebar-collapsed {
  margin-left: 80px;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding-bottom: 2rem;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    padding: 70px 1rem 0;
  }
}
</style>
<!-- frontend/src/views/admin/Dashboard.vue -->

<template>
  <div class="admin-dashboard">
    <component 
      :is="currentComponent" 
      v-if="currentComponent"
      :key="activeComponent"
    />
    <div v-else class="no-component">
      <i class="fas fa-cube"></i>
      <h3>Select a component</h3>
      <p>Choose an option from the sidebar to get started</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import permissionService from '@/services/permissionService'

const route = useRoute()
const router = useRouter()
const activeComponent = ref('overview')

// Dynamic component loader
const componentMap = {
  'overview': defineAsyncComponent(() => import('@/components/admin/Overview.vue')),
  'products': defineAsyncComponent(() => import('@/components/admin/ProductsManagement.vue')),
  'blog': defineAsyncComponent(() => import('@/components/admin/BlogManagement.vue')),
  'jobs': defineAsyncComponent(() => import('@/components/admin/JobManagement.vue')),
  'outlets': defineAsyncComponent(() => import('@/components/admin/OutletManagement.vue')),
  'statistics': defineAsyncComponent(() => import('@/components/admin/AdvancedAnalytics.vue')),
  'contacts': defineAsyncComponent(() => import('@/components/admin/ContactManagement.vue')),
  'newsletter': defineAsyncComponent(() => import('@/components/admin/NewsletterManagement.vue')),
  'users': defineAsyncComponent(() => import('@/components/admin/UserManagement.vue')),
  'permissions': defineAsyncComponent(() => import('@/components/admin/PermissionManager.vue')),
  'roles': defineAsyncComponent(() => import('@/components/admin/RoleManager.vue')),
  
  // ✅ Tour components (moved from tour-manager views)
  'tours': defineAsyncComponent(() => import('@/components/admin/TourManagerBookings.vue')),
  'tour-packages': defineAsyncComponent(() => import('@/components/admin/TourManagerPackages.vue')),
  'tour-calendar': defineAsyncComponent(() => import('@/components/admin/TourManagerCalendar.vue')),
  'tour-payments': defineAsyncComponent(() => import('@/components/admin/TourManagerPayments.vue')),
  'tour-reports': defineAsyncComponent(() => import('@/components/admin/TourManagerReports.vue')),
  'tour-staff': defineAsyncComponent(() => import('@/components/admin/TourStaffManagement.vue')),
  
  // ✅ Partner components
  'partners': defineAsyncComponent(() => import('@/components/admin/PartnerManagement.vue')),
  'partner-links': defineAsyncComponent(() => import('@/components/admin/PartnerReferralLinks.vue')),
  'partner-analytics': defineAsyncComponent(() => import('@/components/admin/PartnerAnalytics.vue')),
  
  // ✅ Profile
  'profile': defineAsyncComponent(() => import('@/components/admin/MyProfile.vue')),
  'activities': defineAsyncComponent(() => import('@/components/admin/Activities.vue')),


}
const currentComponent = computed(() => {
  if (!activeComponent.value) return null
  return componentMap[activeComponent.value] || null
})

// Load component from URL query
watch(() => route.query.tab, (tab) => {
  if (tab && componentMap[tab]) {
    activeComponent.value = tab
  } else if (!tab) {
    // Set default to first available component
    const components = permissionService.getDashboardComponents() || []
    if (components.length > 0) {
      activeComponent.value = components[0].key
    }
  }
}, { immediate: true })

onMounted(() => {
  // If no tab in URL, set default
  if (!route.query.tab) {
    const components = permissionService.getDashboardComponents() || []
    if (components.length > 0) {
      const defaultTab = components[0].key
      router.replace({
        path: '/admin/dashboard',
        query: { tab: defaultTab }
      })
    }
  }
})
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
}

.no-component {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #94a3b8;
}

.no-component i {
  font-size: 48px;
  margin-bottom: 16px;
}

.no-component h3 {
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.no-component p {
  margin: 0;
}
</style>
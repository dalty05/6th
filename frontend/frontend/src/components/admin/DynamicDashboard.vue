<template>
  <div class="dynamic-dashboard">
    <!-- Navbar -->
    <AdminNavbar @toggleSidebar="toggleMobileSidebar" />
    
    <!-- Sidebar -->
    <DynamicSidebar 
      :activeComponent="activeComponent" 
      @navigate="handleNavigate"
      ref="sidebarRef"
    />
    
    <!-- Content -->
    <div class="dashboard-content" :class="{ 'sidebar-collapsed': sidebarCollapsed, 'mobile-open': mobileSidebarOpen }">
      <div class="content-wrapper">
        <!-- Page Header -->
        <div class="page-header">
          <h1>{{ pageTitle || 'Dashboard' }}</h1>
          <p>{{ pageSubtitle || 'Welcome to your dashboard' }}</p>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading dashboard...</p>
        </div>

        <!-- Dynamic Components -->
        <div v-else class="tab-content">
          <component 
            :is="currentComponent" 
            v-if="currentComponent"
            :key="activeComponent"
            @refresh="refreshData"
          />
          
          <!-- Component Not Found -->
          <div v-else class="not-found">
            <i class="fas fa-cube"></i>
            <h3>Component Not Found</h3>
            <p>The component could not be loaded.</p>
            <p class="debug-info">Active component: {{ activeComponent }}</p>
            <p class="debug-info">Available components: {{ componentList ? componentList.join(', ') : 'None' }}</p>
            <button @click="debugMode = true" class="btn-debug" v-if="!debugMode">Show Debug Info</button>
          </div>
        </div>
      </div>
      
      <AdminFooter />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, markRaw, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import authService from '@/services/auth'
import permissionService from '@/services/permissionService'
import AdminNavbar from '@/components/layout/AdminNavbar.vue'
import AdminFooter from '@/components/layout/AdminFooter.vue'
import DynamicSidebar from '@/components/admin/DynamicSidebar.vue'

// ============================================================
// COMPONENT REGISTRY
// ============================================================

const componentMap = {
  'Overview': defineAsyncComponent(() => import('@/components/admin/Overview.vue')),
  'ProductsManagement': defineAsyncComponent(() => import('@/components/admin/ProductsManagement.vue')),
  'BlogManagement': defineAsyncComponent(() => import('@/components/admin/BlogManagement.vue')),
  'JobManagement': defineAsyncComponent(() => import('@/components/admin/JobManagement.vue')),
  'OutletManagement': defineAsyncComponent(() => import('@/components/admin/OutletManagement.vue')),
  'AdvancedAnalytics': defineAsyncComponent(() => import('@/components/admin/AdvancedAnalytics.vue')),
  'ContactManagement': defineAsyncComponent(() => import('@/components/admin/ContactManagement.vue')),
  'NewsletterManagement': defineAsyncComponent(() => import('@/components/admin/NewsletterManagement.vue')),
  'UserManagement': defineAsyncComponent(() => import('@/components/admin/UserManagement.vue')),
  'PermissionManager': defineAsyncComponent(() => import('@/components/admin/PermissionManager.vue')),
  'RoleManager': defineAsyncComponent(() => import('@/components/admin/RoleManager.vue')),
  'TourManagerBookings': defineAsyncComponent(() => import('@/views/tour-manager/TourManagerBookings.vue')),
  'TourManagerPackages': defineAsyncComponent(() => import('@/views/tour-manager/TourManagerPackages.vue')),
  'TourManagerCalendar': defineAsyncComponent(() => import('@/views/tour-manager/TourManagerCalendar.vue')),
  'TourManagerPayments': defineAsyncComponent(() => import('@/views/tour-manager/TourManagerPayments.vue')),
  'TourManagerReports': defineAsyncComponent(() => import('@/views/tour-manager/TourManagerReports.vue')),
  'TourStaffManagement': defineAsyncComponent(() => import('@/components/admin/TourStaffManagement.vue')),
  'PartnerManagement': defineAsyncComponent(() => import('@/components/admin/PartnerManagement.vue')),
  'MyProfile': defineAsyncComponent(() => import('@/components/admin/MyProfile.vue')),
  'Activities': defineAsyncComponent(() => import('@/components/admin/Activities.vue')),
  'PartnerDashboard': defineAsyncComponent(() => import('@/views/partner/Dashboard.vue')),
  'PartnerReferralLinks': defineAsyncComponent(() => import('@/views/partner/ReferralLinks.vue')),
  'PartnerAnalytics': defineAsyncComponent(() => import('@/views/partner/Analytics.vue')),
  'PartnerProfile': defineAsyncComponent(() => import('@/views/partner/Profile.vue')),
  'PartnerHelp': defineAsyncComponent(() => import('@/views/partner/Help.vue')),
}

const route = useRoute()
const router = useRouter()

// ========== STATE ==========
const activeComponent = ref('overview')
const components = ref([])
const roleName = ref('')
const loading = ref(true)
const debugMode = ref(false)
const sidebarCollapsed = ref(false)
const mobileSidebarOpen = ref(false)
const sidebarRef = ref(null)

// ========== COMPUTED ==========
const currentComponentData = computed(() => {
  if (!components.value || components.value.length === 0) return null
  return components.value.find(c => c.key === activeComponent.value) || null
})

const currentComponent = computed(() => {
  const compData = currentComponentData.value
  if (!compData) return null
  
  const componentName = compData.component_name
  const importFn = componentMap[componentName]
  
  if (!importFn) {
    console.warn(`❌ Component "${componentName}" not found in componentMap`)
    console.log('📋 Available components:', Object.keys(componentMap))
    return null
  }
  
  console.log(`✅ Loading component: ${componentName}`)
  return markRaw(importFn)
})

const componentList = computed(() => {
  if (!components.value || components.value.length === 0) return []
  return components.value.map(c => c.component_name).filter(Boolean)
})

const pageTitle = computed(() => {
  const data = currentComponentData.value
  return data?.label || 'Dashboard'
})

const pageSubtitle = computed(() => {
  const data = currentComponentData.value
  return data?.description || `Welcome to your ${roleName.value || 'Dashboard'}`
})

// ========== METHODS ==========
const loadDashboard = async () => {
  loading.value = true
  try {
    if (!permissionService.isDashboardLoaded()) {
      await permissionService.loadPermissions()
    }
    
    components.value = permissionService.getDashboardComponents() || []
    roleName.value = permissionService.getRoleName() || 'User'
    
    console.log('📋 Components loaded:', components.value.map(c => c.key))
    
    // Check URL params for component
    const tab = route.query.tab
    if (tab && components.value.some(c => c.key === tab)) {
      activeComponent.value = tab
    } else if (components.value.length > 0) {
      activeComponent.value = components.value[0].key
    }
    
    console.log('✅ Dashboard loaded:', components.value.length, 'components')
    console.log('🎯 Active component:', activeComponent.value)
    
  } catch (error) {
    console.error('Error loading dashboard:', error)
  } finally {
    loading.value = false
  }
}

const handleNavigate = (key) => {
  console.log('🔄 Dashboard navigating to:', key)
  
  const component = components.value.find(c => c.key === key)
  if (!component) {
    console.warn('⚠️ Component not found:', key)
    return
  }
  
  // ✅ Update active component
  activeComponent.value = key
  
  // ✅ Update URL with query param only
  router.push({ 
    path: '/admin/dashboard', 
    query: { tab: key } 
  })
  
  console.log('✅ Active component set to:', activeComponent.value)
}

const toggleMobileSidebar = () => {
  mobileSidebarOpen.value = !mobileSidebarOpen.value
  if (sidebarRef.value) {
    sidebarRef.value.isOpen = mobileSidebarOpen.value
  }
}

const refreshData = async () => {
  await loadDashboard()
}

// ========== WATCHERS ==========
watch(() => route.query.tab, (tab) => {
  if (tab && components.value.some(c => c.key === tab)) {
    console.log('🔄 Route tab changed to:', tab)
    activeComponent.value = tab
  }
})

// ========== LIFECYCLE ==========
onMounted(() => {
  if (!authService.isAuthenticated()) {
    router.push('/admin/login')
    return
  }
  loadDashboard()
})
</script>

<style scoped>
.dynamic-dashboard {
  min-height: 100vh;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
}

.dashboard-content {
  flex: 1;
  margin-left: 280px;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 64px);
}

.dashboard-content.sidebar-collapsed {
  margin-left: 64px;
}

.content-wrapper {
  flex: 1;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 4px 0;
}

.page-header p {
  color: #64748b;
  margin: 0;
  font-size: 16px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #94a3b8;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.tab-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  min-height: 400px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #94a3b8;
}

.not-found i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #cbd5e1;
}

.not-found h3 {
  margin: 0 0 8px 0;
  color: #1a1a2e;
}

.not-found p {
  margin: 4px 0;
}

.debug-info {
  font-size: 12px;
  color: #94a3b8;
  font-family: monospace;
}

.btn-debug {
  margin-top: 16px;
  padding: 8px 16px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  color: #64748b;
  font-size: 13px;
}

.btn-debug:hover {
  background: #e2e8f0;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .dashboard-content {
    margin-left: 0;
  }
  
  .dashboard-content.mobile-open {
    margin-left: 280px;
  }
  
  .content-wrapper {
    padding: 16px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
}
</style>
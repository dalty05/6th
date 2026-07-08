<template>
  <aside class="admin-sidebar" :class="{ collapsed: isCollapsed, mobile: isMobile }">
    <!-- Sidebar Header -->
    <div class="sidebar-header">
      <img src="/logo.png" alt="Meru Dairy" class="sidebar-logo">
      <div class="sidebar-brand" v-if="!isCollapsed">
        <h3>Meru Dairy</h3>
        <span>{{ roleName || 'Dashboard' }}</span>
      </div>
      <button class="sidebar-toggle" @click="toggleSidebar" v-if="!isMobile">
        <i :class="isCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"></i>
      </button>
    </div>

    <!-- User Profile -->
    <div class="user-profile" v-if="!isCollapsed">
      <div class="user-avatar">
        <i class="fas fa-user-circle"></i>
      </div>
      <div class="user-info">
        <h4>{{ user?.full_name || 'Administrator' }}</h4>
        <span class="user-role">
          <i class="fas fa-tag"></i> {{ formatRole(roleName) }}
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading...</p>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav" v-else>
      <div class="nav-section" v-for="section in groupedComponents" :key="section.name">
        <div class="nav-section-title" v-if="!isCollapsed">{{ section.name }}</div>
        
        <button
          v-for="component in section.components"
          :key="component.key"
          class="nav-item"
          :class="{ active: activeTab === component.key }"
          @click="navigate(component)"
        >
          <i :class="component.icon || 'fas fa-cube'"></i>
          <span v-if="!isCollapsed">{{ component.label }}</span>
          <span v-if="isCollapsed" class="tooltip">{{ component.label }}</span>
        </button>
      </div>

      <!-- Account Section -->
      <div class="nav-section" v-if="!isCollapsed">
        <div class="nav-section-title">Account</div>
        <button class="nav-item logout-btn" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i>
          <span>Logout</span>
        </button>
      </div>
    </nav>

    <!-- Mobile Overlay -->
    <div class="sidebar-overlay" v-if="isMobile && isOpen" @click="closeMobileSidebar"></div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/auth'
import api from '@/services/api'
import permissionService from '@/services/permissionService'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'overview'
  }
})

const emit = defineEmits(['navigate'])

const router = useRouter()
const user = ref(null)
const components = ref([])
const roleName = ref('')
const isCollapsed = ref(false)
const isMobile = ref(false)
const isOpen = ref(false)
const loading = ref(true)

// ========== LOAD DASHBOARD CONFIG ==========
const loadDashboardConfig = async () => {
  loading.value = true
  try {
    // Try to get config from permission service first
    if (permissionService.isDashboardLoaded()) {
      components.value = permissionService.getDashboardComponents()
      roleName.value = permissionService.getRoleName() || 'User'
      console.log('✅ Dashboard config loaded from cache:', components.value.length, 'components')
    } else {
      // Fallback to API call
      const response = await api.get('/dashboard/config')
      components.value = response.data.components || []
      roleName.value = response.data.role?.name || 'User'
      console.log('✅ Dashboard config loaded from API:', components.value.length, 'components')
    }
  } catch (error) {
    console.error('Error loading dashboard config:', error)
    // Fallback: Show overview only
    components.value = [{ key: 'overview', label: 'Overview', icon: 'fas fa-home', section: 'Main' }]
    roleName.value = 'User'
  } finally {
    loading.value = false
  }
}

// ========== GROUP COMPONENTS BY SECTION ==========
const groupedComponents = computed(() => {
  const groups = {}
  components.value.forEach(comp => {
    const section = comp.section || 'Main'
    if (!groups[section]) groups[section] = []
    groups[section].push(comp)
  })
  
  const sectionOrder = { 'Main': 0, 'Tours': 1, 'Administration': 2, 'Partner': 3 }
  const sortedEntries = Object.entries(groups).sort((a, b) => {
    const orderA = sectionOrder[a[0]] ?? 999
    const orderB = sectionOrder[b[0]] ?? 999
    return orderA - orderB || a[0].localeCompare(b[0])
  })
  
  return sortedEntries.map(([name, comps]) => ({
    name,
    components: comps.sort((a, b) => (a.order || 0) - (b.order || 0))
  }))
})

// ========== NAVIGATION ==========
const navigate = (component) => {
  console.log('🔄 Sidebar navigating to:', component.key)
  
  // Emit navigation event to parent
  emit('navigate', component.key)
  
  // ✅ Use query parameter ONLY - stay on the same page
  router.push({ 
    path: '/admin/dashboard', 
    query: { tab: component.key } 
  })
  
  if (isMobile.value) {
    isOpen.value = false
  }
}

// ========== SIDEBAR TOGGLE ==========
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('admin_sidebar_collapsed', isCollapsed.value)
}

const closeMobileSidebar = () => {
  isOpen.value = false
}

// ========== LOGOUT ==========
const handleLogout = async () => {
    await authService.logout()
  this.$router.push('/admin/login')
  router.push('/admin/login')
}

// ========== HELPERS ==========
const formatRole = (role) => {
  const roles = {
    super_admin: 'Super Admin',
    admin: 'Admin',
    tour_manager: 'Tour Manager',
    tour_assistant: 'Tour Assistant',
    partner: 'Partner'
  }
  return roles[role] || role || 'User'
}

// ========== SCREEN SIZE CHECK ==========
const checkScreenSize = () => {
  const width = window.innerWidth
  isMobile.value = width < 768
  if (isMobile.value) {
    isOpen.value = false
  }
}

// ========== WATCH FOR PERMISSION CHANGES ==========
watch(() => permissionService.loaded, (loaded) => {
  if (loaded) {
    components.value = permissionService.getDashboardComponents()
    roleName.value = permissionService.getRoleName() || 'User'
  }
})

// ========== LIFECYCLE ==========
onMounted(() => {
  user.value = authService.getUser()
  loadDashboardConfig()
  
  const saved = localStorage.getItem('admin_sidebar_collapsed')
  if (saved !== null) {
    isCollapsed.value = saved === 'true'
  }
  
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})
</script>


<style scoped>
/* ========== BASE SIDEBAR ========== */
.admin-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 260px;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
}

.admin-sidebar.collapsed {
  width: 70px;
}

.admin-sidebar.mobile {
  position: fixed;
  top: 0;
  left: -300px;
  width: 280px;
  z-index: 2000;
  transition: left 0.3s ease;
}

.admin-sidebar.mobile.is-open {
  left: 0;
}

/* ========== SIDEBAR HEADER ========== */
.sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f8fafc;
  flex-shrink: 0;
  min-height: 70px;
}

.sidebar-logo {
  height: 40px;
  width: auto;
  flex-shrink: 0;
}

.sidebar-brand {
  flex: 1;
  min-width: 0;
}

.sidebar-brand h3 {
  margin: 0;
  font-size: 1rem;
  color: #1e3a8a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-brand span {
  font-size: 0.75rem;
  color: #6b7280;
  display: block;
}

.sidebar-toggle {
  background: none;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  width: 30px;
  height: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  flex-shrink: 0;
  transition: all 0.2s;
}

.sidebar-toggle:hover {
  background: #f1f5f9;
  border-color: #1e3a8a;
}

/* ========== USER PROFILE ========== */
.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #dbeafe;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1e3a8a;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-info h4 {
  margin: 0;
  font-size: 0.9rem;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 0.7rem;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* ========== LOADING STATE ========== */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  flex: 1;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #1e3a8a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ========== SIDEBAR NAV ========== */
.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 2px;
}

.nav-section {
  padding: 0.25rem 0;
}

.nav-section-title {
  padding: 0.5rem 1.25rem 0.25rem;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #9ca3af;
  font-weight: 600;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.6rem 1.25rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #374151;
  font-size: 0.85rem;
  transition: all 0.2s;
  position: relative;
  text-decoration: none;
}

.nav-item i {
  width: 20px;
  text-align: center;
  color: #6b7280;
  font-size: 1rem;
  flex-shrink: 0;
}

.nav-item span {
  white-space: nowrap;
}

.nav-item:hover {
  background: #f8fafc;
  color: #1e3a8a;
}

.nav-item:hover i {
  color: #1e3a8a;
}

.nav-item.active {
  background: #dbeafe;
  color: #1e3a8a;
  font-weight: 500;
}

.nav-item.active i {
  color: #1e3a8a;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #1e3a8a;
  border-radius: 0 2px 2px 0;
}

.nav-item.logout-btn {
  color: #dc2626;
  margin-top: 0.5rem;
}

.nav-item.logout-btn i {
  color: #dc2626;
}

.nav-item.logout-btn:hover {
  background: #fee2e2;
  color: #b91c1c;
}

.nav-item.logout-btn:hover i {
  color: #b91c1c;
}

/* ========== TOOLTIP (Collapsed Mode) ========== */
.tooltip {
  display: none;
  position: absolute;
  left: calc(100% + 12px);
  top: 50%;
  transform: translateY(-50%);
  background: #1f2937;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  white-space: nowrap;
  pointer-events: none;
}

.collapsed .nav-item:hover .tooltip {
  display: block;
}

/* ========== MOBILE OVERLAY ========== */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1999;
}

/* ========== RESPONSIVE ========== */
@media (max-width: 768px) {
  .admin-sidebar {
    width: 280px;
    left: -300px;
  }
  
  .admin-sidebar.mobile.is-open {
    left: 0;
  }
}
</style>
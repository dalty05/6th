<template>
  <aside class="admin-sidebar" :class="{ collapsed: isCollapsed, mobile: isMobile }">
    <!-- Sidebar Header -->
    <div class="sidebar-header">
      <img src="/logo.png" alt="Meru Dairy" class="sidebar-logo">
      <div class="sidebar-brand" v-if="!isCollapsed">
        <h3>Meru Dairy</h3>
        <span>Admin Panel</span>
      </div>
      <button class="sidebar-toggle" @click="toggleSidebar" v-if="!isMobile">
        <i :class="isCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"></i>
      </button>
    </div>

    <!-- User Profile Section -->
    <div class="user-profile" v-if="!isCollapsed">
      <div class="user-avatar">
        <i class="fas fa-user-circle"></i>
      </div>
      <div class="user-info">
        <h4>{{ user?.full_name || 'Administrator' }}</h4>
        <span class="user-role">
          <i class="fas fa-tag"></i> {{ formatRole(user?.role) }}
        </span>
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="sidebar-nav">
      <div class="nav-section">
        <div class="nav-section-title" v-if="!isCollapsed">Main</div>
        
        <button
          class="nav-item"
          :class="{ active: activeTab === 'overview' }"
          @click="navigate('overview')"
        >
          <i class="fas fa-tachometer-alt"></i>
          <span v-if="!isCollapsed">Overview</span>
          <span v-if="isCollapsed" class="tooltip">Overview</span>
        </button>

        <button
          v-if="canViewProducts"
          class="nav-item"
          :class="{ active: activeTab === 'products' }"
          @click="navigate('products')"
        >
          <i class="fas fa-box-open"></i>
          <span v-if="!isCollapsed">Products</span>
          <span v-if="isCollapsed" class="tooltip">Products</span>
        </button>

        <button
          v-if="canViewBlog"
          class="nav-item"
          :class="{ active: activeTab === 'blog' }"
          @click="navigate('blog')"
        >
          <i class="fas fa-newspaper"></i>
          <span v-if="!isCollapsed">Blog Posts</span>
          <span v-if="isCollapsed" class="tooltip">Blog Posts</span>
        </button>

        <button
          v-if="canViewJobs"
          class="nav-item"
          :class="{ active: activeTab === 'jobs' }"
          @click="navigate('jobs')"
        >
          <i class="fas fa-briefcase"></i>
          <span v-if="!isCollapsed">Job Management</span>
          <span v-if="isCollapsed" class="tooltip">Job Management</span>
        </button>

        <button
          v-if="canViewOutlets"
          class="nav-item"
          :class="{ active: activeTab === 'outlets' }"
          @click="navigate('outlets')"
        >
          <i class="fas fa-map-marker-alt"></i>
          <span v-if="!isCollapsed">Outlet Locations</span>
          <span v-if="isCollapsed" class="tooltip">Outlet Locations</span>
        </button>

        <button
          v-if="canViewUsers"
          class="nav-item"
          :class="{ active: activeTab === 'users' }"
          @click="navigate('users')"
        >
          <i class="fas fa-users"></i>
          <span v-if="!isCollapsed">User Management</span>
          <span v-if="isCollapsed" class="tooltip">User Management</span>
        </button>

        <button
          v-if="canViewPartners"
          class="nav-item"
          :class="{ active: activeTab === 'partners' }"
          @click="navigate('partners')"
        >
          <i class="fas fa-handshake"></i>
          <span v-if="!isCollapsed">Partners</span>
          <span v-if="isCollapsed" class="tooltip">Partners</span>
        </button>

        <button
          v-if="canViewStatistics"
          class="nav-item"
          :class="{ active: activeTab === 'statistics' }"
          @click="navigate('statistics')"
        >
          <i class="fas fa-chart-line"></i>
          <span v-if="!isCollapsed">Analytics</span>
          <span v-if="isCollapsed" class="tooltip">Analytics</span>
        </button>

        <button
          v-if="canViewContacts"
          class="nav-item"
          :class="{ active: activeTab === 'contacts' }"
          @click="navigate('contacts')"
        >
          <i class="fas fa-envelope"></i>
          <span v-if="!isCollapsed">Contact Messages</span>
          <span v-if="isCollapsed" class="tooltip">Contact Messages</span>
        </button>

        <button
          v-if="canViewNewsletter"
          class="nav-item"
          :class="{ active: activeTab === 'newsletter' }"
          @click="navigate('newsletter')"
        >
          <i class="fas fa-envelope-open-text"></i>
          <span v-if="!isCollapsed">Newsletter</span>
          <span v-if="isCollapsed" class="tooltip">Newsletter</span>
        </button>

        <!-- TOUR MANAGEMENT -->
        <div class="nav-divider" v-if="canViewTours && !isCollapsed"></div>
        
        <button
          v-if="canViewTours"
          class="nav-item"
          :class="{ active: activeTab === 'tours' }"
          @click="navigate('tours')"
        >
          <i class="fas fa-factory"></i>
          <span v-if="!isCollapsed">Tour Bookings</span>
          <span v-if="isCollapsed" class="tooltip">Tour Bookings</span>
          <span v-if="pendingTourCount > 0" class="badge">{{ pendingTourCount }}</span>
        </button>

        <button
          v-if="canManageTours"
          class="nav-item"
          :class="{ active: activeTab === 'tour-packages' }"
          @click="navigate('tour-packages')"
        >
          <i class="fas fa-tag"></i>
          <span v-if="!isCollapsed">Tour Packages</span>
          <span v-if="isCollapsed" class="tooltip">Tour Packages</span>
        </button>

        <button
          v-if="canManageTours"
          class="nav-item"
          :class="{ active: activeTab === 'tour-calendar' }"
          @click="navigate('tour-calendar')"
        >
          <i class="fas fa-calendar-alt"></i>
          <span v-if="!isCollapsed">Tour Calendar</span>
          <span v-if="isCollapsed" class="tooltip">Tour Calendar</span>
        </button>

        <button
          v-if="canManageTours"
          class="nav-item"
          :class="{ active: activeTab === 'tour-payments' }"
          @click="navigate('tour-payments')"
        >
          <i class="fas fa-money-bill-wave"></i>
          <span v-if="!isCollapsed">Tour Payments</span>
          <span v-if="isCollapsed" class="tooltip">Tour Payments</span>
        </button>

        <button
          v-if="canManageTours"
          class="nav-item"
          :class="{ active: activeTab === 'tour-reports' }"
          @click="navigate('tour-reports')"
        >
          <i class="fas fa-chart-bar"></i>
          <span v-if="!isCollapsed">Tour Reports</span>
          <span v-if="isCollapsed" class="tooltip">Tour Reports</span>
        </button>

        <button
          v-if="canManagePermissions"
          class="nav-item"
          :class="{ active: activeTab === 'permissions' }"
          @click="navigate('permissions')"
        >
          <i class="fas fa-lock"></i>
          <span v-if="!isCollapsed">Permissions</span>
          <span v-if="isCollapsed" class="tooltip">Permissions</span>
        </button>
      </div>

      <div class="nav-section" v-if="!isCollapsed">
        <div class="nav-section-title">Account</div>
        
        <button
          class="nav-item"
          :class="{ active: activeTab === 'profile' }"
          @click="navigate('profile')"
        >
          <i class="fas fa-user-circle"></i>
          <span>My Profile</span>
        </button>
        
        <button class="nav-item logout-btn" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i>
          <span>Logout</span>
        </button>
      </div>

      <!-- Mobile Logout Button -->
      <button v-if="isMobile" class="nav-item logout-btn mobile-logout" @click="handleLogout">
        <i class="fas fa-sign-out-alt"></i>
        <span>Logout</span>
      </button>
    </nav>

    <!-- Mobile Overlay -->
    <div class="sidebar-overlay" v-if="isMobile && isOpen" @click="closeMobileSidebar"></div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/auth'
import permissionService from '@/services/permissionService'
import axios from 'axios'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'overview'
  }
})

const emit = defineEmits(['navigate'])

const router = useRouter()
const user = ref(null)
const isCollapsed = ref(false)
const isMobile = ref(false)
const isOpen = ref(false)
const pendingTourCount = ref(0)
const permissionsLoaded = ref(false)

// Simple role-based permissions
const isSuperAdmin = computed(() => user.value?.role === 'super_admin')
const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.role === 'super_admin')
const isPartner = computed(() => user.value?.role === 'partner')

// Check if permissions are loaded
const checkPermissions = async () => {
  if (!permissionService.loaded) {
    await permissionService.loadPermissions()
  }
  permissionsLoaded.value = true
}

// Existing permissions - Only return true if permissions are loaded
const canViewProducts = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewProducts()
})

const canViewBlog = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewBlog()
})

const canViewJobs = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewJobs()
})

const canViewOutlets = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewOutlets()
})

const canViewUsers = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewUsers()
})

const canViewPartners = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewPartners()
})

const canViewStatistics = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewStatistics()
})

const canViewContacts = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewContacts()
})

const canManagePermissions = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canManagePermissions()
})

const canViewNewsletter = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewNewsletter()
})

// Tour permissions - Using permission service
const canViewTours = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewTours()
})

const canViewBookings = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewBookings()
})

const canViewTourPackages = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canViewTours()
})

const canManageTours = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canManageTours()
})

const canManageBookings = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canManageBookings()
})

const canApproveBookings = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canApproveBookings()
})

const canRejectBookings = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canRejectBookings()
})

const canUpdateAvailability = computed(() => {
  if (!permissionsLoaded.value) return false
  return permissionService.canUpdateAvailability()
})

const canManageTourStaff = computed(() => {
  // Only super admin can manage tour staff
  return user.value?.role === 'super_admin'
})

// Fetch pending tour count
const fetchPendingTours = async () => {
  if (!canViewTours.value) return
  
  try {
    const response = await axios.get('/api/tour/admin/bookings?status=pending')
    pendingTourCount.value = response.data.count || 0
  } catch (error) {
    console.error('Error fetching pending tours:', error)
  }
}

const formatRole = (role) => {
  const roles = {
    super_admin: 'Super Admin',
    admin: 'Admin',
    partner: 'Partner',
    tour_manager: 'Tour Manager',
    tour_assistant: 'Tour Assistant'
  }
  return roles[role] || role
}

const navigate = (tab) => {
  emit('navigate', tab)
  if (isMobile.value) {
    isOpen.value = false
  }
}

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('admin_sidebar_collapsed', isCollapsed.value)
}

const closeMobileSidebar = () => {
  isOpen.value = false
}

const handleLogout = async () => {
  await authService.logout()
  router.push('/admin/login')
}

const checkScreenSize = () => {
  const width = window.innerWidth
  isMobile.value = width < 768
  if (isMobile.value) {
    isOpen.value = false
  }
}

// Setup interval for pending count
let intervalId = null

onMounted(async () => {
  user.value = authService.getUser()
  
  // Load permissions before rendering
  await checkPermissions()
  
  // Now fetch pending tours
  if (canViewTours.value) {
    fetchPendingTours()
  }
  
  const saved = localStorage.getItem('admin_sidebar_collapsed')
  if (saved !== null) {
    isCollapsed.value = saved === 'true'
  }
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  
  // Refresh every 30 seconds
  intervalId = setInterval(() => {
    if (canViewTours.value) {
      fetchPendingTours()
    }
  }, 30000)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
  if (intervalId) {
    clearInterval(intervalId)
  }
})
</script>



<style scoped>
.admin-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 280px;
  background: linear-gradient(180deg, #1e3a8a 0%, #1e293b 100%);
  color: white;
  z-index: 1000;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
}

.admin-sidebar.collapsed {
  width: 80px;
}

.admin-sidebar.mobile {
  transform: translateX(-100%);
  width: 280px;
}

.admin-sidebar.mobile.open {
  transform: translateX(0);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  min-height: 70px;
}

.sidebar-logo {
  width: 40px;
  height: 40px;
  object-fit: contain;
  flex-shrink: 0;
}

.sidebar-brand {
  flex: 1;
  margin-left: 0.75rem;
}

.sidebar-brand h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.sidebar-brand span {
  font-size: 0.7rem;
  opacity: 0.7;
}

.sidebar-toggle {
  background: #f59e0b;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  flex-shrink: 0;
}

.sidebar-toggle:hover {
  transform: scale(1.1);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.user-avatar i {
  font-size: 2.5rem;
  color: #f59e0b;
}

.user-info h4 {
  margin: 0 0 0.25rem;
  font-size: 0.85rem;
}

.user-role {
  font-size: 0.7rem;
  opacity: 0.8;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1rem 0;
}

.nav-section {
  margin-bottom: 1rem;
}

.nav-section-title {
  padding: 0.5rem 1rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: rgba(255,255,255,0.5);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  color: rgba(255,255,255,0.8);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
  text-align: left;
  position: relative;
}

.nav-item i {
  width: 20px;
  font-size: 1rem;
}

.nav-item:hover {
  background: rgba(255,255,255,0.1);
  color: white;
}

.nav-item.active {
  background: rgba(245,158,11,0.2);
  color: #f59e0b;
  border-left: 3px solid #f59e0b;
}

.logout-btn {
  color: #ef4444;
  margin-top: auto;
}

.logout-btn:hover {
  background: rgba(239,68,68,0.2);
  color: #ef4444;
}

/* Tooltip for collapsed mode */
.admin-sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 0.75rem;
  position: relative;
}

.admin-sidebar.collapsed .nav-item span {
  display: none;
}

.admin-sidebar.collapsed .nav-item:hover .tooltip {
  display: block;
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  background: #1e293b;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  white-space: nowrap;
  margin-left: 0.5rem;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 999;
}

/* Scrollbar */
.admin-sidebar::-webkit-scrollbar {
  width: 4px;
}

.admin-sidebar::-webkit-scrollbar-track {
  background: rgba(255,255,255,0.1);
}

.admin-sidebar::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.3);
  border-radius: 4px;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
  }
  
  .admin-sidebar.open {
    transform: translateX(0);
  }
}
</style>
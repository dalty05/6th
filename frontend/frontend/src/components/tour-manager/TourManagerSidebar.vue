<template>
  <aside class="tour-manager-sidebar" :class="{ collapsed: isCollapsed }">
    <!-- Sidebar Header -->
    <div class="sidebar-header">
      <div class="logo-container">
        <img src="/logo.png" alt="Logo" class="logo-img" />
        <span v-if="!isCollapsed" class="logo-text">Tour Manager</span>
      </div>
      <button @click="toggleSidebar" class="toggle-btn">
        <i :class="isCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"></i>
      </button>
    </div>

    <!-- User Profile -->
    <div class="user-profile" v-if="!isCollapsed">
      <div class="user-avatar">
        <i class="fas fa-user-circle"></i>
      </div>
      <div class="user-info">
        <h4>{{ user?.full_name || 'Tour Manager' }}</h4>
        <span class="user-role">
          <i class="fas fa-tag"></i> {{ userRole }}
        </span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <div class="nav-section">
        <span v-if="!isCollapsed" class="nav-section-title">Overview</span>
        
        <button
          class="nav-item"
          :class="{ active: activeTab === 'dashboard' }"
          @click="navigate('dashboard')"
        >
          <i class="fas fa-chart-pie"></i>
          <span v-if="!isCollapsed">Dashboard</span>
          <span v-if="isCollapsed" class="tooltip">Dashboard</span>
        </button>
      </div>

      <div class="nav-section">
        <span v-if="!isCollapsed" class="nav-section-title">Tours</span>
        
        <button
          class="nav-item"
          :class="{ active: activeTab === 'bookings' }"
          @click="navigate('bookings')"
        >
          <i class="fas fa-ticket-alt"></i>
          <span v-if="!isCollapsed">Bookings</span>
          <span v-if="pendingCount > 0" class="badge">{{ pendingCount }}</span>
          <span v-if="isCollapsed" class="tooltip">Bookings</span>
        </button>

        <button
          class="nav-item"
          :class="{ active: activeTab === 'calendar' }"
          @click="navigate('calendar')"
        >
          <i class="fas fa-calendar-alt"></i>
          <span v-if="!isCollapsed">Calendar</span>
          <span v-if="isCollapsed" class="tooltip">Calendar</span>
        </button>

        <button
          v-if="canManage"
          class="nav-item"
          :class="{ active: activeTab === 'packages' }"
          @click="navigate('packages')"
        >
          <i class="fas fa-tag"></i>
          <span v-if="!isCollapsed">Packages</span>
          <span v-if="isCollapsed" class="tooltip">Packages</span>
        </button>
      </div>

      <div class="nav-section">
        <span v-if="!isCollapsed" class="nav-section-title">Finance</span>
        
        <button
          class="nav-item"
          :class="{ active: activeTab === 'payments' }"
          @click="navigate('payments')"
        >
          <i class="fas fa-money-bill-wave"></i>
          <span v-if="!isCollapsed">Payments</span>
          <span v-if="isCollapsed" class="tooltip">Payments</span>
        </button>

        <button
          v-if="canManage"
          class="nav-item"
          :class="{ active: activeTab === 'reports' }"
          @click="navigate('reports')"
        >
          <i class="fas fa-file-alt"></i>
          <span v-if="!isCollapsed">Reports</span>
          <span v-if="isCollapsed" class="tooltip">Reports</span>
        </button>
      </div>

      <!-- ✅ Add Account Section with Profile -->
      <div class="nav-section">
        <span v-if="!isCollapsed" class="nav-section-title">Account</span>
        
        <!-- ✅ Add Profile Link -->
        <button
          class="nav-item"
          :class="{ active: activeTab === 'profile' }"
          @click="navigateToProfile()"
        >
          <i class="fas fa-user-circle"></i>
          <span v-if="!isCollapsed">My Profile</span>
          <span v-if="isCollapsed" class="tooltip">My Profile</span>
        </button>

        <button class="nav-item logout-btn" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i>
          <span v-if="!isCollapsed">Logout</span>
          <span v-if="isCollapsed" class="tooltip">Logout</span>
        </button>
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/auth'
import axios from 'axios'

const props = defineProps({
  activeTab: {
    type: String,
    default: 'dashboard'
  }
})

const emit = defineEmits(['navigate'])

const router = useRouter()
const isCollapsed = ref(false)
const user = ref(null)
const pendingCount = ref(0)

// ✅ FIX: Check BOTH role AND flag
const userRole = computed(() => {
  if (!user.value) return 'Tour Manager'
  
  // ✅ Check role string first, then fallback to flags
  if (user.value.role === 'tour_manager') return 'Tour Manager'
  if (user.value.is_tour_manager) return 'Tour Manager'
  if (user.value.role === 'tour_assistant') return 'Tour Assistant'
  if (user.value.is_tour_assistant) return 'Tour Assistant'
  
  // Check admin/super admin
  if (user.value.role === 'admin' || user.value.role === 'super_admin') return 'Tour Manager'
  
  return 'Tour Assistant'
})

// ✅ FIX: Check BOTH role AND flag for manager permissions
const canManage = computed(() => {
  if (!user.value) return false
  
  // ✅ Check role string FIRST (this will catch your user)
  const isManager = user.value.role === 'tour_manager' ||
                    user.value.role === 'admin' ||
                    user.value.role === 'super_admin' ||
                    user.value.is_tour_manager === true
  
  console.log('🔍 canManage check:', {
    role: user.value.role,
    is_tour_manager: user.value.is_tour_manager,
    isManager: isManager
  })
  
  return isManager
})

const navigate = (tab) => {
  emit('navigate', tab)
}

// ✅ Add navigate to profile
const navigateToProfile = () => {
  // Navigate to tour manager profile page
  router.push('/tour-manager/profile')
}

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleLogout = async () => {
  await authService.logout()
  router.push('/admin/login')
}

const fetchPendingCount = async () => {
  try {
    const response = await axios.get('/api/tour/admin/bookings?status=pending')
    pendingCount.value = response.data.count || 0
  } catch (error) {
    console.error('Error fetching pending count:', error)
  }
}

// Expose isCollapsed to parent
defineExpose({
  isCollapsed
})

onMounted(() => {
  user.value = authService.getUser()
  console.log('🔍 Sidebar mounted - user:', user.value)
  console.log('🔍 canManage:', canManage.value)
  fetchPendingCount()
})
</script>
<style scoped>
.tour-manager-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 260px;
  background: linear-gradient(180deg, #1e3a8a 0%, #1e293b 100%);
  color: white;
  z-index: 100;
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tour-manager-sidebar.collapsed {
  width: 80px;
}

/* Sidebar Header */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  min-height: 60px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  overflow: hidden;
}

.logo-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  flex-shrink: 0;
}

.logo-text {
  font-weight: 700;
  font-size: 1.1rem;
  white-space: nowrap;
}

.toggle-btn {
  background: rgba(255,255,255,0.1);
  border: none;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s;
}

.toggle-btn:hover {
  background: rgba(255,255,255,0.2);
}

/* User Profile */
.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.user-avatar {
  font-size: 2.5rem;
  color: #f59e0b;
  flex-shrink: 0;
}

.user-info {
  overflow: hidden;
}

.user-info h4 {
  margin: 0;
  font-size: 0.9rem;
  white-space: nowrap;
}

.user-role {
  font-size: 0.7rem;
  opacity: 0.8;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.3);
  border-radius: 2px;
}

.nav-section {
  margin-bottom: 1rem;
}

.nav-section-title {
  display: block;
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

.nav-item:hover {
  background: rgba(255,255,255,0.1);
  color: white;
}

.nav-item.active {
  background: rgba(245,158,11,0.2);
  color: #f59e0b;
  border-left: 3px solid #f59e0b;
}

.nav-item i {
  width: 20px;
  font-size: 1rem;
  flex-shrink: 0;
}

.nav-item .badge {
  background: #ef4444;
  color: white;
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: auto;
  font-weight: 600;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
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
.tour-manager-sidebar.collapsed .nav-item span:not(.badge) {
  display: none;
}

.tour-manager-sidebar.collapsed .nav-item .badge {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 8px;
  padding: 1px 6px;
}

.tour-manager-sidebar.collapsed .nav-item:hover .tooltip {
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

@media (max-width: 768px) {
  .tour-manager-sidebar {
    width: 260px;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .tour-manager-sidebar.mobile-open {
    transform: translateX(0);
  }
}
</style>
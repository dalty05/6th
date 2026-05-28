<template>
  <div class="admin-dashboard">
    <AdminNavbar />
    
    <div class="dashboard-layout">
      <div class="admin-sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <img src="/logo.png" alt="Meru Dairy" class="sidebar-logo">
          <h3 v-if="!sidebarCollapsed">Admin Panel</h3>
        </div>
        
        <div class="sidebar-profile" v-if="!sidebarCollapsed">
          <div class="profile-avatar">
            <i class="fas fa-user-circle"></i>
          </div>
          <div class="profile-info">
            <h4>{{ user?.full_name || 'Administrator' }}</h4>
            <span class="profile-role">
              <i class="fas fa-tag"></i> {{ getRoleDisplayName() }}
            </span>
          </div>
        </div>
        
        <div class="sidebar-divider"></div>

        <!-- Sidebar Navigation -->
        <div class="sidebar-nav" v-if="!sidebarCollapsed">
          <button
            class="nav-item"
            :class="{ active: activeTab === 'overview' }"
            @click="activeTab = 'overview'; router.push({ path: '/admin/dashboard', query: { tab: 'overview' } })"
          >
            <i class="fas fa-chart-line"></i>
            <span>Overview</span>
          </button>

          <button
            v-if="canView('products')"
            class="nav-item"
            :class="{ active: activeTab === 'products' }"
            @click="activeTab = 'products'; router.push({ path: '/admin/dashboard', query: { tab: 'products' } })"
          >
            <i class="fas fa-box"></i>
            <span>Products</span>
          </button>

          <button
            v-if="canView('blog')"
            class="nav-item"
            :class="{ active: activeTab === 'blog' }"
            @click="activeTab = 'blog'; router.push({ path: '/admin/dashboard', query: { tab: 'blog' } })"
          >
            <i class="fas fa-newspaper"></i>
            <span>Blog</span>
          </button>

          <button
            v-if="canView('users')"
            class="nav-item"
            :class="{ active: activeTab === 'users' }"
            @click="activeTab = 'users'; router.push({ path: '/admin/dashboard', query: { tab: 'users' } })"
          >
            <i class="fas fa-users-cog"></i>
            <span>Users</span>
          </button>

          <button
            v-if="canView('partners')"
            class="nav-item"
            :class="{ active: activeTab === 'partners' }"
            @click="activeTab = 'partners'; router.push({ path: '/admin/dashboard', query: { tab: 'partners' } })"
          >
            <i class="fas fa-handshake"></i>
            <span>Partners</span>
          </button>

          <button
            v-if="canView('referrals')"
            class="nav-item"
            :class="{ active: activeTab === 'referrals' }"
            @click="activeTab = 'referrals'; router.push({ path: '/admin/dashboard', query: { tab: 'referrals' } })"
          >
            <i class="fas fa-link"></i>
            <span>Referrals</span>
          </button>

          <button
            v-if="canView('statistics')"
            class="nav-item"
            :class="{ active: activeTab === 'statistics' }"
            @click="activeTab = 'statistics'; router.push({ path: '/admin/dashboard', query: { tab: 'statistics' } })"
          >
            <i class="fas fa-chart-pie"></i>
            <span>Statistics</span>
          </button>

          <button
            v-if="canView('settings')"
            class="nav-item"
            :class="{ active: activeTab === 'settings' }"
            @click="activeTab = 'settings'; router.push({ path: '/admin/dashboard', query: { tab: 'settings' } })"
          >
            <i class="fas fa-cog"></i>
            <span>Settings</span>
          </button>
        </div>

        <!-- Sidebar collapsed mode hint -->
        <div class="sidebar-nav" v-else>
          <button
            class="nav-item"
            :class="{ active: activeTab === 'overview' }"
            @click="activeTab = 'overview'; router.push({ path: '/admin/dashboard', query: { tab: 'overview' } })"
            title="Overview"
          >
            <i class="fas fa-chart-line"></i>
          </button>
        </div>

        <div class="sidebar-divider"></div>

        <button class="nav-item logout-btn" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i>
          <span>Logout</span>
        </button>

        <button class="sidebar-toggle" @click="toggleSidebar" :aria-label="'Toggle sidebar'">
          <i class="fas fa-angle-left" v-if="sidebarCollapsed"></i>
          <i class="fas fa-angle-right" v-else></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'
import authService from '@/services/auth'
import notificationService from '@/services/notification'
import { usePermission } from '@/composables/usePermission'
import api from '@/services/api'

// Import components
import AdminNavbar from '@/components/layout/AdminNavbar.vue'
import ProductsManagement from '@/components/admin/ProductsManagement.vue'
import BlogManagement from '@/components/admin/BlogManagement.vue'
import UserManagement from '@/components/admin/UserManagement.vue'
import PartnerManagement from '@/components/admin/PartnerManagement.vue'
import ReferralAnalytics from '@/components/admin/ReferralAnalytics.vue'
import SystemSettings from '@/components/admin/SystemSettings.vue'

export default {
  name: 'AdminDashboard',
  components: {
    AdminNavbar,
    ProductsManagement,
    BlogManagement,
    UserManagement,
    PartnerManagement,
    ReferralAnalytics,
    SystemSettings
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // Get permission functions (these are all functions that return values)
    const { canView, isSuperAdmin, getRoleDisplayName } = usePermission()
    
    // Refs for reactive state
    const activeTab = ref('overview')
    const sidebarCollapsed = ref(false)
    const user = ref(null)
    const stats = ref({
      totalProducts: 0,
      totalBlogs: 0,
      totalUsers: 0,
      totalClicks: 0
    })
    const recentReferrals = ref([])
    
    // Notifications state
    const notificationsOpen = ref(true)
    const sidebarNotifications = ref([])
    const notificationsLoading = ref(false)
    const unreadCount = ref(0)
    
    // Create user modal
    const showCreateUserModal = ref(false)
    const creatingUser = ref(false)
    const newUser = ref({
      full_name: '',
      email: '',
      password: '',
      role: 'admin',
      is_active: true
    })
    
    const userManagementRef = ref(null)
    
    // Load data functions
    const loadStats = async () => {
      try {
        const [products, blogs, users, referrals] = await Promise.all([
          api.get('/products').catch(() => ({ data: [] })),
          api.get('/blog?simple=true&per_page=100').catch(() => ({ data: [] })),
          isSuperAdmin() ? api.get('/admin/users').catch(() => ({ data: [] })) : Promise.resolve({ data: [] }),
          canView('referrals') ? api.get('/referral/stats').catch(() => ({ data: { totalClicks: 0 } })) : Promise.resolve({ data: { totalClicks: 0 } })
        ])
        
        stats.value = {
          totalProducts: products.data.length || 0,
          totalBlogs: Array.isArray(blogs.data) ? blogs.data.length : 0,
          totalUsers: users.data.length || 0,
          totalClicks: referrals.data.totalClicks || 0
        }
      } catch (error) {
        console.error('Error loading stats:', error)
      }
    }
    
    const loadRecentReferrals = async () => {
  try {
    const response = await api.get('/referral/recent?limit=5')
    recentReferrals.value = response.data || []
  } catch (error) {
    console.error('Error loading recent referrals:', error)
    // Fallback to empty array
    recentReferrals.value = []
  }
}
    
    const loadSidebarNotifications = async () => {
  notificationsLoading.value = true
  try {
    const data = await notificationService.fetchNotifications(5)
    sidebarNotifications.value = data || []
    unreadCount.value = notificationService.unreadCount.value || 0
  } catch (error) {
    console.error('Error loading notifications:', error)
    sidebarNotifications.value = []
    unreadCount.value = 0
  } finally {
    notificationsLoading.value = false
  }
}
    
    const toggleNotifications = () => {
      notificationsOpen.value = !notificationsOpen.value
    }
    
    const handleNotificationClick = (notification) => {
      if (!notification.read) {
        notificationService.markAsRead(notification.id)
        notification.read = true
        unreadCount.value--
      }
      
      if (notification.link) {
        router.push(notification.link)
      }
    }
    
    const viewAllNotifications = () => {
      toast.info('Full notifications page coming soon')
    }
    
    const getIconClass = (type) => {
      switch(type) {
        case 'success': return 'fas fa-check-circle'
        case 'error': return 'fas fa-exclamation-circle'
        case 'warning': return 'fas fa-exclamation-triangle'
        default: return 'fas fa-info-circle'
      }
    }
    
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(diff / 3600000)
      const days = Math.floor(diff / 86400000)
      
      if (minutes < 1) return 'Just now'
      if (minutes < 60) return `${minutes} min ago`
      if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
      if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`
      return date.toLocaleDateString()
    }
    
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
      localStorage.setItem('admin_sidebar_collapsed', sidebarCollapsed.value)
    }
    
    const handleLogout = async () => {
      await authService.logout()
      router.push('/admin/login')
    }
    
    const openCreateUserModal = () => {
      newUser.value = {
        full_name: '',
        email: '',
        password: '',
        role: 'admin',
        is_active: true
      }
      showCreateUserModal.value = true
    }
    
    const createUser = async () => {
      const password = newUser.value.password
      if (password.length < 8) {
        toast.error('Password must be at least 8 characters')
        return
      }
      if (!/[A-Z]/.test(password)) {
        toast.error('Password must contain at least one uppercase letter')
        return
      }
      if (!/[a-z]/.test(password)) {
        toast.error('Password must contain at least one lowercase letter')
        return
      }
      if (!/[0-9]/.test(password)) {
        toast.error('Password must contain at least one number')
        return
      }
      
      creatingUser.value = true
      try {
        await api.post('/admin/users', newUser.value)
        toast.success(`User ${newUser.value.full_name} created successfully!`)
        closeCreateUserModal()
        loadStats()
      } catch (error) {
        console.error('Error creating user:', error)
        toast.error(error.response?.data?.error || 'Failed to create user')
      } finally {
        creatingUser.value = false
      }
    }
    
    const closeCreateUserModal = () => {
      showCreateUserModal.value = false
    }
    
    const checkUrlParams = () => {
      const tab = route.query.tab
      if (tab && ['overview', 'products', 'blog', 'users', 'partners', 'referrals', 'statistics', 'settings'].includes(tab)) {
        activeTab.value = tab
      }
    }
    
    onMounted(() => {
      user.value = authService.getUser()
      if (!user.value) {
        router.push('/admin/login')
        return
      }
      
      const saved = localStorage.getItem('admin_sidebar_collapsed')
      if (saved !== null) {
        sidebarCollapsed.value = saved === 'true'
      }
      
      loadStats()
      loadRecentReferrals()
      loadSidebarNotifications()
      checkUrlParams()
      
      notificationService.initWebSocket()
    })
    
    // Return all values to template
    return {
      // Refs
      activeTab,
      sidebarCollapsed,
      user,
      stats,
      recentReferrals,
      sidebarNotifications,
      notificationsLoading,
      unreadCount,
      notificationsOpen,
      showCreateUserModal,
      creatingUser,
      newUser,
      userManagementRef,
      
      // Permission functions (called directly in template)
      canView,
      isSuperAdmin,
      getRoleDisplayName,
      
      // Methods
      toggleNotifications,
      handleNotificationClick,
      viewAllNotifications,
      getIconClass,
      formatTime,
      toggleSidebar,
      handleLogout,
      openCreateUserModal,
      createUser,
      closeCreateUserModal
    }
  }
}
</script>


<style scoped>
/* All styles remain the same as previous */
.admin-dashboard {
  min-height: 100vh;
  background: #f8fafc;
}

.dashboard-layout {
  display: flex;
  margin-top: 60px;
}

/* Sidebar Styles */
.admin-sidebar {
  width: 280px;
  background: linear-gradient(180deg, #1e3a8a 0%, #1e293b 100%);
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: calc(100vh - 60px);
  overflow-y: auto;
  transition: all 0.3s;
  z-index: 100;
}

.admin-sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 1.5rem;
  text-align: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.sidebar-logo {
  width: 60px;
  height: 60px;
  object-fit: contain;
  margin-bottom: 0.5rem;
}

.sidebar-header h3 {
  font-size: 1.2rem;
  margin: 0;
}

.sidebar-profile {
  padding: 1.5rem;
  text-align: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.profile-avatar i {
  font-size: 3rem;
  color: #f59e0b;
  margin-bottom: 0.5rem;
}

.profile-info h4 {
  margin: 0.5rem 0 0.25rem;
  font-size: 0.9rem;
}

.profile-role {
  display: block;
  font-size: 0.7rem;
  opacity: 0.8;
}

/* Notifications in Sidebar */
.sidebar-notifications {
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.notifications-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  cursor: pointer;
  transition: background 0.3s;
  position: relative;
}

.notifications-header:hover {
  background: rgba(255,255,255,0.1);
}

.notification-badge {
  background: #dc2626;
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 50%;
  margin-left: auto;
}

.notifications-header .fa-chevron-down {
  transition: transform 0.3s;
}

.notifications-header .fa-chevron-down.rotated {
  transform: rotate(180deg);
}

.notifications-list {
  max-height: 300px;
  overflow-y: auto;
}

.notifications-loading {
  text-align: center;
  padding: 1rem;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #f59e0b;
  border-radius: 50%;
  margin: 0 auto;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.notifications-empty {
  text-align: center;
  padding: 1.5rem;
  color: rgba(255,255,255,0.6);
  font-size: 0.8rem;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 20px;
  cursor: pointer;
  transition: background 0.3s;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.notification-item:hover {
  background: rgba(255,255,255,0.1);
}

.notification-item.unread {
  background: rgba(245,158,11,0.15);
}

.notification-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notification-icon.success {
  background: rgba(16,185,129,0.2);
  color: #10b981;
}

.notification-icon.error {
  background: rgba(220,38,38,0.2);
  color: #ef4444;
}

.notification-icon.warning {
  background: rgba(245,158,11,0.2);
  color: #f59e0b;
}

.notification-icon.info {
  background: rgba(59,130,246,0.2);
  color: #3b82f6;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-size: 0.8rem;
  font-weight: 500;
  margin-bottom: 2px;
}

.notification-time {
  font-size: 0.65rem;
  opacity: 0.6;
}

.notifications-footer {
  padding: 8px 20px;
  text-align: center;
  border-top: 1px solid rgba(255,255,255,0.1);
}

.btn-link {
  background: none;
  border: none;
  color: #f59e0b;
  font-size: 0.75rem;
  cursor: pointer;
}

/* Sidebar Navigation */
.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  width: 100%;
  background: none;
  border: none;
  color: rgba(255,255,255,0.8);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
  text-align: left;
}

.nav-item i {
  width: 20px;
  font-size: 1.1rem;
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
}

.logout-btn:hover {
  background: rgba(239,68,68,0.2);
  color: #ef4444;
}

.sidebar-divider, .nav-divider {
  height: 1px;
  background: rgba(255,255,255,0.1);
  margin: 0.5rem 0;
}

.sidebar-toggle {
  position: absolute;
  bottom: 20px;
  right: -12px;
  width: 24px;
  height: 24px;
  background: #f59e0b;
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.sidebar-toggle:hover {
  transform: scale(1.1);
}

/* Admin Content */
.admin-content {
  flex: 1;
  margin-left: 280px;
  padding: 2rem;
  transition: margin-left 0.3s;
}

.admin-content.expanded {
  margin-left: 80px;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.stat-card i {
  font-size: 2.5rem;
  color: #f59e0b;
}

.stat-info h3 {
  font-size: 1.8rem;
  margin: 0;
  color: #1e3a8a;
}

.stat-info p {
  margin: 0;
  color: #666;
}

/* Create User Card */
.create-user-card {
  background: linear-gradient(135deg, #f0f4ff, white);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.create-user-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.create-user-content h3 {
  color: #1e3a8a;
  margin-bottom: 0.25rem;
}

.create-user-content p {
  color: #666;
  margin: 0;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

/* Two Column Layout */
.two-column-layout {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 1.5rem;
}

.activity-placeholder {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
}

.quick-stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
}

.quick-stat-card h4 {
  color: #1e3a8a;
  margin-bottom: 1rem;
}

.recent-referrals {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.referral-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #f8fafc;
  border-radius: 8px;
}

.referral-code {
  font-family: monospace;
  font-size: 0.8rem;
  color: #1e3a8a;
}

.referral-clicks {
  font-size: 0.75rem;
  color: #666;
}

.no-data {
  text-align: center;
  padding: 1rem;
  color: #999;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-container {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-medium {
  max-width: 500px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  color: #1e3a8a;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
}

.modal-form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.9rem;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.7rem;
  color: #999;
}

.toggle-switch {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
  position: absolute;
}

.toggle-slider {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
  background-color: #ccc;
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #f59e0b;
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

.toggle-label {
  font-size: 0.85rem;
  color: #333;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  margin-top: 1rem;
}

.btn-secondary {
  background: #e5e7eb;
  color: #333;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
}

/* Responsive */
@media (max-width: 1024px) {
  .two-column-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
    position: fixed;
    z-index: 200;
  }
  
  .admin-sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .admin-content {
    margin-left: 0;
  }
  
  .admin-content.expanded {
    margin-left: 0;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .create-user-content {
    flex-direction: column;
    text-align: center;
  }
}
</style>
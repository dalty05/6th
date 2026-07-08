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

    <!-- Navigation -->
    <nav class="sidebar-nav">
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

      <!-- Logout -->
      <div class="nav-section" v-if="!isCollapsed">
        <div class="nav-section-title">Account</div>
        <button class="nav-item logout-btn" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i>
          <span>Logout</span>
        </button>
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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
const loading = ref(false)

const loadDashboardConfig = async () => {
  loading.value = true
  try {
    const response = await api.get('/dashboard/config')
    components.value = response.data.components || []
    roleName.value = response.data.role?.name || 'User'
    
    console.log('✅ Dashboard config loaded:', components.value.length, 'components')
  } catch (error) {
    console.error('Error loading dashboard config:', error)
  } finally {
    loading.value = false
  }
}

// Group components by section
const groupedComponents = computed(() => {
  const groups = {}
  components.value.forEach(comp => {
    const section = comp.section || 'Main'
    if (!groups[section]) groups[section] = []
    groups[section].push(comp)
  })
  return Object.entries(groups).map(([name, comps]) => ({
    name,
    components: comps.sort((a, b) => (a.order || 0) - (b.order || 0))
  }))
})

const navigate = (component) => {
  emit('navigate', component.key)
  if (component.path) {
    router.push(component.path)
  }
}

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('admin_sidebar_collapsed', isCollapsed.value)
}

const handleLogout = async () => {
    await authService.logout()
  this.$router.push('/admin/login')
  router.push('/admin/login')
}

const formatRole = (role) => {
  const roles = {
    super_admin: 'Super Admin',
    admin: 'Admin',
    tour_manager: 'Tour Manager',
    tour_assistant: 'Tour Assistant',
    partner: 'Partner'
  }
  return roles[role] || role
}

onMounted(() => {
  user.value = authService.getUser()
  loadDashboardConfig()
  
  const saved = localStorage.getItem('admin_sidebar_collapsed')
  if (saved !== null) {
    isCollapsed.value = saved === 'true'
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
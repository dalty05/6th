<!-- frontend/src/components/admin/AdminSidebar.vue -->

<template>
  <aside 
    class="admin-sidebar" 
    :class="{ 
      collapsed: isCollapsed, 
      'mobile-open': isMobileOpen,
      'auto-collapsed': isAutoCollapsed
    }"
  >
    <!-- Logo -->
    <div class="sidebar-header">
      <div class="logo-container">
        <img src="/logo.png" alt="Meru Dairy" class="logo-img" />
        <span v-if="!isCollapsed && !isAutoCollapsed" class="logo-text">Meru Dairy</span>
        <span v-if="isAutoCollapsed" class="logo-text-short">MD</span>
      </div>
      <button @click="toggleCollapse" class="collapse-btn">
        <i :class="isCollapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-left'"></i>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <!-- Group by section -->
      <div v-for="(group, section) in groupedComponents" :key="section" class="nav-section">
        <span v-if="!isCollapsed && !isAutoCollapsed" class="nav-section-title">{{ section }}</span>
        
        <router-link
          v-for="comp in group"
          :key="comp.key"
          :to="`/admin/dashboard?tab=${comp.key}`"
          class="nav-item"
          :class="{ active: activeComponent === comp.key }"
          @click="navigate(comp.key)"
        >
          <i :class="comp.icon"></i>
          <span v-if="!isCollapsed && !isAutoCollapsed">{{ comp.label }}</span>
          <span v-if="isCollapsed || isAutoCollapsed" class="tooltip">{{ comp.label }}</span>
        </router-link>
      </div>
    </nav>

    <!-- Footer with User Info and Logout -->
    <div class="sidebar-footer">
      <!-- User Info -->
      <div class="user-info">
        <div class="user-avatar">
          <i class="fas fa-user-circle"></i>
        </div>
        <div v-if="!isCollapsed && !isAutoCollapsed" class="user-details">
          <span class="user-name">{{ user?.full_name || 'User' }}</span>
          <span class="user-role">{{ user?.role || 'User' }}</span>
        </div>
      </div>
      
      <!-- Logout Button -->
      <button @click="handleLogout" class="logout-btn" :title="isCollapsed || isAutoCollapsed ? 'Logout' : ''">
        <i class="fas fa-sign-out-alt"></i>
        <span v-if="!isCollapsed && !isAutoCollapsed">Logout</span>
        <span v-if="isCollapsed || isAutoCollapsed" class="tooltip logout-tooltip">Logout</span>
      </button>
    </div>

    <!-- Mobile Overlay -->
    <div v-if="isMobileOpen" class="mobile-overlay" @click="closeMobile"></div>
  </aside>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import authService from '@/services/auth'
import permissionService from '@/services/permissionService'

const props = defineProps({
  components: {
    type: Array,
    default: () => []
  },
  activeComponent: {
    type: String,
    default: 'overview'
  }
})

const emit = defineEmits(['navigate', 'toggle'])

const route = useRoute()
const router = useRouter()
const isCollapsed = ref(false)
const isMobileOpen = ref(false)
const isAutoCollapsed = ref(false)
const user = ref(null)
const isMobile = ref(window.innerWidth < 768)
const isTablet = ref(window.innerWidth >= 768 && window.innerWidth < 1024)

// Group components by section
const groupedComponents = computed(() => {
  const groups = {}
  
  const sorted = [...props.components].sort((a, b) => (a.order || 0) - (b.order || 0))
  
  for (const comp of sorted) {
    const section = comp.section || 'Main'
    if (!groups[section]) groups[section] = []
    groups[section].push(comp)
  }
  
  return groups
})

const navigate = (key) => {
  emit('navigate', key)
  if (isMobile.value) {
    closeMobile()
  }
}

const toggleCollapse = () => {
  if (isMobile.value) return
  isCollapsed.value = !isCollapsed.value
  isAutoCollapsed.value = false
}

// Mobile methods
const toggleMobile = () => {
  isMobileOpen.value = !isMobileOpen.value
  emit('toggle', isMobileOpen.value)
  document.body.style.overflow = isMobileOpen.value ? 'hidden' : ''
}

const openMobile = () => {
  isMobileOpen.value = true
  emit('toggle', true)
  document.body.style.overflow = 'hidden'
}

const closeMobile = () => {
  isMobileOpen.value = false
  emit('toggle', false)
  document.body.style.overflow = ''
}

// Handle logout
const handleLogout = async () => {
  try {
    await authService.logout()
    router.push('/admin/login')
  } catch (error) {
    console.error('Logout error:', error)
    authService.clearUser()
    router.push('/admin/login')
  }
}

// Handle window resize
const handleResize = () => {
  const wasMobile = isMobile.value
  const wasTablet = isTablet.value
  
  isMobile.value = window.innerWidth < 768
  isTablet.value = window.innerWidth >= 768 && window.innerWidth < 1024
  
  if (isTablet.value && !isCollapsed.value && !isMobile.value) {
    isAutoCollapsed.value = true
  } else if (!isTablet.value && isAutoCollapsed.value) {
    isAutoCollapsed.value = false
  }
  
  if (wasMobile && !isMobile.value) {
    closeMobile()
  }
}

// Watch route changes to close mobile
watch(() => route.path, () => {
  if (isMobile.value) {
    closeMobile()
  }
})

// Load user data
const loadUser = () => {
  const userData = authService.getUser()
  user.value = userData
}

// Expose methods to parent
defineExpose({
  isCollapsed,
  isMobileOpen,
  isAutoCollapsed,
  toggleMobile,
  openMobile,
  closeMobile
})

// Lifecycle
onMounted(() => {
  loadUser()
  
  if (isTablet.value) {
    isAutoCollapsed.value = true
  }
  
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.admin-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 280px;
  height: 100vh;
  background: linear-gradient(180deg, #1a1a2e 0%, #1e3a8a 50%, #1a1a2e 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  overflow: hidden;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.15);
}

.admin-sidebar.collapsed {
  width: 72px;
}

.admin-sidebar.auto-collapsed {
  width: 72px;
}

/* Mobile Styles */
@media (max-width: 768px) {
  .admin-sidebar {
    transform: translateX(-100%);
    width: 280px;
    box-shadow: 2px 0 20px rgba(0, 0, 0, 0.3);
  }
  
  .admin-sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .admin-sidebar.collapsed,
  .admin-sidebar.auto-collapsed {
    width: 280px;
  }
  
  .admin-sidebar.collapsed .nav-item,
  .admin-sidebar.auto-collapsed .nav-item {
    justify-content: flex-start;
  }
  
  .admin-sidebar.collapsed .tooltip,
  .admin-sidebar.auto-collapsed .tooltip {
    display: none;
  }
  
  .admin-sidebar.collapsed .logo-text,
  .admin-sidebar.auto-collapsed .logo-text {
    display: inline;
  }
  
  .admin-sidebar.collapsed .logo-text-short,
  .admin-sidebar.auto-collapsed .logo-text-short {
    display: none;
  }
  
  .admin-sidebar.collapsed .nav-section-title,
  .admin-sidebar.auto-collapsed .nav-section-title {
    display: block;
  }
  
  .admin-sidebar.collapsed .user-details,
  .admin-sidebar.auto-collapsed .user-details {
    display: flex;
  }
  
  .admin-sidebar.collapsed .logout-btn span,
  .admin-sidebar.auto-collapsed .logout-btn span {
    display: inline;
  }
  
  .admin-sidebar.collapsed .logout-btn .tooltip,
  .admin-sidebar.auto-collapsed .logout-btn .tooltip {
    display: none;
  }
}

/* Tablet: auto-collapse */
@media (min-width: 769px) and (max-width: 1024px) {
  .admin-sidebar:not(.collapsed):not(.mobile-open) {
    width: 72px;
  }
  
  .admin-sidebar:not(.collapsed):not(.mobile-open) .logo-text {
    display: none;
  }
  
  .admin-sidebar:not(.collapsed):not(.mobile-open) .logo-text-short {
    display: inline;
  }
  
  .admin-sidebar:not(.collapsed):not(.mobile-open) .nav-section-title {
    display: none;
  }
  
  .admin-sidebar:not(.collapsed):not(.mobile-open) .user-details {
    display: none;
  }
  
  .admin-sidebar:not(.collapsed):not(.mobile-open) .nav-item {
    justify-content: center;
    padding: 10px;
    margin: 2px 6px;
  }
  
  .admin-sidebar:not(.collapsed):not(.mobile-open) .nav-item:hover {
    transform: translateX(0);
  }
  
  .admin-sidebar:not(.collapsed):not(.mobile-open) .nav-item span:not(.tooltip) {
    display: none;
  }
  
  .admin-sidebar:not(.collapsed):not(.mobile-open) .logout-btn span:not(.tooltip) {
    display: none;
  }
  
  .admin-sidebar:not(.collapsed):not(.mobile-open) .logout-btn {
    justify-content: center;
    padding: 8px;
  }
}

/* Desktop: hide mobile overlay */
@media (min-width: 769px) {
  .mobile-overlay {
    display: none !important;
  }
}

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: -1;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
  min-height: 72px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-img {
  width: 40px;
  height: 40px;
  object-fit: contain;
  filter: brightness(0) invert(1);
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.logo-text-short {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  display: none;
}

.collapse-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0;
}

.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.nav-section {
  margin-bottom: 8px;
}

.nav-section-title {
  display: block;
  padding: 8px 20px;
  font-size: 11px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  position: relative;
  margin: 2px 8px;
  border-radius: 8px;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  transform: translateX(4px);
}

.nav-item.active {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border-left-color: #3b82f6;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.nav-item i {
  width: 20px;
  font-size: 16px;
  text-align: center;
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.5);
}

.nav-item:hover i {
  color: #ffffff;
}

.nav-item.active i {
  color: #60a5fa;
}

.nav-item span {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

.collapsed .nav-item,
.auto-collapsed .nav-item {
  justify-content: center;
  padding: 10px;
  margin: 2px 6px;
}

.collapsed .nav-item:hover,
.auto-collapsed .nav-item:hover {
  transform: translateX(0);
}

.collapsed .nav-section-title,
.auto-collapsed .nav-section-title {
  display: none;
}

.tooltip {
  position: absolute;
  left: 60px;
  top: 50%;
  transform: translateY(-50%);
  background: #1e293b;
  color: #ffffff;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.tooltip::before {
  content: '';
  position: absolute;
  left: -6px;
  top: 50%;
  transform: translateY(-50%);
  border-right: 6px solid #1e293b;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
}

.nav-item:hover .tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(4px);
}

/* Sidebar Footer */
.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  font-size: 32px;
  color: rgba(255, 255, 255, 0.6);
}

.user-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
}

.user-role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: capitalize;
}

.collapsed .user-details,
.auto-collapsed .user-details {
  display: none;
}

.collapsed .user-avatar,
.auto-collapsed .user-avatar {
  font-size: 28px;
}

/* Logout Button */
.logout-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: #f87171;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  width: 100%;
  position: relative;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: rgba(239, 68, 68, 0.4);
  color: #fca5a5;
  transform: translateX(4px);
}

.logout-btn i {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.logout-btn span {
  white-space: nowrap;
}

.collapsed .logout-btn,
.auto-collapsed .logout-btn {
  justify-content: center;
  padding: 8px;
  width: 100%;
}

.collapsed .logout-btn span:not(.tooltip),
.auto-collapsed .logout-btn span:not(.tooltip) {
  display: none;
}

.collapsed .logout-btn:hover .logout-tooltip,
.auto-collapsed .logout-btn:hover .logout-tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(4px);
}

.logout-tooltip {
  position: absolute;
  left: 60px;
  top: 50%;
  transform: translateY(-50%);
  background: #1e293b;
  color: #ffffff;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.logout-tooltip::before {
  content: '';
  position: absolute;
  left: -6px;
  top: 50%;
  transform: translateY(-50%);
  border-right: 6px solid #1e293b;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
}
</style>
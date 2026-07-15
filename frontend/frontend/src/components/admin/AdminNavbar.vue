<!-- DEPRECATED: keep only AdminNavbar.vue (casing fix). -->
<template>
  <header class="admin-navbar">

    <div class="navbar-left">
      <button @click="toggleSidebar" class="menu-btn">
        <i class="fas fa-bars"></i>
      </button>
      <h1 class="page-title">{{ pageTitle }}</h1>
    </div>
    
    <div class="navbar-right">
      <!-- Notifications -->
      <button class="nav-btn" @click="toggleNotifications">
        <i class="fas fa-bell"></i>
        <span v-if="notificationCount > 0" class="badge">{{ notificationCount }}</span>
      </button>
      
      <!-- User Menu -->
      <div class="user-menu" @click="toggleUserMenu">
        <div class="user-avatar">
          <i class="fas fa-user-circle"></i>
        </div>
        <span class="user-name">{{ user?.full_name || 'User' }}</span>
        <i class="fas fa-chevron-down" :class="{ rotated: userMenuOpen }"></i>
        
        <!-- Dropdown -->
        <div v-if="userMenuOpen" class="dropdown-menu">
          <router-link to="/admin/dashboard?tab=profile" class="dropdown-item">
            <i class="fas fa-user"></i> My Profile
          </router-link>
          <router-link to="/admin/dashboard" class="dropdown-item">
            <i class="fas fa-home"></i> Dashboard
          </router-link>
          <hr class="dropdown-divider">
          <button @click="handleLogout" class="dropdown-item logout">
            <i class="fas fa-sign-out-alt"></i> Logout
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import authService from '@/services/auth'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['logout', 'toggle-sidebar'])

const route = useRoute()
const router = useRouter()
const userMenuOpen = ref(false)
const notificationOpen = ref(false)

const pageTitle = computed(() => {
  return route.meta.title || 'Dashboard'
})

const notificationCount = ref(3)

const toggleSidebar = () => {
  emit('toggle-sidebar')
}

const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
}

const toggleNotifications = () => {
  notificationOpen.value = !notificationOpen.value
}

const handleLogout = async () => {
  userMenuOpen.value = false
  await authService.logout()
  router.push('/admin/login')
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
  const menu = document.querySelector('.user-menu')
  if (menu && !menu.contains(e.target)) {
    userMenuOpen.value = false
  }
})
</script>

<style scoped>
.admin-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  min-height: 64px;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #64748b;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.menu-btn:hover {
  background: #f1f5f9;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-btn {
  position: relative;
  background: none;
  border: none;
  font-size: 20px;
  color: #64748b;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: #f1f5f9;
  color: #1a1a2e;
}

.nav-btn .badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #dc2626;
  color: white;
  font-size: 10px;
  font-weight: 600;
  min-width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-menu {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px 4px 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-menu:hover {
  background: #f1f5f9;
}

.user-avatar {
  font-size: 32px;
  color: #94a3b8;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
}

.user-menu .fa-chevron-down {
  font-size: 12px;
  color: #94a3b8;
  transition: transform 0.2s;
}

.user-menu .fa-chevron-down.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  min-width: 200px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  z-index: 1000;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  color: #1a1a2e;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
  cursor: pointer;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
}

.dropdown-item:hover {
  background: #f1f5f9;
}

.dropdown-item i {
  width: 18px;
  color: #64748b;
}

.dropdown-item.logout {
  color: #dc2626;
}

.dropdown-item.logout i {
  color: #dc2626;
}

.dropdown-divider {
  border: none;
  border-top: 1px solid #f1f5f9;
  margin: 4px 0;
}

@media (max-width: 768px) {
  .admin-navbar {
    padding: 12px 16px;
  }
  
  .page-title {
    font-size: 16px;
  }
  
  .user-name {
    display: none;
  }
}
</style>




<!-- frontend/src/components/admin/AdminNavbar.vue -->

<template>
  <header class="admin-navbar">
    <div class="navbar-left">
      <button @click="toggleSidebar" class="menu-btn">
        <i class="fas fa-bars"></i>
      </button>
      <h1 class="page-title">{{ pageTitle }}</h1>
    </div>
    
    <div class="navbar-right">
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
          <button @click="redirectToLogin" class="dropdown-item logout">
            <i class="fas fa-sign-out-alt"></i> Logout
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  user: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['toggle-sidebar'])

const route = useRoute()
const router = useRouter()
const userMenuOpen = ref(false)

const pageTitle = computed(() => {
  return route.meta.title || 'Dashboard'
})

const toggleSidebar = () => {
  emit('toggle-sidebar')
}

const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
}

const redirectToLogin = () => {
  userMenuOpen.value = false
  router.push('/admin/login')
}

// Close dropdown when clicking outside
const handleClickOutside = (e) => {
  const menu = document.querySelector('.user-menu')
  if (menu && !menu.contains(e.target)) {
    userMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.admin-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #3b82f6 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 64px;
  box-shadow: 0 2px 4px rgba(30, 58, 138, 0.1);
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-btn {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 20px;
  color: #ffffff;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.menu-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
  border-color: rgba(255, 255, 255, 0.4);
}

.menu-btn:active {
  transform: scale(0.95);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-menu {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px 6px 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.user-menu:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.user-avatar {
  font-size: 32px;
  color: #ffffff;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.user-menu .fa-chevron-down {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  transition: transform 0.3s ease;
}

.user-menu .fa-chevron-down.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  min-width: 220px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(30, 58, 138, 0.2);
  border: 1px solid rgba(30, 58, 138, 0.1);
  overflow: hidden;
  z-index: 1000;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 18px;
  color: #1e293b;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s ease;
  cursor: pointer;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
}

.dropdown-item:hover {
  background: #eff6ff;
  color: #1e3a8a;
}

.dropdown-item i {
  width: 18px;
  color: #3b82f6;
  transition: color 0.2s ease;
}

.dropdown-item:hover i {
  color: #1e3a8a;
}

.dropdown-item.logout {
  color: #dc2626;
}

.dropdown-item.logout i {
  color: #dc2626;
}

.dropdown-item.logout:hover {
  background: #fef2f2;
  color: #b91c1c;
}

.dropdown-item.logout:hover i {
  color: #b91c1c;
}

.dropdown-divider {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 4px 12px;
}

/* Responsive */
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
  
  .user-menu {
    padding: 6px 8px;
  }
}
</style>
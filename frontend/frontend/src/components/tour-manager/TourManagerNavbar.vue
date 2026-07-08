<template>
  <nav class="tour-manager-navbar">
    <div class="navbar-left">
      <button class="menu-toggle" @click="$emit('toggleSidebar')">
        <i class="fas fa-bars"></i>
      </button>
      <div class="navbar-brand">
        <img src="/logo.png" alt="Logo" class="brand-logo">
        <span class="brand-text">Tour Manager</span>
      </div>
    </div>

    <div class="navbar-center">
      <span class="welcome-text">
        Welcome, {{ user?.full_name?.split(' ')[0] || 'Manager' }}
      </span>
    </div>

    <div class="navbar-right">
      <div class="notification-badge">
        <i class="fas fa-bell"></i>
        <span v-if="pendingCount > 0" class="badge">{{ pendingCount }}</span>
      </div>
      <div class="navbar-user" >
        <div class="user-avatar">
          <i class="fas fa-user-circle"></i>
        </div>
        <span class="user-name">{{ user?.full_name || 'Tour Manager' }}</span>
        
      </div>

      
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/auth'
import axios from 'axios'

const router = useRouter()
const user = ref(null)
const pendingCount = ref(0)
const showDropdown = ref(false)

const fetchPendingCount = async () => {
  try {
    const response = await axios.get('/api/tour/admin/bookings?status=pending')
    pendingCount.value = response.data.count || 0
  } catch (error) {
    console.error('Error fetching pending count:', error)
  }
}

const goToProfile = () => {
  showDropdown.value = false
  router.push('/admin/profile')
}

const handleLogout = async () => {
  showDropdown.value = false
    await authService.logout()
  this.$router.push('/admin/login')
  router.push('/login')
}


</script>

<style scoped>
.tour-manager-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1.5rem;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.menu-toggle {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #4b5563;
  padding: 0.5rem;
  transition: color 0.3s;
}

.menu-toggle:hover {
  color: #1e3a8a;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.brand-logo {
  height: 32px;
  width: 32px;
  object-fit: contain;
}

.brand-text {
  font-weight: 600;
  color: #1e3a8a;
  font-size: 1.1rem;
}

.navbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.welcome-text {
  font-size: 0.95rem;
  color: #4b5563;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
}

.notification-badge {
  position: relative;
  font-size: 1.2rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
}

.notification-badge .badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #ef4444;
  color: white;
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 50%;
  font-weight: 600;
  min-width: 18px;
  text-align: center;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.25rem 0.75rem;
  border-radius: 8px;
  transition: background 0.3s;
}

.navbar-user:hover {
  background: #f3f4f6;
}

.user-avatar {
  font-size: 1.8rem;
  color: #f59e0b;
}

.user-name {
  font-size: 0.85rem;
  color: #1f2937;
}

.navbar-user .fa-chevron-down {
  font-size: 0.7rem;
  color: #6b7280;
  transition: transform 0.3s;
}

.navbar-user .fa-chevron-down.rotated {
  transform: rotate(180deg);
}

@media (max-width: 768px) {
  .brand-text {
    display: none;
  }
  
  .welcome-text {
    display: none;
  }
  
  .user-name {
    display: none;
  }
  
  .navbar-center {
    flex: 0;
  }
}
</style>
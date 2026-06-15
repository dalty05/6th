<template>
  <nav class="admin-navbar">
    <div class="navbar-container">
      <div class="navbar-left">
        <MobileMenuButton @toggle="toggleMobileSidebar" />
        <div class="company-brand" @click="goToDashboard">
          <img src="/logo.png" alt="Meru Dairy" class="company-logo">
          <div class="company-info">
            <span class="company-name">Meru Dairy</span>
            <span class="company-role">Admin Portal</span>
          </div>
        </div>
      </div>

      <div class="navbar-right">
        <div class="user-info">
          <div class="user-avatar">
            <i class="fas fa-user-shield"></i>
          </div>
          <div class="user-details">
            <span class="user-name">{{ userName }}</span>
            <span class="user-role">
              <i class="fas fa-tag"></i>
              {{ userRole }}
            </span>
          </div>
        </div>
        <button @click="handleLogout" class="logout-btn" title="Logout">
          <i class="fas fa-sign-out-alt"></i>
          <span>Logout</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/auth'
import MobileMenuButton from '@/components/admin/MobileMenuButton.vue'

const router = useRouter()
const user = ref(null)

const userName = computed(() => {
  return user.value?.full_name?.split(' ')[0] || 'Admin'
})

const userRole = computed(() => {
  const role = user.value?.role
  switch(role) {
    case 'super_admin': return 'Super Admin'
    case 'admin': return 'Admin'
    case 'partner': return 'Partner'
    default: return 'User'
  }
})

const emit = defineEmits(['toggleSidebar'])

const toggleMobileSidebar = () => {
  emit('toggleSidebar')
}

const goToDashboard = () => {
  router.push('/admin/dashboard')
}

const handleLogout = async () => {
  await authService.logout()
  router.push('/admin/login')
}

onMounted(() => {
  user.value = authService.getUser()
})
</script>

<style scoped>
.admin-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  z-index: 1001;
  height: 60px;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 1.5rem;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.company-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.company-logo {
  height: 36px;
  width: auto;
}

.company-info {
  display: flex;
  flex-direction: column;
}

.company-name {
  font-size: 1rem;
  font-weight: 700;
  color: #1e3a8a;
  line-height: 1.2;
}

.company-role {
  font-size: 0.65rem;
  color: #f59e0b;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: #f8fafc;
  border-radius: 40px;
}

.user-avatar i {
  font-size: 1.2rem;
  color: #f59e0b;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e3a8a;
}

.user-role {
  font-size: 0.65rem;
  color: #666;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: none;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  color: #ef4444;
  font-size: 0.85rem;
}

.logout-btn:hover {
  background: #fee2e2;
}

@media (max-width: 768px) {
  .navbar-container {
    padding: 0 1rem;
  }
  
  .company-role {
    display: none;
  }
  
  .user-details {
    display: none;
  }
  
  .user-info {
    padding: 0.5rem;
  }
  
  .logout-btn span {
    display: none;
  }
  
  .logout-btn {
    padding: 0.5rem;
  }
}

@media (max-width: 480px) {
  .company-info {
    display: none;
  }
}
</style>
<template>
  <nav class="admin-navbar" :class="{ scrolled: isScrolled }">
    <div class="navbar-container">
      <div class="navbar-brand" @click="goToDashboard">
        <img src="/logo.png" alt="Meru Dairy" class="logo">
        <span class="brand-text">Admin Panel</span>
      </div>
      
      <div class="navbar-actions">
        <!-- Quick Actions Dropdown -->
        <div class="quick-actions-dropdown">
          <button class="action-btn" @click="toggleQuickActions">
            <i class="fas fa-plus-circle"></i>
            <span>Quick Actions</span>
            <i class="fas fa-chevron-down" :class="{ rotated: quickActionsOpen }"></i>
          </button>
          <div v-if="quickActionsOpen" class="dropdown-menu" @click.stop>
            <button @click="quickCreate('product')" class="dropdown-item">
              <i class="fas fa-box-open"></i> Add Product
            </button>
            <button @click="quickCreate('blog')" class="dropdown-item">
              <i class="fas fa-newspaper"></i> Write Blog
            </button>
            <button @click="quickCreate('user')" class="dropdown-item">
              <i class="fas fa-user-plus"></i> Create User
            </button>
            <button @click="quickCreate('partner')" class="dropdown-item">
              <i class="fas fa-handshake"></i> Add Partner
            </button>
          </div>
        </div>
        
        <!-- Search -->
        <button class="action-btn" @click="toggleSearch">
          <i class="fas fa-search"></i>
        </button>
        
        <!-- User Menu -->
        <div class="user-menu">
          <button class="user-btn" @click="toggleUserMenu">
            <i class="fas fa-user-circle"></i>
            <span>{{ userName }}</span>
            <i class="fas fa-chevron-down" :class="{ rotated: userMenuOpen }"></i>
          </button>
          <div v-if="userMenuOpen" class="dropdown-menu user-dropdown" @click.stop>
            <router-link to="/admin/profile" class="dropdown-item">
              <i class="fas fa-user"></i> My Profile
            </router-link>
            <router-link to="/admin/settings" class="dropdown-item">
              <i class="fas fa-cog"></i> Settings
            </router-link>
            <div class="dropdown-divider"></div>
            <button @click="handleLogout" class="dropdown-item logout">
              <i class="fas fa-sign-out-alt"></i> Logout
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Search Modal -->
    <div v-if="showSearch" class="search-modal" @click.self="toggleSearch">
      <div class="search-modal-content">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search products, blogs, users..." 
          @keyup.enter="handleSearch"
          autofocus
        >
        <button @click="handleSearch"><i class="fas fa-arrow-right"></i></button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/auth'

const router = useRouter()
const quickActionsOpen = ref(false)
const userMenuOpen = ref(false)
const showSearch = ref(false)
const searchQuery = ref('')
const isScrolled = ref(false)

const userName = computed(() => {
  const user = authService.getUser()
  return user?.full_name?.split(' ')[0] || 'Admin'
})

const toggleQuickActions = () => {
  quickActionsOpen.value = !quickActionsOpen.value
  userMenuOpen.value = false
}

const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
  quickActionsOpen.value = false
}

const toggleSearch = () => {
  showSearch.value = !showSearch.value
  if (!showSearch.value) {
    searchQuery.value = ''
  }
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push(`/admin/search?q=${encodeURIComponent(searchQuery.value)}`)
    showSearch.value = false
    searchQuery.value = ''
  }
}

const quickCreate = (type) => {
  quickActionsOpen.value = false
  if (type === 'product') {
    router.push('/admin/dashboard?tab=products&action=create')
  } else if (type === 'blog') {
    router.push('/admin/dashboard?tab=blog&action=create')
  } else if (type === 'user') {
    router.push('/admin/dashboard?tab=users&action=create')
  } else if (type === 'partner') {
    router.push('/admin/dashboard?tab=partners&action=create')
  }
}

const goToDashboard = () => {
  router.push('/admin/dashboard')
}

const handleLogout = async () => {
  await authService.logout()
  router.push('/admin/login')
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 10
}

const handleClickOutside = (event) => {
  const quickActions = document.querySelector('.quick-actions-dropdown')
  const userMenu = document.querySelector('.user-menu')
  
  if (quickActions && !quickActions.contains(event.target) && quickActionsOpen.value) {
    quickActionsOpen.value = false
  }
  if (userMenu && !userMenu.contains(event.target) && userMenuOpen.value) {
    userMenuOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.admin-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  z-index: 999;
  transition: all 0.3s;
}

.admin-navbar.scrolled {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 2rem;
  max-width: 100%;
  margin: 0 auto;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.logo {
  height: 40px;
  width: auto;
}

.brand-text {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e3a8a;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  color: #333;
}

.action-btn:hover {
  background: #e0e7ff;
  border-color: #f59e0b;
}

.quick-actions-dropdown, .user-menu {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  min-width: 200px;
  overflow: hidden;
  z-index: 1000;
}

.user-dropdown {
  right: 0;
  left: auto;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: none;
  color: #333;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.dropdown-item:hover {
  background: #f8fafc;
}

.dropdown-item.logout {
  color: #dc2626;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 0.25rem 0;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: none;
  border: none;
  cursor: pointer;
  font-weight: 500;
  color: #1e3a8a;
}

.fa-chevron-down {
  transition: transform 0.3s;
}

.fa-chevron-down.rotated {
  transform: rotate(180deg);
}

/* Search Modal */
.search-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.8);
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-modal-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 60px;
  width: 90%;
  max-width: 600px;
}

.search-modal-content i {
  font-size: 1.2rem;
  color: #666;
}

.search-modal-content input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 1rem;
}

.search-modal-content button {
  background: #f59e0b;
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
}

.search-modal-content button:hover {
  background: #d97706;
}

@media (max-width: 768px) {
  .navbar-container {
    padding: 0.5rem 1rem;
  }
  
  .brand-text {
    display: none;
  }
  
  .action-btn span {
    display: none;
  }
  
  .user-btn span {
    display: none;
  }
}
</style>
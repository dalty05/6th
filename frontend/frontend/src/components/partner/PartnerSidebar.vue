<template>
  <aside class="partner-sidebar" :class="{ 'mobile-open': isMobileOpen }">
    <!-- Brand -->
    <div class="sidebar-brand">
      <h2>
        <i class="fas fa-handshake"></i>
        Partner Portal
      </h2>
      <p class="brand-sub">Referral &amp; Marketing</p>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <div class="nav-section">
        <div class="nav-section-title">Main</div>
        <router-link to="/partner/dashboard" class="nav-item" :class="{ active: $route.path === '/partner/dashboard' }">
          <i class="fas fa-home"></i> Dashboard
        </router-link>
        <router-link to="/partner/links" class="nav-item" :class="{ active: $route.path === '/partner/links' }">
          <i class="fas fa-link"></i> Referral Links
          <span v-if="linkCount > 0" class="badge">{{ linkCount }}</span>
        </router-link>
        <router-link to="/partner/analytics" class="nav-item" :class="{ active: $route.path === '/partner/analytics' }">
          <i class="fas fa-chart-line"></i> Analytics
        </router-link>
      </div>

      <div class="nav-section">
        <div class="nav-section-title">Account</div>
        <router-link to="/partner/profile" class="nav-item" :class="{ active: $route.path === '/partner/profile' }">
          <i class="fas fa-user"></i> Profile
        </router-link>
        <router-link to="/partner/help" class="nav-item" :class="{ active: $route.path === '/partner/help' }">
          <i class="fas fa-question-circle"></i> Help &amp; Support
        </router-link>
      </div>
    </nav>

    <!-- User Footer -->
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">
          <i class="fas fa-user-circle"></i>
        </div>
        <div class="user-details">
          <div class="name">{{ user?.full_name || 'Partner' }}</div>
          <div class="role">{{ user?.role || 'Partner' }}</div>
        </div>
        <button @click="handleLogout" class="logout-btn" title="Logout">
          <i class="fas fa-sign-out-alt"></i>
        </button>
      </div>
    </div>
  </aside>

</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/auth'
import referralService from '@/services/referral'

const router = useRouter()
const user = ref(null)
const linkCount = ref(0)
const isMobileOpen = ref(false)

// Toggle mobile sidebar
const toggleMobile = () => {
  isMobileOpen.value = !isMobileOpen.value
}

// Close mobile sidebar
const closeMobile = () => {
  isMobileOpen.value = false
}

const handleLogout = async () => {
    await authService.logout()
  this.$router.push('/admin/login')
  router.push('/')
}

const loadLinkCount = async () => {
  try {
    const response = await referralService.getStats()
    linkCount.value = response.total_links || 0
  } catch (error) {
    console.error('Error loading link count:', error)
  }
}

// Listen to route changes to close mobile
router.afterEach(() => {
  closeMobile()
})

onMounted(() => {
  user.value = authService.getUser()
  if (user.value) {
    loadLinkCount()
  }
})

// Expose methods to parent
defineExpose({
  toggleMobile,
  closeMobile,
  isMobileOpen
})
</script>

<style scoped>
/* ========================================
   PARTNER SIDEBAR - COMPLETE STYLES
   ======================================== */

.partner-sidebar {
  width: 260px;
  min-height: 100vh;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
  color: #e2e8f0;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  z-index: 1000;
  transition: transform 0.3s ease;
  box-shadow: 4px 0 12px rgba(0, 0, 0, 0.1);
}

/* Brand */
.sidebar-brand {
  padding: 1.5rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-brand h2 {
  color: white;
  font-size: 1.2rem;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sidebar-brand h2 i {
  color: #f59e0b;
}

.sidebar-brand .brand-sub {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0.25rem 0 0;
}

/* Navigation */
.sidebar-nav {
  flex: 1;
  padding: 1rem 0.75rem;
  overflow-y: auto;
}

.sidebar-nav .nav-section {
  margin-bottom: 1.5rem;
}

.sidebar-nav .nav-section-title {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b;
  padding: 0 0.75rem;
  margin-bottom: 0.5rem;
}

.sidebar-nav .nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.65rem 0.75rem;
  border-radius: 10px;
  color: #94a3b8;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  margin-bottom: 2px;
  font-size: 0.9rem;
  border: none;
  background: transparent;
  width: 100%;
  text-align: left;
}

.sidebar-nav .nav-item i {
  width: 20px;
  font-size: 1rem;
  color: #64748b;
  transition: color 0.2s;
}

.sidebar-nav .nav-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: white;
}

.sidebar-nav .nav-item:hover i {
  color: #f59e0b;
}

.sidebar-nav .nav-item.active {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.sidebar-nav .nav-item.active i {
  color: #f59e0b;
}

.sidebar-nav .nav-item .badge {
  margin-left: auto;
  background: #f59e0b;
  color: #0f172a;
  font-size: 0.65rem;
  padding: 0.1rem 0.5rem;
  border-radius: 20px;
  font-weight: 600;
}

/* Footer */
.sidebar-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-footer .user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 10px;
  transition: background 0.2s;
}

.sidebar-footer .user-info:hover {
  background: rgba(255, 255, 255, 0.05);
}

.sidebar-footer .user-avatar i {
  font-size: 2rem;
  color: #94a3b8;
}

.sidebar-footer .user-details {
  flex: 1;
}

.sidebar-footer .user-details .name {
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
}

.sidebar-footer .user-details .role {
  font-size: 0.7rem;
  color: #94a3b8;
}

.sidebar-footer .logout-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.3rem 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
  font-size: 0.85rem;
}

.sidebar-footer .logout-btn:hover {
  background: rgba(220, 38, 38, 0.15);
  color: #ef4444;
}

/* Mobile */
@media (max-width: 768px) {
  .partner-sidebar {
    transform: translateX(-100%);
    width: 280px;
  }
  
  .partner-sidebar.mobile-open {
    transform: translateX(0);
  }
}
</style>
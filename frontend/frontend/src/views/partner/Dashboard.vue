<template>
  <div class="partner-layout">
    <!-- Sidebar -->
    <PartnerSidebar ref="sidebarRef" />

    <!-- Main Content -->
    <main class="partner-main">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-left">
          <button class="sidebar-toggle" @click="toggleSidebar">
            <i class="fas fa-bars"></i>
          </button>
          <h1><i class="fas fa-home"></i> Dashboard</h1>
        </div>
        <div class="header-actions">
          <button class="btn-primary" @click="createNewLink">
            <i class="fas fa-plus"></i> New Link
          </button>
        </div>
      </div>

      <!-- Page Content -->
      <div class="page-content">
        <!-- Welcome Section -->
        <div class="welcome-section">
          <h2>Welcome back, {{ user?.full_name?.split(' ')[0] || 'Partner' }}!</h2>
          <p>Track your referral performance and marketing campaigns</p>
        </div>

        <!-- Stats Cards -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon blue"><i class="fas fa-mouse-pointer"></i></div>
            <div class="stat-info">
              <h3>{{ stats.totalClicks || 0 }}</h3>
              <p>Total Clicks</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon green"><i class="fas fa-users"></i></div>
            <div class="stat-info">
              <h3>{{ stats.uniqueClicks || 0 }}</h3>
              <p>Unique Visitors</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon orange"><i class="fas fa-shopping-cart"></i></div>
            <div class="stat-info">
              <h3>{{ stats.totalConversions || 0 }}</h3>
              <p>Conversions</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon purple"><i class="fas fa-chart-line"></i></div>
            <div class="stat-info">
              <h3>{{ stats.conversionRate || 0 }}%</h3>
              <p>Conversion Rate</p>
            </div>
          </div>
        </div>

        <!-- Referral Code -->
        <div class="glass-card">
          <h3><i class="fas fa-link"></i> Your Referral Code</h3>
          <div class="code-box">
            <code>{{ user?.referral_code || 'Generate your code' }}</code>
            <CopyLinkButton 
              v-if="user?.referral_code" 
              :link="fullReferralLink" 
            />
          </div>
          <p v-if="user?.referral_code" class="referral-link">
            <i class="fas fa-globe"></i>
            Full referral link: <strong>{{ fullReferralLink }}</strong>
          </p>
          <p v-else class="info-text">
            Your referral code will be generated automatically.
          </p>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
          <router-link to="/partner/links" class="action-card">
            <i class="fas fa-plus-circle"></i>
            <span>Create New Link</span>
          </router-link>
          <router-link to="/partner/analytics" class="action-card">
            <i class="fas fa-chart-bar"></i>
            <span>View Analytics</span>
          </router-link>
        </div>

        <!-- Recent Links -->
        <div class="glass-card">
          <div class="section-header">
            <h3>Your Recent Links</h3>
            <router-link to="/partner/links" class="view-all">View All →</router-link>
          </div>

          <div v-if="recentLinksLoading" class="loading-state">
            <div class="loading-spinner"></div>
          </div>

          <div v-else-if="recentLinks.length === 0" class="empty-state">
            <i class="fas fa-link"></i>
            <p>No referral links yet</p>
            <router-link to="/partner/links" class="btn-primary">
              Create Your First Link
            </router-link>
          </div>

          <div v-else class="links-list">
            <div v-for="link in recentLinks" :key="link.id" class="link-item">
              <div class="link-info">
                <h4>{{ link.name }}</h4>
                <code>{{ baseUrl }}/r/{{ link.link_code }}</code>
              </div>
              <div class="link-stats">
                <span><i class="fas fa-mouse-pointer"></i> {{ link.total_clicks || 0 }}</span>
                <span><i class="fas fa-chart-line"></i> {{ link.conversion_rate || 0 }}%</span>
              </div>
              <CopyLinkButton :link="`${baseUrl}/r/${link.link_code}`" />
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/auth'
import referralService from '@/services/referral'
import PartnerSidebar from '@/components/partner/PartnerSidebar.vue'
import CopyLinkButton from '@/components/partner/CopyLinkButton.vue'

const router = useRouter()
const sidebarRef = ref(null)
const user = ref(null)
const stats = ref({
  totalClicks: 0,
  uniqueClicks: 0,
  totalConversions: 0,
  conversionRate: 0
})
const recentLinks = ref([])
const recentLinksLoading = ref(true)
const baseUrl = window.location.origin

const fullReferralLink = computed(() => 
  user.value?.referral_code ? `${baseUrl}/r/${user.value.referral_code}` : ''
)

const toggleSidebar = () => {
  if (sidebarRef.value) {
    sidebarRef.value.toggleMobile()
  }
}

const createNewLink = () => {
  router.push('/partner/links')
}

const loadStats = async () => {
  try {
    const response = await referralService.getStats()
    // Map response to expected structure
    const totalClicks = response.total_clicks || 0
    const uniqueClicks = response.total_unique_clicks || 0
    const totalConversions = response.total_conversions || 0
    
    stats.value = {
      totalClicks: totalClicks,
      uniqueClicks: uniqueClicks,
      totalConversions: totalConversions,
      conversionRate: totalClicks > 0 
        ? Math.round((totalConversions / totalClicks) * 100) 
        : 0
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const loadRecentLinks = async () => {
  recentLinksLoading.value = true
  try {
    const response = await referralService.getTopLinks(3)
    recentLinks.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.error('Error loading recent links:', error)
    recentLinks.value = []
  } finally {
    recentLinksLoading.value = false
  }
}

onMounted(() => {
  user.value = authService.getUser()
  if (!user.value) {
    router.push('/')
    return
  }
  loadStats()
  loadRecentLinks()
})
</script>

<style scoped>
.partner-layout {
  display: flex;
  min-height: 100vh;
  background: #f1f5f9;
}

.partner-main {
  flex: 1;
  margin-left: 260px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header {
  background: white;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-header h1 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-header h1 i {
  color: #f59e0b;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.page-content {
  flex: 1;
  padding: 1.5rem 2rem;
}

.welcome-section {
  margin-bottom: 1.5rem;
}

.welcome-section h2 {
  font-size: 1.3rem;
  color: #0f172a;
  margin: 0 0 0.25rem;
}

.welcome-section p {
  color: #6b7280;
  margin: 0;
}

.sidebar-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #0f172a;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

.sidebar-toggle:hover {
  background: #f1f5f9;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.stat-icon.blue { background: #dbeafe; color: #2563eb; }
.stat-icon.green { background: #d1fae5; color: #059669; }
.stat-icon.orange { background: #fef3c7; color: #d97706; }
.stat-icon.purple { background: #ede9fe; color: #7c3aed; }

.stat-info h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  color: #0f172a;
}

.stat-info p {
  font-size: 0.75rem;
  margin: 0;
  color: #6b7280;
}

/* Glass Card */
.glass-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.glass-card h3 {
  font-size: 1rem;
  color: #0f172a;
  margin: 0 0 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.glass-card h3 i {
  color: #f59e0b;
}

/* Code Box */
.code-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f1f5f9;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  flex-wrap: wrap;
}

.code-box code {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  color: #0f172a;
  word-break: break-all;
  flex: 1;
}

.referral-link {
  font-size: 0.85rem;
  color: #6b7280;
  margin: 0.5rem 0 0;
  word-break: break-all;
}

.referral-link strong {
  color: #0f172a;
}

.info-text {
  color: #6b7280;
  font-size: 0.85rem;
  margin: 0.5rem 0 0;
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: white;
  border-radius: 12px;
  text-decoration: none;
  color: #0f172a;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  border-color: #f59e0b;
}

.action-card i {
  font-size: 1.5rem;
  color: #f59e0b;
}

.action-card span {
  font-weight: 500;
}

/* Link Items */
.links-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.link-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border-radius: 8px;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.link-item .link-info h4 {
  margin: 0 0 0.25rem;
  font-size: 0.9rem;
  color: #0f172a;
}

.link-item .link-info code {
  font-size: 0.75rem;
  color: #6b7280;
  background: #e5e7eb;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.link-item .link-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.link-item .link-stats i {
  color: #f59e0b;
  margin-right: 0.25rem;
}

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.view-all {
  color: #f59e0b;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
}

.view-all:hover {
  text-decoration: underline;
}

/* Buttons */
.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-primary:hover {
  background: #d97706;
  transform: translateY(-1px);
}

/* Loading & Empty States */
.loading-state {
  text-align: center;
  padding: 2rem;
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  margin: 0 auto 0.5rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.empty-state i {
  font-size: 2.5rem;
  color: #d1d5db;
  margin-bottom: 0.5rem;
}

.empty-state p {
  margin-bottom: 1rem;
}

/* Mobile */
@media (max-width: 768px) {
  .partner-main {
    margin-left: 0;
  }
  
  .sidebar-toggle {
    display: flex;
  }
  
  .page-header {
    padding: 0.75rem 1rem;
  }
  
  .page-content {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
  
  .link-item {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
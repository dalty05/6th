<template>
  <div class="partner-dashboard">
    <div class="dashboard-header">
      <h1>Partner Dashboard</h1>
      <div class="user-info">
        <span class="user-name">
          <i class="fas fa-user-circle"></i>
          {{ user?.full_name }}
        </span>
        <button @click="handleLogout" class="logout-btn">
          <i class="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </div>
    
    <div class="dashboard-content">
      <!-- Welcome Section -->
      <div class="welcome-section">
        <h2>Welcome back, {{ user?.full_name?.split(' ')[0] }}!</h2>
        <p>Track your referral performance and marketing campaigns</p>
      </div>
      
      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-mouse-pointer"></i>
          <div class="stat-info">
            <h3>{{ stats.totalClicks || 0 }}</h3>
            <p>Total Clicks</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-users"></i>
          <div class="stat-info">
            <h3>{{ stats.uniqueClicks || 0 }}</h3>
            <p>Unique Visitors</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-shopping-cart"></i>
          <div class="stat-info">
            <h3>{{ stats.totalConversions || 0 }}</h3>
            <p>Conversions</p>
          </div>
        </div>
        <div class="stat-card">
          <i class="fas fa-chart-line"></i>
          <div class="stat-info">
            <h3>{{ stats.conversionRate || 0 }}%</h3>
            <p>Conversion Rate</p>
          </div>
        </div>
      </div>
      
      <!-- Referral Code Section -->
      <div class="referral-code-card glass-card">
        <h3><i class="fas fa-link"></i> Your Referral Code</h3>
        <div class="code-box">
          <code>{{ user?.referral_code || 'Generate your code' }}</code>
          <CopyLinkButton v-if="user?.referral_code" :link="fullReferralLink" />
        </div>
        <p class="referral-link" v-if="user?.referral_code">
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
      <div class="recent-links-section">
        <div class="section-header">
          <h3>Your Recent Links</h3>
          <router-link to="/partner/links" class="view-all">View All →</router-link>
        </div>
        
        <div v-if="recentLinksLoading" class="loading-state">
          <div class="loading-spinner"></div>
        </div>
        
        <div v-else-if="recentLinks.length === 0" class="empty-state">
          <p>No referral links yet</p>
          <router-link to="/partner/links" class="btn-primary">Create Your First Link</router-link>
        </div>
        
        <div v-else class="links-list">
          <div v-for="link in recentLinks" :key="link.id" class="link-item">
            <div class="link-info">
              <h4>{{ link.name }}</h4>
              <code>{{ baseUrl }}/r/{{ link.link_code }}</code>
            </div>
            <div class="link-stats">
              <span><i class="fas fa-mouse-pointer"></i> {{ link.total_clicks }}</span>
              <span><i class="fas fa-chart-line"></i> {{ link.conversion_rate }}%</span>
            </div>
            <CopyLinkButton :link="`${baseUrl}/r/${link.link_code}`" />
          </div>
        </div>
      </div>
    </div>


    <PartnerFooter />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/auth'
import referralService from '@/services/referral'
import CopyLinkButton from '@/components/partner/CopyLinkButton.vue'


import PartnerFooter from '@/components/partner/PartnerFooter.vue'





const router = useRouter()
const user = ref(null)
const stats = ref({})
const recentLinks = ref([])
const recentLinksLoading = ref(true)
const baseUrl = window.location.origin

const fullReferralLink = computed(() => 
  user.value?.referral_code ? `${baseUrl}/r/${user.value.referral_code}` : ''
)

const loadStats = async () => {
  try {
    const response = await referralService.getStats()
    stats.value = response
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const loadRecentLinks = async () => {
  recentLinksLoading.value = true
  try {
    const response = await referralService.getTopLinks(3)
    recentLinks.value = response
  } catch (error) {
    console.error('Error loading recent links:', error)
  } finally {
    recentLinksLoading.value = false
  }
}

const handleLogout = async () => {
  await authService.logout()
  router.push('/')
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

.partner-dashboard {
  min-height: 100vh;
  background: #f8fafc;
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 60px);
  padding: 80px 2rem 0;
}

.content-wrapper {
  flex: 1;
}




.partner-dashboard {
  min-height: 100vh;
  background: #f8fafc;
}

.dashboard-header {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.dashboard-header h1 {
  font-size: 1.5rem;
  color: #1e3a8a;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-name {
  font-weight: 500;
  color: #333;
}

.user-name i {
  margin-right: 0.5rem;
  color: #f59e0b;
}

.logout-btn {
  background: none;
  border: none;
  color: #dc2626;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: #fee2e2;
}

.dashboard-content {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-section {
  margin-bottom: 2rem;
}

.welcome-section h2 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.welcome-section p {
  color: #666;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.stat-card i {
  font-size: 2rem;
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

.referral-code-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.referral-code-card h3 {
  color: #1e3a8a;
  margin-bottom: 1rem;
}

.code-box {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.code-box code {
  background: #f1f5f9;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-family: monospace;
  font-size: 1rem;
}

.referral-link {
  font-size: 0.85rem;
  color: #666;
  word-break: break-all;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 16px;
  text-decoration: none;
  color: #1e3a8a;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.action-card i {
  font-size: 2rem;
  color: #f59e0b;
}

.action-card span {
  font-weight: 500;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.recent-links-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  color: #1e3a8a;
  margin: 0;
}

.view-all {
  color: #f59e0b;
  text-decoration: none;
  font-size: 0.85rem;
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.link-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 12px;
  flex-wrap: wrap;
  gap: 1rem;
}

.link-info h4 {
  margin: 0 0 0.25rem 0;
  color: #1e3a8a;
}

.link-info code {
  font-size: 0.7rem;
  color: #666;
}

.link-stats {
  display: flex;
  gap: 1rem;
}

.link-stats span {
  font-size: 0.85rem;
  color: #666;
}

.link-stats i {
  margin-right: 0.25rem;
  color: #f59e0b;
}

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
  margin: 0 auto;
  animation: spin 1s linear infinite;
}

.empty-state {
  text-align: center;
  padding: 2rem;
}

.empty-state p {
  color: #666;
  margin-bottom: 1rem;
}

.btn-primary {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}

.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}


.partner-links {
  min-height: 100vh;
  background: #f8fafc;
}

.page-content {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 60px);
  padding: 80px 2rem 0;
}

.content-wrapper {
  flex: 1;
}

@media (max-width: 768px) {
  .page-content {
    padding: 70px 1rem 0;
  }
}



@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .dashboard-content {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
  
  .link-item {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .dashboard-content {
    padding: 70px 1rem 0;
  }
}



</style>
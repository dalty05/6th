<template>
  <div class="partner-dashboard">
    <div class="dashboard-header">
      <h1>Partner Dashboard</h1>
      <div class="header-actions">
        <div class="date-range">
          <select v-model="dateRange" class="form-select" @change="loadData">
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
        </div>
        <button class="btn btn-outline" @click="refreshData">
          <i class="fas fa-sync-alt"></i> Refresh
        </button>
      </div>
    </div>

    <!-- Welcome Section -->
    <div class="welcome-section glass-card">
      <div class="welcome-text">
        <h2>Welcome back, {{ user?.full_name?.split(' ')[0] }}!</h2>
        <p>Track your referral performance and manage your marketing campaigns.</p>
      </div>
      <div class="referral-code-box">
        <div class="code-label">Your Referral Code</div>
        <div class="code-value">
          <code>{{ user?.referral_code || 'Generate your first link' }}</code>
          <button v-if="user?.referral_code" @click="copyReferralCode" class="btn btn-sm btn-primary">
            <i class="fas fa-copy"></i> Copy
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <StatsCard
        title="Total Clicks"
        :value="stats.totalClicks"
        icon="fas fa-mouse-pointer"
        :trend="stats.clickTrend"
      />
      <StatsCard
        title="Unique Visitors"
        :value="stats.uniqueClicks"
        icon="fas fa-users"
        format="number"
      />
      <StatsCard
        title="Conversions"
        :value="stats.totalConversions"
        icon="fas fa-shopping-cart"
        :trend="stats.conversionTrend"
      />
      <StatsCard
        title="Conversion Rate"
        :value="stats.conversionRate"
        icon="fas fa-chart-line"
        format="percentage"
      />
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <router-link to="/partner/links" class="action-card glass-card">
        <i class="fas fa-plus-circle"></i>
        <div>
          <h3>Create New Link</h3>
          <p>Generate a new referral link for your campaign</p>
        </div>
        <i class="fas fa-arrow-right action-arrow"></i>
      </router-link>
      <router-link to="/partner/analytics" class="action-card glass-card">
        <i class="fas fa-chart-line"></i>
        <div>
          <h3>View Analytics</h3>
          <p>See detailed performance reports</p>
        </div>
        <i class="fas fa-arrow-right action-arrow"></i>
      </router-link>
    </div>

    <!-- Recent Links -->
    <div class="recent-links-section">
      <div class="section-header">
        <h3><i class="fas fa-link"></i> Your Recent Links</h3>
        <router-link to="/partner/links" class="view-all">View All →</router-link>
      </div>
      
      <div v-if="recentLinksLoading" class="loading-state">
        <div class="loading-spinner"></div>
      </div>
      
      <div v-else-if="recentLinks.length === 0" class="empty-state">
        <i class="fas fa-link"></i>
        <p>No referral links yet</p>
        <router-link to="/partner/links" class="btn btn-primary btn-sm">Create Your First Link</router-link>
      </div>
      
      <div v-else class="links-list">
        <div v-for="link in recentLinks" :key="link.id" class="link-item glass-card">
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

    <PartnerFooter />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue3-toastify'
import authService from '@/services/auth'
import referralService from '@/services/referral'
import CopyLinkButton from '@/components/partner/CopyLinkButton.vue'
import StatsCard from '@/components/partner/StatsCard.vue'


import PartnerFooter from '@/components/partner/PartnerFooter.vue'





const router = useRouter()
const user = ref(null)
const stats = ref({
  totalClicks: 0,
  uniqueClicks: 0,
  totalConversions: 0,
  conversionRate: 0,
  clickTrend: null,
  conversionTrend: null
})
const recentLinks = ref([])
const recentLinksLoading = ref(true)
const dateRange = ref('30')
const baseUrl = window.location.origin

const loadStats = async () => {
  try {
    const response = await referralService.getStats()
    stats.value = { ...stats.value, ...response }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const loadRecentLinks = async () => {
  recentLinksLoading.value = true
  try {
    const response = await referralService.getTopLinks(5)
    recentLinks.value = response
  } catch (error) {
    console.error('Error loading recent links:', error)
    recentLinks.value = []
  } finally {
    recentLinksLoading.value = false
  }
}

const loadData = async () => {
  await Promise.all([loadStats(), loadRecentLinks()])
}

const refreshData = async () => {
  await loadData()
  toast.success('Data refreshed')
}

const copyReferralCode = () => {
  navigator.clipboard.writeText(user.value?.referral_code || '')
  toast.success('Referral code copied to clipboard!')
}

onMounted(() => {
  user.value = authService.getUser()
  if (!user.value) {
    router.push('/')
    return
  }
  loadData()
})
</script>

<style scoped>
/* .partner-dashboard {
  min-height: 100vh;
  background: #f8fafc;
} */

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
  background: var(--gray-50);
  padding: var(--spacing-6);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-6);
  flex-wrap: wrap;
  gap: var(--spacing-4);
}

.dashboard-header h1 {
  color: var(--primary-blue);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--spacing-3);
  align-items: center;
}

.date-range .form-select {
  padding: var(--spacing-2) var(--spacing-3);
}

.welcome-section {
  background: linear-gradient(135deg, var(--primary-blue), var(--gray-800));
  color: white;
  padding: var(--spacing-6);
  border-radius: var(--radius-2xl);
  margin-bottom: var(--spacing-6);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-4);
}

.welcome-text h2 {
  margin: 0 0 var(--spacing-2) 0;
  font-size: var(--text-2xl);
}

.welcome-text p {
  margin: 0;
  opacity: 0.9;
}

.referral-code-box {
  background: rgba(255,255,255,0.15);
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-xl);
}

.code-label {
  font-size: var(--text-xs);
  opacity: 0.8;
  margin-bottom: var(--spacing-1);
}

.code-value {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}

.code-value code {
  background: rgba(0,0,0,0.3);
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--radius-lg);
  font-family: monospace;
  font-size: var(--text-sm);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--spacing-5);
  margin-bottom: var(--spacing-6);
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-5);
  margin-bottom: var(--spacing-6);
}

.action-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-5);
  text-decoration: none;
  transition: transform var(--transition-base);
}

.action-card:hover {
  transform: translateY(-4px);
}

.action-card i:first-child {
  font-size: var(--text-3xl);
  color: var(--accent-orange);
}

.action-card h3 {
  margin: 0 0 var(--spacing-1) 0;
  color: var(--primary-blue);
}

.action-card p {
  margin: 0;
  color: var(--gray-500);
  font-size: var(--text-sm);
}

.action-arrow {
  margin-left: auto;
  color: var(--gray-400);
  transition: transform var(--transition-base);
}

.action-card:hover .action-arrow {
  transform: translateX(4px);
  color: var(--accent-orange);
}

.recent-links-section {
  background: white;
  border-radius: var(--radius-xl);
  padding: var(--spacing-5);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

.section-header h3 {
  color: var(--primary-blue);
  margin: 0;
}

.view-all {
  color: var(--accent-orange);
  text-decoration: none;
  font-size: var(--text-sm);
}

.links-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.link-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-4);
  background: var(--gray-50);
  border-radius: var(--radius-lg);
  flex-wrap: wrap;
  gap: var(--spacing-3);
}

.link-info h4 {
  margin: 0 0 var(--spacing-1) 0;
  color: var(--primary-blue);
}

.link-info code {
  font-size: var(--text-xs);
  color: var(--gray-500);
}

.link-stats {
  display: flex;
  gap: var(--spacing-4);
}

.link-stats span {
  font-size: var(--text-sm);
  color: var(--gray-500);
}

.link-stats i {
  margin-right: var(--spacing-1);
  color: var(--accent-orange);
}

.loading-state, .empty-state {
  text-align: center;
  padding: var(--spacing-8);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--gray-200);
  border-top-color: var(--accent-orange);
  border-radius: 50%;
  margin: 0 auto;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state i {
  font-size: var(--text-4xl);
  color: var(--gray-300);
  margin-bottom: var(--spacing-4);
}

.empty-state p {
  color: var(--gray-500);
  margin-bottom: var(--spacing-4);
}

@media (max-width: 768px) {
  .partner-dashboard {
    padding: var(--spacing-4);
  }
  
  .welcome-section {
    flex-direction: column;
    text-align: center;
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
</style>
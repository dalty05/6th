<template>
  <div class="partner-analytics">
    <div class="page-header">
      <div>
        <h1>Analytics Dashboard</h1>
        <p>Track your referral performance and marketing ROI</p>
      </div>
    </div>
    
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading analytics data...</p>
    </div>
    
    <div v-else>
      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card">
          <i class="fas fa-mouse-pointer"></i>
          <div class="stat-info">
            <h3>{{ stats.totalClicks || 0 }}</h3>
            <p>Total Clicks</p>
            <span class="trend" v-if="stats.clickTrend">
              <i :class="stats.clickTrend > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(stats.clickTrend) }}%
            </span>
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
      
      <!-- Performance Chart -->
      <AnalyticsChart 
        title="Performance Overview"
        :data="chartData"
        @rangeChange="updateDateRange"
      />
      
      <!-- Top Links -->
      <div class="top-links-section">
        <h3>Your Top Performing Links</h3>
        <div class="top-links-list">
          <div v-for="(link, index) in topLinks" :key="link.id" class="top-link-item">
            <div class="rank">{{ index + 1 }}</div>
            <div class="link-details">
              <strong>{{ link.name }}</strong>
              <code>{{ baseUrl }}/r/{{ link.link_code }}</code>
            </div>
            <div class="link-performance">
              <span class="clicks">{{ link.total_clicks }} clicks</span>
              <span class="rate">{{ link.conversion_rate }}% conv.</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Clicks Table -->
      <div class="recent-clicks-section">
        <h3>Recent Clicks</h3>
        <DataTable 
          :data="recentClicks" 
          :columns="clickColumns" 
          :loading="clicksLoading"
          :show-toolbar="false"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import referralService from '@/services/referral'
import AnalyticsChart from '@/components/partner/AnalyticsChart.vue'
import DataTable from '@/components/admin/DataTable.vue'

const loading = ref(true)
const clicksLoading = ref(false)
const stats = ref({})
const chartData = ref({ labels: [], clicks: [], conversions: [] })
const topLinks = ref([])
const recentClicks = ref([])
const baseUrl = window.location.origin

const clickColumns = [
  { key: 'clicked_at', label: 'Date', type: 'date', sortable: true },
  { key: 'ip_address', label: 'IP Address' },
  { key: 'referrer_url', label: 'Source', type: 'truncate', maxLength: 50 },
  { key: 'link_name', label: 'Link' }
]

const loadAnalytics = async (days = 30) => {
  loading.value = true
  try {
    const response = await referralService.getAnalytics(days)
    stats.value = response.stats
    chartData.value = response.chartData
    topLinks.value = response.topLinks || []
  } catch (error) {
    console.error('Error loading analytics:', error)
  } finally {
    loading.value = false
  }
}

const loadRecentClicks = async () => {
  clicksLoading.value = true
  try {
    const response = await referralService.getRecentClicks()
    recentClicks.value = response
  } catch (error) {
    console.error('Error loading recent clicks:', error)
  } finally {
    clicksLoading.value = false
  }
}

const updateDateRange = (days) => {
  loadAnalytics(days)
}

onMounted(() => {
  loadAnalytics()
  loadRecentClicks()
})
</script>

<style scoped>
.partner-analytics {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  color: #1e3a8a;
  margin-bottom: 0.25rem;
}

.page-header p {
  color: #666;
}

.loading-state {
  text-align: center;
  padding: 4rem;
  background: white;
  border-radius: 16px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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

.trend {
  font-size: 0.7rem;
  color: #10b981;
}

.top-links-section, .recent-clicks-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.top-links-section h3, .recent-clicks-section h3 {
  color: #1e3a8a;
  margin-bottom: 1rem;
}

.top-links-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.top-link-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 12px;
}

.rank {
  width: 32px;
  height: 32px;
  background: #f59e0b;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.link-details {
  flex: 1;
}

.link-details strong {
  display: block;
  color: #1e3a8a;
}

.link-details code {
  font-size: 0.7rem;
  color: #666;
}

.link-performance {
  text-align: right;
}

.link-performance .clicks {
  display: block;
  font-weight: bold;
  color: #1e3a8a;
}

.link-performance .rate {
  font-size: 0.7rem;
  color: #10b981;
}

@media (max-width: 768px) {
  .partner-analytics {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .top-link-item {
    flex-wrap: wrap;
  }
  
  .link-performance {
    width: 100%;
    text-align: left;
    margin-left: 42px;
  }
}
</style>
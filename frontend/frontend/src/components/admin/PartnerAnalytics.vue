<!-- frontend/src/components/admin/PartnerAnalytics.vue -->

<template>
  <div class="partner-analytics">
    <!-- Header -->
    <div class="analytics-header">
      <div class="header-left">
        <h1><i class="fas fa-chart-line"></i> My Referral Analytics</h1>
        <p>Track and analyze your referral performance</p>
        <div class="referral-code-box" v-if="overview.referral_code">
          <span class="code-label">Your Referral Code:</span>
          <code class="referral-code">{{ overview.referral_code }}</code>
          <button @click="copyReferralCode" class="copy-btn">
            <i class="fas fa-copy"></i> Copy
          </button>
        </div>
      </div>
      <div class="header-right">
        <div class="filter-group">
          <label>Period:</label>
          <select v-model="days" @change="loadAnalytics">
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="60">Last 60 days</option>
            <option value="90">Last 90 days</option>
            <option value="180">Last 180 days</option>
          </select>
          <button @click="loadAnalytics" class="btn-refresh" :disabled="loading">
            <i class="fas fa-sync-alt" :class="{ spinning: loading }"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading your analytics...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      <h3>Error Loading Analytics</h3>
      <p>{{ error }}</p>
      <button @click="loadAnalytics" class="btn-primary">Retry</button>
    </div>

    <!-- Analytics Content -->
    <div v-else class="analytics-content">
      <!-- Overview Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue">
            <i class="fas fa-link"></i>
          </div>
          <div class="stat-info">
            <h3>{{ formatNumber(overview.total_links || 0) }}</h3>
            <p>My Links</p>
            <span class="stat-change positive" v-if="overview.recent_links > 0">
              <i class="fas fa-arrow-up"></i> {{ overview.recent_links }} new
            </span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">
            <i class="fas fa-mouse-pointer"></i>
          </div>
          <div class="stat-info">
            <h3>{{ formatNumber(overview.total_clicks || 0) }}</h3>
            <p>Total Clicks</p>
            <span class="stat-change positive" v-if="overview.recent_clicks > 0">
              <i class="fas fa-arrow-up"></i> {{ overview.recent_clicks }} recent
            </span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon purple">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-info">
            <h3>{{ formatNumber(overview.total_unique_clicks || 0) }}</h3>
            <p>Unique Visitors</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">
            <i class="fas fa-percentage"></i>
          </div>
          <div class="stat-info">
            <h3>{{ overview.conversion_rate || 0 }}%</h3>
            <p>Conversion Rate</p>
            <span class="stat-change">
              {{ overview.total_conversions || 0 }} conversions
            </span>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
          <div class="charts-row">
      <div class="chart-card">
        <h3>Click Trend</h3>
        <div class="chart-container">
          <canvas ref="trendChart"></canvas>
          <!-- Show message when no data -->
          <div v-if="!hasClickData" class="chart-empty-state">
            <i class="fas fa-chart-line"></i>
            <p>No click data available yet</p>
            <span>Share your referral links to start tracking</span>
          </div>
        </div>
      </div>
      <div class="chart-card">
        <h3>Top Sources</h3>
        <div class="chart-container">
          <canvas ref="sourcesChart"></canvas>
          <!-- Show message when no data -->
          <div v-if="!hasSourceData" class="chart-empty-state">
            <i class="fas fa-globe"></i>
            <p>No source data available</p>
            <span>Clicks will be tracked from different sources</span>
          </div>
        </div>
      </div>
    </div>


      <!-- Top Links -->
      <div class="section-card">
        <div class="section-header">
          <h3><i class="fas fa-trophy"></i> My Top Performing Links</h3>
          <span class="section-count">{{ topLinks.length }} links</span>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Link Name</th>
                <th>Code</th>
                <th>Clicks</th>
                <th>Unique</th>
                <th>Conversions</th>
                <th>Rate</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="link in topLinks" :key="link.id">
                <td>{{ link.name }}</td>
                <td><code>{{ link.link_code }}</code></td>
                <td>{{ formatNumber(link.total_clicks) }}</td>
                <td>{{ formatNumber(link.unique_clicks) }}</td>
                <td>{{ formatNumber(link.conversions) }}</td>
                <td>
                  <span class="rate-badge" :class="getRateClass(link.conversion_rate)">
                    {{ link.conversion_rate || 0 }}%
                  </span>
                </td>
              </tr>
              <tr v-if="topLinks.length === 0">
                <td colspan="6" class="no-data">No links found. Create your first referral link!</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

  
      <!-- Quick Action -->
      <div class="quick-action">
        <router-link to="/admin/dashboard?tab=partner-links" class="action-btn">
          <i class="fas fa-plus-circle"></i>
          Create New Referral Link
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, watch } from 'vue'
import { toast } from 'vue3-toastify'
import referralService from '@/services/referral'
import { Chart, registerables, Filler } from 'chart.js'

Chart.register(...registerables, Filler)

// ============================================================
// STATE
// ============================================================

const loading = ref(false)
const error = ref(null)
const days = ref(30)
const analyticsData = ref(null)

// Chart refs
const trendChart = ref(null)
const sourcesChart = ref(null)

let trendChartInstance = null
let sourcesChartInstance = null

// ============================================================
// COMPUTED
// ============================================================

const overview = computed(() => analyticsData.value?.overview || {})
const topLinks = computed(() => analyticsData.value?.top_links || [])
const dailyTrend = computed(() => analyticsData.value?.daily_trend || { dates: [], clicks: [] })
const topSources = computed(() => analyticsData.value?.top_sources || [])
const recentActivity = computed(() => analyticsData.value?.recent_activity || [])

// ============================================================
// METHODS
// ============================================================

// ✅ Check if there's data for charts
const hasClickData = computed(() => {
  return dailyTrend.value.clicks && dailyTrend.value.clicks.some(c => c > 0)
})

const hasSourceData = computed(() => {
  return topSources.value && topSources.value.length > 0 && topSources.value.some(s => s.count > 0)
})





const loadAnalytics = async () => {
  loading.value = true
  error.value = null
  
  try {
    const data = await referralService.getAnalytics(days.value)
    analyticsData.value = data
    
    await nextTick()
    initCharts()
    
  } catch (err) {
    console.error('Error loading analytics:', err)
    error.value = err.response?.data?.error || 'Failed to load analytics'
    toast.error('Failed to load analytics')
  } finally {
    loading.value = false
  }
}
const initCharts = () => {
  // Trend Chart - Only create if there's data
  if (trendChartInstance) {
    trendChartInstance.destroy()
  }
  
  if (trendChart.value && hasClickData.value && dailyTrend.value.dates.length > 0) {
    const ctx = trendChart.value.getContext('2d')
    const labels = dailyTrend.value.dates.map(d => {
      return new Date(d).toLocaleDateString('en-KE', { month: 'short', day: 'numeric' })
    })
    
    trendChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Clicks',
          data: dailyTrend.value.clicks || [],
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointBackgroundColor: '#2563eb'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.parsed.y + ' clicks'
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(0,0,0,0.05)' },
            ticks: { stepSize: 1 }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    })
  }

  // Sources Chart - Only create if there's data
  if (sourcesChartInstance) {
    sourcesChartInstance.destroy()
  }
  
  if (sourcesChart.value && hasSourceData.value) {
    const ctx = sourcesChart.value.getContext('2d')
    const colors = ['#2563eb', '#16a34a', '#f59e0b', '#7c3aed', '#dc2626', '#0d9488', '#ea580c', '#4f46e5', '#0891b2', '#b45309']
    
    sourcesChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: topSources.value.map(s => s.source),
        datasets: [{
          data: topSources.value.map(s => s.count),
          backgroundColor: colors.slice(0, topSources.value.length),
          borderWidth: 2,
          borderColor: '#fff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 12,
              font: { size: 11 }
            }
          }
        }
      }
    })
  }
}


const getRateClass = (rate) => {
  if (rate >= 20) return 'high'
  if (rate >= 10) return 'medium'
  return 'low'
}

const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  
  if (diff < 60) return 'Just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return date.toLocaleDateString('en-KE', { month: 'short', day: 'numeric' })
}

const copyReferralCode = () => {
  if (overview.value.referral_code) {
    navigator.clipboard.writeText(overview.value.referral_code)
    toast.success('Referral code copied to clipboard!')
  }
}

// Watch days change
watch(days, () => {
  loadAnalytics()
})

// ============================================================
// LIFECYCLE
// ============================================================

onMounted(() => {
  loadAnalytics()
})

onUnmounted(() => {
  if (trendChartInstance) {
    trendChartInstance.destroy()
    trendChartInstance = null
  }
  if (sourcesChartInstance) {
    sourcesChartInstance.destroy()
    sourcesChartInstance = null
  }
})
</script>

<style scoped>
.partner-analytics {
  padding: 24px;
}

/* Header */
.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 4px 0;
}

.header-left h1 i {
  color: #2563eb;
  margin-right: 8px;
}

.header-left p {
  color: #64748b;
  margin: 0 0 12px 0;
}

.referral-code-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f1f5f9;
  padding: 6px 12px;
  border-radius: 8px;
  flex-wrap: wrap;
}

.code-label {
  font-size: 13px;
  color: #64748b;
}

.referral-code {
  font-family: monospace;
  font-size: 14px;
  font-weight: 600;
  color: #2563eb;
  background: white;
  padding: 2px 10px;
  border-radius: 4px;
}

.copy-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.copy-btn:hover {
  background: #e2e8f0;
  color: #1a1a2e;
}


.quick-action {
  margin-top: 24px;
  text-align: center;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}


.partner-analytics {
  padding: 24px;
}

/* Header */
.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 4px 0;
}

.header-left h1 i {
  color: #2563eb;
  margin-right: 8px;
}

.header-left p {
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 500;
  color: #1a1a2e;
}

.filter-group select {
  padding: 6px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
}

.filter-group select:focus {
  outline: none;
  border-color: #2563eb;
}

.btn-refresh {
  padding: 6px 12px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Loading & Error */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #94a3b8;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

.error-state {
  text-align: center;
  padding: 60px 0;
}

.error-state i {
  font-size: 48px;
  color: #dc2626;
  margin-bottom: 16px;
}

.error-state h3 {
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.error-state p {
  color: #64748b;
  margin: 0 0 16px 0;
}

.btn-primary {
  padding: 8px 24px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.btn-primary:hover {
  background: #1d4ed8;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.stat-icon.blue {
  background: #dbeafe;
  color: #2563eb;
}

.stat-icon.green {
  background: #dcfce7;
  color: #16a34a;
}

.stat-icon.purple {
  background: #f3e8ff;
  color: #7c3aed;
}

.stat-icon.orange {
  background: #fef3c7;
  color: #f59e0b;
}

.stat-info h3 {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 2px 0;
}

.stat-info p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.stat-change {
  font-size: 12px;
  color: #94a3b8;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.stat-change.positive {
  color: #16a34a;
}

/* Charts */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.chart-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 16px 0;
}

.chart-container {
  height: 200px;
}

/* Section Cards */
.section-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.section-header h3 i {
  color: #2563eb;
  margin-right: 8px;
}

.section-count {
  font-size: 13px;
  color: #94a3b8;
}

/* Tables */
.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead th {
  text-align: left;
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #f1f5f9;
}

.data-table tbody td {
  padding: 10px 12px;
  font-size: 14px;
  color: #1a1a2e;
  border-bottom: 1px solid #f1f5f9;
}

.data-table tbody tr:hover {
  background: #f8fafc;
}

.data-table code {
  font-family: monospace;
  font-size: 12px;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
}

.rate-badge {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.rate-badge.high {
  background: #dcfce7;
  color: #16a34a;
}

.rate-badge.medium {
  background: #fef3c7;
  color: #f59e0b;
}

.rate-badge.low {
  background: #fee2e2;
  color: #dc2626;
}

.no-data {
  text-align: center;
  padding: 20px !important;
  color: #94a3b8;
}

/* Activity List */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

.activity-icon.click {
  background: #dbeafe;
  color: #2563eb;
}

.activity-content {
  flex: 1;
}

.activity-content p {
  margin: 0;
  font-size: 14px;
  color: #1a1a2e;
}

.activity-detail {
  color: #64748b;
}

.conversion-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #16a34a;
  font-size: 12px;
  font-weight: 500;
  margin-left: 8px;
}

.activity-time {
  font-size: 12px;
  color: #94a3b8;
}

.no-activity {
  text-align: center;
  padding: 24px 0;
  color: #94a3b8;
}

.no-activity i {
  font-size: 32px;
  margin-bottom: 8px;
}

.no-activity p {
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .analytics-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
  }
  
  .filter-group {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .filter-group select {
    flex: 1;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .charts-row {
    grid-template-columns: 1fr;
  }
  
  .data-table {
    font-size: 13px;
  }
  
  .data-table thead th,
  .data-table tbody td {
    padding: 6px 8px;
  }
}
</style>
<template>
  <div class="advanced-analytics">
    <!-- Header -->
    <div class="analytics-header">
      <div>
        <h2>Partner Analytics</h2>
        <p>Track referral performance and partner activity</p>
      </div>
      <div class="header-actions">
        <button @click="exportData" class="btn btn-outline">
          <i class="fas fa-download"></i> Export Report
        </button>
        <button @click="refreshData" class="btn btn-outline">
          <i class="fas fa-sync-alt"></i> Refresh
        </button>
      </div>
    </div>

    <!-- Partner Filter (Super Admin only) -->
    <div class="partner-filter" v-if="isSuperAdmin">
      <label>Filter by Partner:</label>
      <select v-model="selectedPartnerId" @change="loadAnalytics">
        <option value="all">All Partners</option>
        <option v-for="partner in partners" :key="partner.id" :value="partner.id">
          {{ partner.full_name }} ({{ partner.email }})
        </option>
      </select>
    </div>

    <!-- Date Range Filter -->
    <div class="date-range-filter">
      <div class="filter-group">
        <label>Date Range:</label>
        <select v-model="dateRange.preset" @change="applyPresetRange">
          <option value="last7">Last 7 Days</option>
          <option value="last30">Last 30 Days</option>
          <option value="last90">Last 90 Days</option>
          <option value="this_month">This Month</option>
          <option value="custom">Custom Range</option>
        </select>
      </div>
      <div v-if="dateRange.preset === 'custom'" class="custom-range">
        <input type="date" v-model="dateRange.start" class="date-input">
        <span>to</span>
        <input type="date" v-model="dateRange.end" class="date-input">
        <button @click="applyCustomRange" class="btn btn-sm btn-primary">Apply</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading analytics...</p>
    </div>

    <div v-else>
      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon blue"><i class="fas fa-users"></i></div>
          <div class="kpi-content">
            <span class="kpi-value">{{ formatNumber(totalPartners) }}</span>
            <span class="kpi-label">Active Partners</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon green"><i class="fas fa-link"></i></div>
          <div class="kpi-content">
            <span class="kpi-value">{{ formatNumber(totalLinks) }}</span>
            <span class="kpi-label">Referral Links</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon orange"><i class="fas fa-mouse-pointer"></i></div>
          <div class="kpi-content">
            <span class="kpi-value">{{ formatNumber(totalClicks) }}</span>
            <span class="kpi-label">Total Clicks</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon purple"><i class="fas fa-users"></i></div>
          <div class="kpi-content">
            <span class="kpi-value">{{ formatNumber(uniqueVisitors) }}</span>
            <span class="kpi-label">Unique Visitors</span>
          </div>
        </div>
      </div>

      <!-- Performance Chart -->
      <div class="chart-card">
        <h3>Clicks Over Time</h3>
        <div class="chart-container">
          <canvas ref="chartCanvas"></canvas>
        </div>
      </div>

      <!-- Two Column Layout -->
      <div class="two-column">
        <!-- Top Performing Partners -->
        <div class="top-partners-card">
          <div class="card-header">
            <h3>Top Performing Partners</h3>
            <div class="card-controls">
              <select v-model="leaderboardSort" class="sort-select">
                <option value="clicks">Sort by Clicks</option>
                <option value="links">Sort by Links</option>
              </select>
            </div>
          </div>
          <div class="top-partners-list">
            <div v-for="(partner, index) in topPartners" :key="partner.id" class="partner-item">
              <div class="rank">{{ index + 1 }}</div>
              <div class="partner-info">
                <strong>{{ partner.full_name }}</strong>
                <span>{{ partner.email }}</span>
              </div>
              <div class="partner-stats">
                <span class="clicks">{{ formatNumber(partner.total_clicks) }} clicks</span>
                <span class="links">{{ partner.link_count || 0 }} links</span>
              </div>
            </div>
            <div v-if="topPartners.length === 0" class="no-data">No partner data available</div>
          </div>
        </div>

        <!-- Recent Clicks Activity -->
        <div class="recent-clicks-card">
          <h3>Recent Clicks Activity</h3>
          <div class="recent-clicks-list">
            <div v-for="click in recentClicks" :key="click.id" class="click-item">
              <div class="click-icon">
                <i class="fas fa-mouse-pointer"></i>
              </div>
              <div class="click-details">
                <p><strong>{{ click.partner_name || 'Unknown Partner' }}</strong></p>
                <small>{{ formatDateTime(click.clicked_at) }}</small>
              </div>
              <div class="click-location">
                <i class="fas fa-map-marker-alt"></i> {{ click.ip_address || 'Unknown' }}
              </div>
            </div>
            <div v-if="recentClicks.length === 0" class="no-data">No recent clicks</div>
          </div>
        </div>
      </div>

      <!-- Partners Table (Partners Only) -->
      <div class="partners-table-card">
        <div class="card-header">
          <h3>All Partners</h3>
          <div class="table-controls">
            <div class="search-box-small">
              <i class="fas fa-search"></i>
              <input type="text" v-model="partnerSearch" placeholder="Search partners...">
            </div>
            <select v-model="partnerSort" class="sort-select">
              <option value="clicks">Sort by Clicks</option>
              <option value="links">Sort by Links</option>
              <option value="name">Sort by Name</option>
              <option value="newest">Sort by Newest</option>
            </select>
          </div>
        </div>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Partner</th>
                <th>Email</th>
                <th>Referral Code</th>
                <th>Links</th>
                <th>Total Clicks</th>
                <th>Unique</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="partner in filteredPartners" :key="partner.id">
                <td>
                  <div class="partner-cell">
                    <i class="fas fa-user-circle"></i>
                    <strong>{{ partner.full_name }}</strong>
                  </div>
                </td>
                <td>{{ partner.email }}</td>
                <td>
                  <code class="referral-code">{{ partner.referral_code || 'N/A' }}</code>
                  <button v-if="partner.referral_code" @click="copyCode(partner.referral_code)" class="copy-code-btn" title="Copy">
                    <i class="fas fa-copy"></i>
                  </button>
                </td>
                <td class="number-cell">{{ partner.link_count || 0 }}</td>
                <td class="number-cell">{{ formatNumber(partner.total_clicks || 0) }}</td>
                <td class="number-cell">{{ formatNumber(partner.unique_clicks || 0) }}</td>
                <td>{{ formatDate(partner.created_at) }}</td>
                <td class="actions-cell">
                  <button @click="viewPartnerDetails(partner)" class="action-icon view" title="View Details">
                    <i class="fas fa-eye"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="filteredPartners.length === 0">
                <td colspan="8" class="empty-row">No partners found</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination" v-if="filteredPartners.length > 0">
          <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">Previous</button>
          <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">Next</button>
        </div>
      </div>
    </div>

    <!-- Partner Details Modal -->
    <div class="modal-overlay" v-if="showDetailsModal" @click.self="closeDetailsModal">
      <div class="modal-container large">
        <div class="modal-header">
          <h2>Partner Details</h2>
          <button class="close-btn" @click="closeDetailsModal">&times;</button>
        </div>
        <div class="modal-body" v-if="selectedPartner">
          <div class="detail-section">
            <h4>Personal Information</h4>
            <div class="detail-row">
              <span class="detail-label">Name:</span>
              <span class="detail-value">{{ selectedPartner.full_name }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Email:</span>
              <span class="detail-value">{{ selectedPartner.email }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Referral Code:</span>
              <code class="referral-code">{{ selectedPartner.referral_code || 'Not generated' }}</code>
            </div>
          </div>
          <div class="detail-section">
            <h4>Performance Stats</h4>
            <div class="detail-row">
              <span class="detail-label">Total Links:</span>
              <span class="detail-value">{{ selectedPartner.link_count || 0 }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Total Clicks:</span>
              <span class="detail-value">{{ formatNumber(selectedPartner.total_clicks || 0) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Unique Visitors:</span>
              <span class="detail-value">{{ formatNumber(selectedPartner.unique_clicks || 0) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Conversion Rate:</span>
              <span class="detail-value">{{ selectedPartner.conversion_rate || 0 }}%</span>
            </div>
          </div>
          <div class="detail-section" v-if="selectedPartner.referral_links?.length">
            <h4>Referral Links</h4>
            <div class="links-list">
              <div v-for="link in selectedPartner.referral_links" :key="link.id" class="link-item">
                <div class="link-info">
                  <strong>{{ link.name }}</strong>
                  <code>{{ link.link_code }}</code>
                </div>
                <div class="link-stats">
                  <span><i class="fas fa-mouse-pointer"></i> {{ link.total_clicks || 0 }} clicks</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeDetailsModal" class="btn-secondary">Close</button>
        </div>
      </div>
    </div>

    <!-- Notification -->
    <div v-if="notification.show" :class="['notification', notification.type]" @click="notification.show = false">
      <i :class="notification.icon"></i>
      <span>{{ notification.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import Chart from 'chart.js/auto'
import api from '@/services/api'
import authService from '@/services/auth'

// State
const loading = ref(false)
const partners = ref([])
const totalPartners = ref(0)
const totalLinks = ref(0)
const totalClicks = ref(0)
const uniqueVisitors = ref(0)
const dailyClicks = ref([])
const recentClicks = ref([])
const selectedPartnerId = ref('all')
const partnerSearch = ref('')
const partnerSort = ref('clicks')
const currentPage = ref(1)
const itemsPerPage = 15

const showDetailsModal = ref(false)
const selectedPartner = ref(null)

// User permissions
const currentUser = authService.getUser()
const isSuperAdmin = computed(() => currentUser?.role === 'super_admin')

const dateRange = ref({
  preset: 'last30',
  start: '',
  end: ''
})

const leaderboardSort = ref('clicks')
let chart = null
const chartCanvas = ref(null)

const notification = ref({
  show: false,
  message: '',
  type: 'success',
  icon: 'fas fa-check-circle'
})

// Computed
const sortedPartners = computed(() => {
  let sorted = [...partners.value]
  if (leaderboardSort.value === 'clicks') {
    sorted.sort((a, b) => (b.total_clicks || 0) - (a.total_clicks || 0))
  } else {
    sorted.sort((a, b) => (b.link_count || 0) - (a.link_count || 0))
  }
  return sorted.slice(0, 10)
})

const topPartners = computed(() => sortedPartners.value.slice(0, 5))

const filteredPartners = computed(() => {
  let filtered = [...partners.value]
  
  if (partnerSearch.value) {
    const query = partnerSearch.value.toLowerCase()
    filtered = filtered.filter(p => 
      p.full_name.toLowerCase().includes(query) || 
      p.email.toLowerCase().includes(query)
    )
  }
  
  if (partnerSort.value === 'clicks') {
    filtered.sort((a, b) => (b.total_clicks || 0) - (a.total_clicks || 0))
  } else if (partnerSort.value === 'links') {
    filtered.sort((a, b) => (b.link_count || 0) - (a.link_count || 0))
  } else if (partnerSort.value === 'name') {
    filtered.sort((a, b) => a.full_name.localeCompare(b.full_name))
  } else if (partnerSort.value === 'newest') {
    filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }
  
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredPartners.value.length / itemsPerPage))
const paginatedPartners = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredPartners.value.slice(start, start + itemsPerPage)
})

// Methods
const showNotification = (message, type = 'success') => {
  notification.value = { show: true, message, type, icon: type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle' }
  setTimeout(() => notification.value.show = false, 3000)
}

const getDateRangeDays = () => {
  if (dateRange.value.preset === 'custom' && dateRange.value.start && dateRange.value.end) {
    const start = new Date(dateRange.value.start)
    const end = new Date(dateRange.value.end)
    return Math.ceil((end - start) / (1000 * 60 * 60 * 24))
  }
  const ranges = { last7: 7, last30: 30, last90: 90, this_month: 30 }
  return ranges[dateRange.value.preset] || 30
}

const applyPresetRange = () => {
  if (dateRange.value.preset !== 'custom') loadAnalytics()
}

const applyCustomRange = () => {
  if (dateRange.value.start && dateRange.value.end) loadAnalytics()
  else showNotification('Select both start and end dates', 'error')
}

const loadPartners = async () => {
  try {
    const response = await api.get('/admin/users')
    const allUsers = response.data
    const partnersData = allUsers.filter(user => user.role === 'partner')
    partners.value = partnersData
    totalPartners.value = partnersData.length
  } catch (error) {
    console.error('Error loading partners:', error)
  }
}

const loadAnalytics = async () => {
  loading.value = true
  try {
    const days = getDateRangeDays()
    const params = { days }
    if (selectedPartnerId.value !== 'all') params.partner_id = selectedPartnerId.value
    
    const response = await api.get('/referral/analytics/partner', { params })
    const data = response.data
    
    totalClicks.value = data.total_clicks || 0
    uniqueVisitors.value = data.unique_visitors || 0
    totalLinks.value = data.total_links || 0
    dailyClicks.value = data.daily_clicks || []
    recentClicks.value = data.recent_clicks || []
    
    // Update partner stats
    if (data.partner_stats) {
      for (const partner of partners.value) {
        const stats = data.partner_stats.find(p => p.id === partner.id)
        if (stats) {
          partner.total_clicks = stats.total_clicks || 0
          partner.unique_clicks = stats.unique_clicks || 0
          partner.link_count = stats.link_count || 0
          partner.referral_links = stats.referral_links || []
        }
      }
    }
    
    updateChart()
  } catch (error) {
    console.error('Error loading analytics:', error)
    showNotification('Failed to load analytics', 'error')
  } finally {
    loading.value = false
  }
}

const updateChart = () => {
  if (chart) chart.destroy()
  
  const ctx = chartCanvas.value?.getContext('2d')
  if (!ctx || !dailyClicks.value.length) return
  
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dailyClicks.value.map(d => d.date),
      datasets: [{
        label: 'Clicks',
        data: dailyClicks.value.map(d => d.clicks),
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245, 158, 11, 0.1)',
        fill: true,
        tension: 0.3,
        pointBackgroundColor: '#f59e0b',
        pointBorderColor: '#fff',
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toLocaleString()}`
          }
        }
      },
      scales: {
        y: { beginAtZero: true, ticks: { callback: (v) => v.toLocaleString() } }
      }
    }
  })
}

const viewPartnerDetails = async (partner) => {
  try {
    const statsRes = await api.get(`/referral/partner/${partner.id}/stats`)
    partner.link_count = statsRes.data.total_links || 0
    partner.total_clicks = statsRes.data.total_clicks || 0
    partner.unique_clicks = statsRes.data.total_unique_clicks || 0
    partner.referral_links = statsRes.data.links || []
    partner.conversion_rate = partner.total_clicks ? ((partner.total_conversions || 0) / partner.total_clicks * 100).toFixed(1) : 0
    selectedPartner.value = partner
    showDetailsModal.value = true
  } catch (error) {
    showNotification('Failed to load partner details', 'error')
  }
}

const copyCode = (code) => {
  navigator.clipboard.writeText(code)
  showNotification('Referral code copied')
}

const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const prevPage = () => { if (currentPage.value > 1) currentPage.value-- }
const nextPage = () => { if (currentPage.value < totalPages.value) currentPage.value++ }

const exportData = () => {
  const data = {
    exported_at: new Date().toISOString(),
    date_range: dateRange.value,
    total_clicks: totalClicks.value,
    unique_visitors: uniqueVisitors.value,
    total_links: totalLinks.value,
    partners: partners.value.map(p => ({
      name: p.full_name,
      email: p.email,
      clicks: p.total_clicks,
      links: p.link_count
    }))
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `partner_analytics_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  showNotification('Report exported')
}

const refreshData = () => { loadPartners(); loadAnalytics() }

const setDefaultDateRange = () => {
  const today = new Date()
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(today.getDate() - 30)
  dateRange.value.start = thirtyDaysAgo.toISOString().split('T')[0]
  dateRange.value.end = today.toISOString().split('T')[0]
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedPartner.value = null
}

onMounted(() => {
  setDefaultDateRange()
  loadPartners()
  loadAnalytics()
})
</script>

<style scoped>
.advanced-analytics {
  padding: 1rem;
  background: #f8fafc;
  min-height: 100vh;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.analytics-header h2 {
  color: #1e3a8a;
  margin: 0 0 0.25rem;
}

.analytics-header p {
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.partner-filter {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.partner-filter select {
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  min-width: 250px;
}

.date-range-filter {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.kpi-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid #e5e7eb;
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-icon.blue { background: #e0e7ff; color: #1e3a8a; }
.kpi-icon.green { background: #d1fae5; color: #065f46; }
.kpi-icon.orange { background: #fed7aa; color: #9a3412; }
.kpi-icon.purple { background: #e0e7ff; color: #1e3a8a; }

.kpi-icon i { font-size: 1.25rem; }
.kpi-value { font-size: 1.5rem; font-weight: 700; color: #1e3a8a; display: block; }
.kpi-label { font-size: 0.75rem; color: #6b7280; }

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border: 1px solid #e5e7eb;
}

.chart-card h3 {
  color: #1e3a8a;
  margin: 0 0 1rem;
  font-size: 1rem;
}

.chart-container {
  height: 300px;
}

.two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.top-partners-card, .recent-clicks-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid #e5e7eb;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.top-partners-card h3, .recent-clicks-card h3 {
  color: #1e3a8a;
  margin: 0;
  font-size: 1rem;
}

.top-partners-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.partner-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 10px;
}

.rank {
  width: 28px;
  height: 28px;
  background: #f59e0b;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.8rem;
}

.partner-info {
  flex: 1;
}

.partner-info strong { display: block; color: #1e3a8a; font-size: 0.85rem; }
.partner-info span { font-size: 0.7rem; color: #6b7280; }

.partner-stats { text-align: right; }
.partner-stats .clicks { display: block; font-weight: bold; color: #1e3a8a; font-size: 0.85rem; }
.partner-stats .links { font-size: 0.7rem; color: #10b981; }

.recent-clicks-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 350px;
  overflow-y: auto;
}

.click-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.click-icon {
  width: 32px;
  height: 32px;
  background: #e0e7ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1e3a8a;
}

.click-details { flex: 1; }
.click-details p { margin: 0; font-size: 0.8rem; }
.click-details small { font-size: 0.7rem; color: #9ca3af; }

.click-location { font-size: 0.7rem; color: #6b7280; }

.partners-table-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid #e5e7eb;
}

.search-box-small {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.search-box-small i {
  position: absolute;
  left: 10px;
  color: #9ca3af;
  font-size: 0.8rem;
}

.search-box-small input {
  padding: 0.4rem 0.75rem 0.4rem 2rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.8rem;
  width: 200px;
}

.table-container {
  overflow-x: auto;
  margin-top: 1rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}

.data-table th, .data-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #1e3a8a;
}

.partner-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.partner-cell i {
  font-size: 1.2rem;
  color: #9ca3af;
}

.referral-code {
  font-family: monospace;
  background: #f1f5f9;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.7rem;
}

.copy-code-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #f59e0b;
  margin-left: 0.25rem;
}

.number-cell {
  font-weight: 500;
  text-align: center;
}

.actions-cell .action-icon {
  background: none;
  border: none;
  cursor: pointer;
  color: #3b82f6;
  font-size: 1rem;
}

.actions-cell .action-icon:hover {
  color: #f59e0b;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
}

.page-btn {
  background: white;
  border: 1px solid #e5e7eb;
  padding: 0.3rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  border: none;
}

.btn-outline {
  background: white;
  border: 1px solid #e5e7eb;
}

.btn-outline:hover {
  border-color: #f59e0b;
  color: #f59e0b;
}

.btn-sm { padding: 0.3rem 0.8rem; font-size: 0.8rem; }
.btn-primary { background: #f59e0b; color: white; }

.sort-select {
  padding: 0.3rem 0.6rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.8rem;
  background: white;
}

.loading-state {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #1e3a8a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-container.large { max-width: 700px; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 { margin: 0; color: #1e3a8a; }

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.modal-body { padding: 1.25rem; }
.modal-footer { padding: 1rem 1.25rem; border-top: 1px solid #e5e7eb; display: flex; justify-content: flex-end; }

.detail-section { margin-bottom: 1.5rem; }
.detail-section h4 { color: #1e3a8a; margin: 0 0 0.75rem; }
.detail-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9; }
.detail-label { font-weight: 500; color: #6b7280; }
.detail-value { color: #374151; }

.links-list { display: flex; flex-direction: column; gap: 0.5rem; }
.link-item { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: #f8fafc; border-radius: 8px; }

.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 0.75rem 1.25rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  z-index: 1000;
  cursor: pointer;
}

.notification.success { background: #10b981; color: white; }
.notification.error { background: #ef4444; color: white; }

.empty-row, .no-data { text-align: center; padding: 2rem; color: #9ca3af; }

@media (max-width: 1024px) {
  .two-column { grid-template-columns: 1fr; }
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .kpi-grid { grid-template-columns: 1fr; }
  .partner-filter { flex-direction: column; align-items: stretch; }
  .partner-filter select { width: 100%; }
  .date-range-filter { flex-direction: column; align-items: stretch; }
  .custom-range { flex-wrap: wrap; }
  .search-box-small input { width: 100%; }
  .table-container { overflow-x: scroll; }
  .data-table { min-width: 700px; }
}
</style>
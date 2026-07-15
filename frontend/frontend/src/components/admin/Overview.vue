<template>
  <div class="overview-dashboard">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1>Dashboard Overview</h1>
        <p>Welcome back, {{ user?.full_name || 'Admin' }}! Here's what's happening today.</p>
      </div>
      <div class="header-right">
        <span class="date-display">{{ currentDate }}</span>
        <button @click="refreshData" class="btn-refresh" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ spinning: loading }"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-icon" :class="stat.color">
          <i :class="stat.icon"></i>
        </div>
        <div class="stat-info">
          <h3>{{ formatNumber(stat.value) }}</h3>
          <p>{{ stat.label }}</p>
          <span v-if="stat.change" class="stat-change" :class="stat.change > 0 ? 'positive' : 'negative'">
            <i :class="stat.change > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
            {{ Math.abs(stat.change) }}%
          </span>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <h3>Recent Bookings</h3>
          <span class="chart-period">Last 7 days</span>
        </div>
        <div class="chart-container">
          <canvas ref="bookingsChart"></canvas>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>Revenue Overview</h3>
          <span class="chart-period">Last 7 days</span>
        </div>
        <div class="chart-container">
          <canvas ref="revenueChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h3>Quick Actions</h3>
      <div class="actions-grid">
        <router-link to="/admin/dashboard?tab=products" class="action-card">
          <i class="fas fa-plus-circle"></i>
          <span>Add Product</span>
        </router-link>
        <router-link to="/admin/dashboard?tab=blog" class="action-card">
          <i class="fas fa-pen-fancy"></i>
          <span>Write Blog</span>
        </router-link>
        <router-link to="/admin/dashboard?tab=tours" class="action-card">
          <i class="fas fa-calendar-plus"></i>
          <span>Create Tour</span>
        </router-link>
        <router-link to="/admin/dashboard?tab=jobs" class="action-card">
          <i class="fas fa-briefcase"></i>
          <span>Post Job</span>
        </router-link>
        <router-link to="/admin/dashboard?tab=partners" class="action-card">
          <i class="fas fa-user-plus"></i>
          <span>Add Partner</span>
        </router-link>
        <router-link to="/admin/dashboard?tab=newsletter" class="action-card">
          <i class="fas fa-envelope"></i>
          <span>Send Newsletter</span>
        </router-link>
      </div>
    </div>

    <!-- Two Column Layout -->
    <div class="two-column">
      <!-- Recent Activity -->
      <div class="activity-section">
        <div class="section-header">
          <h3><i class="fas fa-history"></i> Recent Activity</h3>
          <router-link to="/admin/dashboard?tab=activities" class="view-all">
            View All <i class="fas fa-arrow-right"></i>
          </router-link>
        </div>
        <div class="activity-list">
          <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
            <div class="activity-icon" :class="activity.action">
              <i :class="getActivityIcon(activity.action)"></i>
            </div>
            <div class="activity-content">
              <p class="activity-text">{{ activity.description }}</p>
              <span class="activity-time">{{ formatTime(activity.created_at) }}</span>
            </div>
          </div>
          <div v-if="recentActivities.length === 0" class="no-activity">
            <i class="fas fa-inbox"></i>
            <p>No recent activity</p>
          </div>
        </div>
      </div>

      <!-- Upcoming Tours -->
      <div class="upcoming-section">
        <div class="section-header">
          <h3><i class="fas fa-calendar-check"></i> Upcoming Tours</h3>
          <router-link to="/admin/dashboard?tab=tours" class="view-all">
            View All <i class="fas fa-arrow-right"></i>
          </router-link>
        </div>
        <div class="tour-list">
          <div v-for="tour in upcomingTours" :key="tour.id" class="tour-item">
            <div class="tour-date">
              <span class="day">{{ formatDay(tour.tour_date) }}</span>
              <span class="month">{{ formatMonth(tour.tour_date) }}</span>
            </div>
            <div class="tour-info">
              <p class="tour-customer">{{ tour.customer_name }}</p>
              <span class="tour-status" :class="tour.status">
                <i :class="getStatusIcon(tour.status)"></i>
                {{ tour.status }}
              </span>
            </div>
            <div class="tour-people">
              <i class="fas fa-users"></i> {{ tour.people_count || 1 }}
            </div>
          </div>
          <div v-if="upcomingTours.length === 0" class="no-tours">
            <i class="fas fa-calendar-plus"></i>
            <p>No upcoming tours</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Jobs -->
    <div class="jobs-section">
      <div class="section-header">
        <h3><i class="fas fa-briefcase"></i> Recent Jobs</h3>
        <router-link to="/admin/dashboard?tab=jobs" class="view-all">
          View All <i class="fas fa-arrow-right"></i>
        </router-link>
      </div>
      <div class="jobs-grid">
        <div v-for="job in recentJobs" :key="job.id" class="job-card">
          <div class="job-header">
            <h4>{{ job.title }}</h4>
            <span class="job-status" :class="job.is_active ? 'active' : 'inactive'">
              {{ job.is_active ? 'Active' : 'Closed' }}
            </span>
          </div>
          <p class="job-location">
            <i class="fas fa-map-marker-alt"></i> {{ job.location || 'Remote' }}
          </p>
          <div class="job-meta">
            <span><i class="fas fa-calendar-alt"></i> {{ formatDate(job.created_at) }}</span>
            <span><i class="fas fa-eye"></i> {{ job.views_count || 0 }} views</span>
            <span><i class="fas fa-users"></i> {{ job.applications_count || 0 }} applicants</span>
          </div>
        </div>
        <div v-if="recentJobs.length === 0" class="no-jobs">
          <i class="fas fa-briefcase"></i>
          <p>No recent jobs</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed, nextTick } from 'vue'  // ✅ Add nextTick import
import api from '@/services/api'
import authService from '@/services/auth'
import { toast } from 'vue3-toastify'
import { Chart, registerables } from 'chart.js'

// Register Chart.js components
Chart.register(...registerables)

// ============================================================
// STATE
// ============================================================

const user = ref(null)
const loading = ref(false)
const stats = ref([
  { label: 'Total Products', value: 0, icon: 'fas fa-boxes', color: 'blue', change: 0 },
  { label: 'Active Jobs', value: 0, icon: 'fas fa-briefcase', color: 'green', change: 0 },
  { label: 'Total Tours', value: 0, icon: 'fas fa-calendar-check', color: 'orange', change: 0 },
  { label: 'Total Partners', value: 0, icon: 'fas fa-handshake', color: 'purple', change: 0 },
  { label: 'Total Bookings', value: 0, icon: 'fas fa-ticket-alt', color: 'teal', change: 0 },
  { label: 'Revenue', value: 0, icon: 'fas fa-money-bill-wave', color: 'emerald', change: 0 },
])

const recentActivities = ref([])
const upcomingTours = ref([])
const recentJobs = ref([])

// Chart refs
const bookingsChart = ref(null)
const revenueChart = ref(null)

let bookingsChartInstance = null
let revenueChartInstance = null

// ============================================================
// COMPUTED
// ============================================================

const currentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('en-KE', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
})

// ============================================================
// METHODS
// ============================================================

const loadOverview = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/dashboard/overview')
    const data = response.data
    
    // Update stats
    stats.value = [
      { 
        label: 'Total Products', 
        value: data.total_products || 0, 
        icon: 'fas fa-boxes', 
        color: 'blue',
        change: data.products_change || 0
      },
      { 
        label: 'Active Jobs', 
        value: data.total_jobs || 0, 
        icon: 'fas fa-briefcase', 
        color: 'green',
        change: data.jobs_change || 0
      },
      { 
        label: 'Total Tours', 
        value: data.total_tours || 0, 
        icon: 'fas fa-calendar-check', 
        color: 'orange',
        change: data.tours_change || 0
      },
      { 
        label: 'Total Partners', 
        value: data.total_partners || 0, 
        icon: 'fas fa-handshake', 
        color: 'purple',
        change: data.partners_change || 0
      },
      { 
        label: 'Total Bookings', 
        value: data.total_bookings || 0, 
        icon: 'fas fa-ticket-alt', 
        color: 'teal',
        change: data.bookings_change || 0
      },
      { 
        label: 'Revenue', 
        value: data.total_revenue || 0, 
        icon: 'fas fa-money-bill-wave', 
        color: 'emerald',
        change: data.revenue_change || 0
      },
    ]
    
    recentActivities.value = data.recent_activities || []
    upcomingTours.value = data.upcoming_tours || []
    recentJobs.value = data.recent_jobs || []
    
    // Initialize charts after data is loaded
    await nextTick()
    initCharts()
    
  } catch (error) {
    toast.error('Failed to load dashboard data')
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  // Bookings Chart
  if (bookingsChartInstance) {
    bookingsChartInstance.destroy()
  }
  
  if (bookingsChart.value) {
    const ctx = bookingsChart.value.getContext('2d')
    bookingsChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
          label: 'Bookings',
          data: [12, 19, 15, 22, 18, 25, 20],
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          fill: true,
          tension: 0.4,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            grid: {
              display: false
            }
          }
        }
      }
    })
  }

  // Revenue Chart
  if (revenueChartInstance) {
    revenueChartInstance.destroy()
  }
  
  if (revenueChart.value) {
    const ctx = revenueChart.value.getContext('2d')
    revenueChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
          label: 'Revenue (KES)',
          data: [45000, 52000, 38000, 61000, 48000, 72000, 55000],
          backgroundColor: 'rgba(37, 99, 235, 0.7)',
          borderColor: '#2563eb',
          borderWidth: 2,
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            },
            ticks: {
              callback: function(value) {
                return 'KES ' + value.toLocaleString()
              }
            }
          },
          x: {
            grid: {
              display: false
            }
          }
        }
      }
    })
  }
}

const refreshData = async () => {
  await loadOverview()
  toast.success('Dashboard refreshed')
}

const getActivityIcon = (action) => {
  const icons = {
    'login': 'fas fa-sign-in-alt',
    'logout': 'fas fa-sign-out-alt',
    'create': 'fas fa-plus-circle',
    'update': 'fas fa-edit',
    'delete': 'fas fa-trash-alt',
    'approve': 'fas fa-check-circle',
    'reject': 'fas fa-times-circle',
    'booking': 'fas fa-calendar-check',
    'payment': 'fas fa-money-bill-wave',
    'view': 'fas fa-eye',
  }
  return icons[action] || 'fas fa-circle'
}

const getStatusIcon = (status) => {
  const icons = {
    'pending': 'fas fa-clock',
    'confirmed': 'fas fa-check-circle',
    'completed': 'fas fa-check-double',
    'cancelled': 'fas fa-times-circle',
    'rejected': 'fas fa-ban',
    'commitment_pending': 'fas fa-hourglass-half',
    'cleared': 'fas fa-check-circle',
  }
  return icons[status] || 'fas fa-circle'
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
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`
  return date.toLocaleDateString('en-KE', { month: 'short', day: 'numeric', year: 'numeric' })
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-KE', { month: 'short', day: 'numeric', year: 'numeric' })
}

const formatDay = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.getDate().toString().padStart(2, '0')
}

const formatMonth = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return months[date.getMonth()]
}

// ============================================================
// LIFECYCLE
// ============================================================

onMounted(() => {
  user.value = authService.getUser()
  loadOverview()
})
</script>


<style scoped>
.overview-dashboard {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

/* ========== PAGE HEADER ========== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 4px 0;
}

.header-left p {
  color: #64748b;
  margin: 0;
  font-size: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.date-display {
  font-size: 14px;
  color: #64748b;
}

.btn-refresh {
  padding: 8px 16px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 14px;
}

.btn-refresh:hover:not(:disabled) {
  background: #f1f5f9;
  color: #1a1a2e;
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

/* ========== STATS GRID ========== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
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

.stat-icon.orange {
  background: #fef3c7;
  color: #f59e0b;
}

.stat-icon.purple {
  background: #f3e8ff;
  color: #7c3aed;
}

.stat-icon.teal {
  background: #ccfbf1;
  color: #0d9488;
}

.stat-icon.emerald {
  background: #d1fae5;
  color: #059669;
}

.stat-info {
  flex: 1;
}

.stat-info h3 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 2px 0;
  letter-spacing: -0.5px;
}

.stat-info p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.stat-change {
  font-size: 12px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.stat-change.positive {
  color: #16a34a;
}

.stat-change.negative {
  color: #dc2626;
}

/* ========== CHARTS ========== */
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

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.chart-period {
  font-size: 12px;
  color: #94a3b8;
}

.chart-container {
  height: 200px;
}

/* ========== QUICK ACTIONS ========== */
.quick-actions {
  margin-bottom: 24px;
}

.quick-actions h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 12px 0;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  text-decoration: none;
  color: #1a1a2e;
  transition: all 0.2s;
  gap: 8px;
}

.action-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
  color: #2563eb;
}

.action-card i {
  font-size: 24px;
  color: #2563eb;
}

.action-card span {
  font-size: 13px;
  font-weight: 500;
}

/* ========== TWO COLUMN ========== */
.two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* ========== ACTIVITY SECTION ========== */
.activity-section,
.upcoming-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
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

.view-all {
  color: #2563eb;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.view-all:hover {
  text-decoration: underline;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.activity-icon.login {
  background: #dbeafe;
  color: #2563eb;
}

.activity-icon.logout {
  background: #f1f5f9;
  color: #64748b;
}

.activity-icon.create {
  background: #dcfce7;
  color: #16a34a;
}

.activity-icon.update {
  background: #fef3c7;
  color: #f59e0b;
}

.activity-icon.delete {
  background: #fee2e2;
  color: #dc2626;
}

.activity-icon.approve {
  background: #dcfce7;
  color: #16a34a;
}

.activity-icon.reject {
  background: #fee2e2;
  color: #dc2626;
}

.activity-icon.booking {
  background: #dbeafe;
  color: #2563eb;
}

.activity-icon.payment {
  background: #d1fae5;
  color: #059669;
}

.activity-content {
  flex: 1;
}

.activity-text {
  margin: 0;
  font-size: 14px;
  color: #1a1a2e;
}

.activity-time {
  font-size: 12px;
  color: #94a3b8;
}

.no-activity,
.no-tours,
.no-jobs {
  text-align: center;
  padding: 24px 0;
  color: #94a3b8;
}

.no-activity i,
.no-tours i,
.no-jobs i {
  font-size: 32px;
  margin-bottom: 8px;
}

.no-activity p,
.no-tours p,
.no-jobs p {
  margin: 0;
}

/* ========== TOUR LIST ========== */
.tour-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tour-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}

.tour-item:last-child {
  border-bottom: none;
}

.tour-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 44px;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 4px 8px;
}

.tour-date .day {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  line-height: 1.2;
}

.tour-date .month {
  font-size: 10px;
  color: #64748b;
  text-transform: uppercase;
}

.tour-info {
  flex: 1;
}

.tour-customer {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
}

.tour-status {
  font-size: 11px;
  font-weight: 500;
  text-transform: capitalize;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.tour-status.pending {
  color: #f59e0b;
}

.tour-status.confirmed {
  color: #2563eb;
}

.tour-status.completed {
  color: #16a34a;
}

.tour-status.cancelled {
  color: #dc2626;
}

.tour-status.rejected {
  color: #dc2626;
}

.tour-status.commitment_pending {
  color: #f59e0b;
}

.tour-status.cleared {
  color: #16a34a;
}

.tour-people {
  font-size: 13px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ========== JOBS SECTION ========== */
.jobs-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.job-card {
  padding: 16px;
  border: 1px solid #f1f5f9;
  border-radius: 8px;
  transition: all 0.2s;
}

.job-card:hover {
  border-color: #e2e8f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.job-header h4 {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.job-status {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 10px;
  border-radius: 12px;
}

.job-status.active {
  background: #dcfce7;
  color: #16a34a;
}

.job-status.inactive {
  background: #fee2e2;
  color: #dc2626;
}

.job-location {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 8px 0;
}

.job-location i {
  margin-right: 4px;
}

.job-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #94a3b8;
  flex-wrap: wrap;
}

.job-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* ========== RESPONSIVE ========== */
@media (max-width: 1024px) {
  .two-column {
    grid-template-columns: 1fr;
  }
  
  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    justify-content: space-between;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
  
  .actions-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
  
  .jobs-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-info h3 {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .stat-card {
    flex-direction: column;
    text-align: center;
  }
  
  .chart-container {
    height: 150px;
  }
}
</style>
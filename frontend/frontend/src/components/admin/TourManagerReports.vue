<template>
  <div class="tour-manager-reports">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1><i class="fas fa-chart-bar"></i> Reports & Analytics</h1>
        <p class="subtitle">Track performance, revenue, and booking trends</p>
      </div>
      <div class="header-actions">
        <button @click="exportReport('pdf')" class="btn-export-pdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button @click="exportReport('csv')" class="btn-export-csv">
          <i class="fas fa-file-csv"></i> Export CSV
        </button>
        <button @click="refreshData" class="btn-refresh" :disabled="loading">
          <i :class="loading ? 'fas fa-spinner fa-spin' : 'fas fa-sync-alt'"></i>
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Date Range Selector -->
    <div class="date-range-section">
      <div class="date-range-group">
        <label>Date Range</label>
        <div class="date-inputs">
          <input type="date" v-model="dateRange.start" class="date-input">
          <span>to</span>
          <input type="date" v-model="dateRange.end" class="date-input">
        </div>
      </div>
      <div class="quick-ranges">
        <button 
          v-for="range in quickRanges" 
          :key="range.label"
          class="quick-range-btn"
          :class="{ active: activeRange === range.value }"
          @click="setQuickRange(range.value)"
        >
          {{ range.label }}
        </button>
      </div>
      <button @click="applyDateRange" class="btn-apply">
        <i class="fas fa-filter"></i> Apply
      </button>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue"><i class="fas fa-calendar-check"></i></div>
        <div class="stat-info">
          <h3>{{ stats.totalBookings || 0 }}</h3>
          <p>Total Bookings</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green"><i class="fas fa-money-bill-wave"></i></div>
        <div class="stat-info">
          <h3>KES {{ formatPrice(stats.totalRevenue || 0) }}</h3>
          <p>Total Revenue</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <h3>{{ stats.totalVisitors || 0 }}</h3>
          <p>Total Visitors</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple"><i class="fas fa-percent"></i></div>
        <div class="stat-info">
          <h3>{{ stats.conversionRate || 0 }}%</h3>
          <p>Conversion Rate</p>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-grid">
      <!-- Revenue Chart -->
      <div class="chart-card">
        <div class="chart-header">
          <h3><i class="fas fa-chart-line"></i> Revenue Trend</h3>
          <span class="chart-period">{{ dateRangeLabel }}</span>
        </div>
        <div class="chart-body">
          <canvas ref="revenueChartRef"></canvas>
        </div>
      </div>

      <!-- Bookings Chart -->
      <div class="chart-card">
        <div class="chart-header">
          <h3><i class="fas fa-chart-bar"></i> Bookings by Status</h3>
          <span class="chart-period">{{ dateRangeLabel }}</span>
        </div>
        <div class="chart-body">
          <canvas ref="statusChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Popular Packages -->
    <div class="popular-packages">
      <div class="card-header">
        <h3><i class="fas fa-trophy"></i> Popular Packages</h3>
        <span class="subtitle">Most booked tours in this period</span>
      </div>
      <div class="packages-list">
        <div v-if="popularPackages.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>No data available for this period</p>
        </div>
        <div v-else v-for="(pkg, index) in popularPackages" :key="pkg.id" class="package-rank">
          <div class="rank-number">{{ index + 1 }}</div>
          <div class="package-rank-info">
            <span class="package-name">{{ pkg.name }}</span>
            <span class="package-bookings">{{ pkg.total_bookings }} bookings</span>
          </div>
          <div class="package-rank-bar">
            <div class="rank-bar-fill" :style="{ width: pkg.percentage + '%' }"></div>
          </div>
          <span class="package-percentage">{{ pkg.percentage }}%</span>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="recent-activity">
      <div class="card-header">
        <h3><i class="fas fa-clock"></i> Recent Activity</h3>
        <span class="subtitle">Latest booking activity</span>
      </div>
      <div class="activity-list">
        <div v-if="recentActivity.length === 0" class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>No recent activity</p>
        </div>
        <div v-else v-for="activity in recentActivity" :key="activity.id" class="activity-item">
          <div class="activity-icon" :class="activity.type">
            <i :class="getActivityIcon(activity.type)"></i>
          </div>
          <div class="activity-content">
            <span class="activity-text">{{ activity.message }}</span>
            <span class="activity-time">{{ formatTime(activity.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import { format, subDays, subMonths, startOfMonth, endOfMonth } from 'date-fns'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { Line, Bar, Pie } from 'vue-chartjs'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

// ============================================================
// STATE
// ============================================================
const loading = ref(false)
const stats = ref({
  totalBookings: 0,
  totalRevenue: 0,
  totalVisitors: 0,
  conversionRate: 0
})
const bookings = ref([])
const popularPackages = ref([])
const recentActivity = ref([])
const revenueChartRef = ref(null)
const statusChartRef = ref(null)
const revenueChart = ref(null)
const statusChart = ref(null)

// Date Range
const dateRange = ref({
  start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
  end: format(new Date(), 'yyyy-MM-dd')
})
const activeRange = ref('30days')
const quickRanges = [
  { label: '7 Days', value: '7days' },
  { label: '30 Days', value: '30days' },
  { label: '90 Days', value: '90days' },
  { label: 'This Month', value: 'thisMonth' },
  { label: 'Last Month', value: 'lastMonth' }
]

const dateRangeLabel = computed(() => {
  const start = new Date(dateRange.value.start)
  const end = new Date(dateRange.value.end)
  return `${format(start, 'MMM d')} - ${format(end, 'MMM d, yyyy')}`
})

// ============================================================
// METHODS
// ============================================================
const loadReports = async () => {
  loading.value = true
  try {
    const params = {
      start_date: dateRange.value.start,
      end_date: dateRange.value.end
    }
    
    const response = await axios.get('/api/admin/tour/reports/summary', { params })
    const data = response.data
    
    stats.value = {
      totalBookings: data.total_bookings || 0,
      totalRevenue: data.total_revenue || 0,
      totalVisitors: data.total_visitors || 0,
      conversionRate: data.conversion_rate || 0
    }
    
    bookings.value = data.bookings || []
    popularPackages.value = data.popular_packages || []
    recentActivity.value = data.recent_activity || []
    
    await nextTick()
    renderCharts()
  } catch (error) {
    alert('Failed to load reports. Please try again.')
  } finally {
    loading.value = false
  }
}

const loadFallbackData = () => {
  // Generate sample data for demo
  const today = new Date()
  const startDate = new Date(dateRange.value.start)
  const days = Math.ceil((today - startDate) / (1000 * 60 * 60 * 24))
  
  stats.value = {
    totalBookings: Math.floor(Math.random() * 100) + 50,
    totalRevenue: Math.floor(Math.random() * 500000) + 100000,
    totalVisitors: Math.floor(Math.random() * 300) + 100,
    conversionRate: Math.round(Math.random() * 30) + 10
  }
  
  // Generate popular packages
  const packageNames = ['Standard Tour', 'Premium Tour', 'School Tour', 'Corporate Tour', 'Family Package']
  popularPackages.value = packageNames.map((name, i) => ({
    id: i + 1,
    name: name,
    total_bookings: Math.floor(Math.random() * 20) + 5,
    percentage: Math.floor(Math.random() * 30) + 10
  })).sort((a, b) => b.total_bookings - a.total_bookings)
  
  // Generate recent activity
  const actions = ['New booking', 'Booking confirmed', 'Payment received', 'Tour completed', 'Booking cancelled']
  recentActivity.value = Array.from({ length: 5 }, (_, i) => ({
    id: i,
    type: ['booking', 'confirmed', 'payment', 'completed', 'cancelled'][i % 5],
    message: `${actions[i % 5]} - ${['Standard', 'Premium', 'School'][i % 3]} Tour`,
    created_at: new Date(Date.now() - i * 3600000).toISOString()
  }))
  
  nextTick(() => renderCharts())
}

const renderCharts = () => {
  renderRevenueChart()
  renderStatusChart()
}

const renderRevenueChart = () => {
  if (!revenueChartRef.value) return
  
  // Generate sample data
  const days = 30
  const labels = Array.from({ length: days }, (_, i) => {
    const date = subDays(new Date(), days - 1 - i)
    return format(date, 'MMM d')
  })
  
  const revenueData = Array.from({ length: days }, () => 
    Math.floor(Math.random() * 50000) + 5000
  )
  
  if (revenueChart.value) {
    revenueChart.value.destroy()
  }
  
  revenueChart.value = new ChartJS(revenueChartRef.value, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Revenue (KES)',
        data: revenueData,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `KES ${context.parsed.y.toLocaleString()}`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return 'KES ' + value.toLocaleString()
            }
          }
        }
      }
    }
  })
}

const renderStatusChart = () => {
  if (!statusChartRef.value) return
  
  const statusData = {
    labels: ['Pending', 'Confirmed', 'Completed', 'Cancelled'],
    datasets: [{
      data: [
        Math.floor(Math.random() * 20) + 5,
        Math.floor(Math.random() * 30) + 10,
        Math.floor(Math.random() * 25) + 5,
        Math.floor(Math.random() * 10) + 2
      ],
      backgroundColor: ['#f59e0b', '#10b981', '#3b82f6', '#ef4444'],
      borderWidth: 0
    }]
  }
  
  if (statusChart.value) {
    statusChart.value.destroy()
  }
  
  statusChart.value = new ChartJS(statusChartRef.value, {
    type: 'doughnut',
    data: statusData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 20,
            usePointStyle: true,
            pointStyle: 'circle'
          }
        }
      },
      cutout: '65%'
    }
  })
}

const setQuickRange = (range) => {
  activeRange.value = range
  const now = new Date()
  let start = new Date()
  
  switch(range) {
    case '7days':
      start = subDays(now, 7)
      break
    case '30days':
      start = subDays(now, 30)
      break
    case '90days':
      start = subDays(now, 90)
      break
    case 'thisMonth':
      start = startOfMonth(now)
      break
    case 'lastMonth':
      start = startOfMonth(subMonths(now, 1))
      break
    default:
      start = subDays(now, 30)
  }
  
  dateRange.value.start = format(start, 'yyyy-MM-dd')
  dateRange.value.end = format(now, 'yyyy-MM-dd')
  applyDateRange()
}

const applyDateRange = () => {
  loadReports()
}

const refreshData = () => {
  loadReports()
}

const getActivityIcon = (type) => {
  const icons = {
    booking: 'fas fa-plus-circle',
    confirmed: 'fas fa-check-circle',
    payment: 'fas fa-money-bill-wave',
    completed: 'fas fa-check-double',
    cancelled: 'fas fa-times-circle'
  }
  return icons[type] || 'fas fa-circle'
}

const formatPrice = (amount) => {
  return (amount || 0).toLocaleString('en-KE', { 
    minimumFractionDigits: 0, 
    maximumFractionDigits: 0 
  })
}

const formatTime = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000 / 60)
  
  if (diff < 1) return 'Just now'
  if (diff < 60) return `${diff} minutes ago`
  if (diff < 120) return '1 hour ago'
  if (diff < 1440) return `${Math.floor(diff / 60)} hours ago`
  return format(date, 'MMM d, h:mm a')
}

const exportReport = async (format) => {
  try {
    const response = await axios.get(`/api/admin/tour/reports/export`, {
      params: {
        format: format,
        start_date: dateRange.value.start,
        end_date: dateRange.value.end
      },
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `report_${dateRange.value.start}_to_${dateRange.value.end}.${format}`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    alert('Failed to export report. Please try again.')
  }
}

// ============================================================
// LIFECYCLE
// ============================================================
onMounted(() => {
  loadReports()
})

// Cleanup charts on unmount
import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (revenueChart.value) {
    revenueChart.value.destroy()
  }
  if (statusChart.value) {
    statusChart.value.destroy()
  }
})
</script>

<style scoped>
.tour-manager-reports {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ============================================
   PAGE HEADER
   ============================================ */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  color: #1e3a8a;
  margin: 0 0 4px;
  font-size: 1.8rem;
}

.page-header h1 i {
  color: #f59e0b;
  margin-right: 12px;
}

.subtitle {
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-export-pdf {
  padding: 10px 20px;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-export-pdf:hover {
  background: #b91c1c;
  transform: translateY(-2px);
}

.btn-export-csv {
  padding: 10px 20px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-export-csv:hover {
  background: #059669;
  transform: translateY(-2px);
}

.btn-refresh {
  padding: 10px 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  color: #4b5563;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-refresh:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #1e3a8a;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ============================================
   DATE RANGE
   ============================================ */
.date-range-section {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.date-range-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-range-group label {
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.date-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.quick-ranges {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.quick-range-btn {
  padding: 6px 12px;
  background: #f3f4f6;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  color: #4b5563;
  transition: all 0.3s;
}

.quick-range-btn:hover {
  background: #e5e7eb;
}

.quick-range-btn.active {
  background: #f59e0b;
  color: white;
}

.btn-apply {
  padding: 6px 16px;
  background: #1e3a8a;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-apply:hover {
  background: #1a2d6e;
}

/* ============================================
   STATS GRID
   ============================================ */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  flex-shrink: 0;
}

.stat-icon.blue { background: #3b82f6; }
.stat-icon.green { background: #10b981; }
.stat-icon.orange { background: #f59e0b; }
.stat-icon.purple { background: #8b5cf6; }

.stat-info h3 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
}

.stat-info p {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

/* ============================================
   CHARTS
   ============================================ */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.chart-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #1f2937;
}

.chart-header h3 i {
  color: #f59e0b;
  margin-right: 8px;
}

.chart-period {
  font-size: 12px;
  color: #6b7280;
}

.chart-body {
  padding: 20px;
  height: 250px;
  position: relative;
}

/* ============================================
   POPULAR PACKAGES
   ============================================ */
.popular-packages {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 20px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.card-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #1f2937;
}

.card-header h3 i {
  color: #f59e0b;
  margin-right: 8px;
}

.card-header .subtitle {
  font-size: 12px;
  color: #6b7280;
}

.packages-list {
  padding: 16px 20px;
}

.package-rank {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.package-rank:last-child {
  border-bottom: none;
}

.rank-number {
  width: 28px;
  height: 28px;
  background: #f3f4f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  color: #4b5563;
  flex-shrink: 0;
}

.package-rank-info {
  flex: 0 0 180px;
}

.package-name {
  font-weight: 500;
  color: #1f2937;
  font-size: 14px;
}

.package-bookings {
  font-size: 12px;
  color: #6b7280;
  margin-left: 8px;
}

.package-rank-bar {
  flex: 1;
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
}

.rank-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
  border-radius: 3px;
  transition: width 1s ease;
}

.package-percentage {
  font-weight: 600;
  color: #1e3a8a;
  font-size: 13px;
  min-width: 45px;
  text-align: right;
}

/* ============================================
   RECENT ACTIVITY
   ============================================ */
.recent-activity {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  overflow: hidden;
}

.activity-list {
  padding: 16px 20px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
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
  color: white;
  font-size: 12px;
  flex-shrink: 0;
}

.activity-icon.booking { background: #3b82f6; }
.activity-icon.confirmed { background: #10b981; }
.activity-icon.payment { background: #f59e0b; }
.activity-icon.completed { background: #8b5cf6; }
.activity-icon.cancelled { background: #ef4444; }

.activity-content {
  flex: 1;
}

.activity-text {
  display: block;
  font-size: 14px;
  color: #1f2937;
}

.activity-time {
  font-size: 12px;
  color: #6b7280;
}

/* ============================================
   LOADING & EMPTY STATES
   ============================================ */
.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 30px 20px;
  color: #6b7280;
}

.empty-state i {
  font-size: 32px;
  opacity: 0.3;
  display: block;
  margin-bottom: 8px;
}

.empty-state p {
  margin: 0;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .date-range-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .quick-ranges {
    justify-content: center;
  }
  
  .btn-apply {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .header-actions button {
    flex: 1;
    min-width: calc(50% - 6px);
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  
  .stat-card {
    padding: 12px 16px;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
  
  .stat-info h3 {
    font-size: 18px;
  }
  
  .date-inputs {
    flex-wrap: wrap;
  }
  
  .package-rank {
    flex-wrap: wrap;
  }
  
  .package-rank-info {
    flex: 1;
    min-width: 120px;
  }
  
  .package-rank-bar {
    flex-basis: 100%;
    order: 1;
  }
  
  .package-percentage {
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .header-actions button {
    min-width: 100%;
  }
  
  .date-range-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .date-inputs {
    flex-direction: column;
  }
  
  .quick-ranges {
    flex-wrap: wrap;
  }
  
  .quick-range-btn {
    flex: 1;
    min-width: calc(50% - 4px);
    text-align: center;
  }
}
</style>
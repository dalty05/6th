<template>
  <div class="partner-analytics">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>Analytics Dashboard</h1>
        <p>Track your referral performance and marketing ROI</p>
      </div>
      <div class="date-range-selector">
        <button 
          v-for="range in dateRanges" 
          :key="range.days"
          @click="setDateRange(range.days)"
          class="btn" 
          :class="{ 'btn-primary': selectedRange === range.days, 'btn-outline': selectedRange !== range.days }"
        >
          {{ range.label }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading analytics data...</p>
    </div>

    <div v-else>
      <!-- Summary Cards -->
      <div class="summary-cards">
        <div class="summary-card">
          <div class="summary-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="summary-info">
            <span class="summary-value">{{ formatNumber(summary.current?.clicks || 0) }}</span>
            <span class="summary-label">Total Clicks</span>
            <span class="summary-trend" :class="getTrendClass(summary.growth?.clicks)">
              <i :class="getTrendIcon(summary.growth?.clicks)"></i>
              {{ Math.abs(summary.growth?.clicks || 0) }}%
            </span>
          </div>
        </div>

        <div class="summary-card">
          <div class="summary-icon">
            <i class="fas fa-shopping-cart"></i>
          </div>
          <div class="summary-info">
            <span class="summary-value">{{ formatNumber(summary.current?.conversions || 0) }}</span>
            <span class="summary-label">Conversions</span>
            <span class="summary-trend" :class="getTrendClass(summary.growth?.conversions)">
              <i :class="getTrendIcon(summary.growth?.conversions)"></i>
              {{ Math.abs(summary.growth?.conversions || 0) }}%
            </span>
          </div>
        </div>

        <div class="summary-card">
          <div class="summary-icon">
            <i class="fas fa-chart-pie"></i>
          </div>
          <div class="summary-info">
            <span class="summary-value">{{ summary.current?.conversion_rate || 0 }}%</span>
            <span class="summary-label">Conversion Rate</span>
          </div>
        </div>

        <div class="summary-card">
          <div class="summary-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="summary-info">
            <span class="summary-value">{{ formatNumber(summary.current?.unique_visitors || 0) }}</span>
            <span class="summary-label">Unique Visitors</span>
          </div>
        </div>
      </div>

      <!-- Main Chart -->
      <div class="chart-card glass-card">
        <div class="chart-header">
          <h3>Performance Overview</h3>
          <div class="chart-legend">
            <span class="legend-item">
              <span class="legend-color clicks"></span>
              Clicks
            </span>
            <span class="legend-item">
              <span class="legend-color conversions"></span>
              Conversions
            </span>
          </div>
        </div>
        <AnalyticsChart 
          :data="chartData" 
          @rangeChange="updateDateRange"
        />
      </div>

      <!-- Two Column Layout for Additional Charts -->
      <div class="two-column">
        <!-- Source Breakdown -->
        <div class="source-card glass-card">
          <h3>Traffic Sources</h3>
          <div class="source-list">
            <div v-for="(count, source) in sourceStats" :key="source" class="source-item">
              <div class="source-name">
                <i :class="getSourceIcon(source)"></i>
                {{ formatSourceName(source) }}
              </div>
              <div class="source-bar">
                <div class="source-bar-fill" :style="{ width: getSourcePercentage(count) + '%' }"></div>
              </div>
              <div class="source-count">{{ formatNumber(count) }}</div>
            </div>
          </div>
        </div>

        <!-- Hourly Timeline -->
        <div class="timeline-card glass-card">
          <h3>Today's Activity</h3>
          <div class="timeline-chart">
            <div v-for="item in timelineData" :key="item.hour" class="timeline-bar-container">
              <div class="timeline-bar" :style="{ height: getTimelineHeight(item.clicks) + '%' }">
                <span class="timeline-value">{{ item.clicks }}</span>
              </div>
              <div class="timeline-label">{{ item.hour }}:00</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Performing Links -->
      <div class="top-links-card glass-card">
        <div class="card-header">
          <h3>Top Performing Links</h3>
          <select v-model="topLinksSort" @change="loadTopLinks" class="sort-select">
            <option value="clicks">Sort by Clicks</option>
            <option value="conversions">Sort by Conversions</option>
            <option value="rate">Sort by Conversion Rate</option>
          </select>
        </div>
        <div class="top-links-list">
          <div v-for="(link, index) in topLinks" :key="link.id" class="top-link-item">
            <div class="rank">{{ index + 1 }}</div>
            <div class="link-details">
              <strong>{{ link.name }}</strong>
              <code>{{ baseUrl }}/r/{{ link.link_code }}</code>
            </div>
            <div class="link-performance">
              <span class="clicks">{{ formatNumber(link.total_clicks) }} clicks</span>
              <span class="rate">{{ link.conversion_rate }}% conv.</span>
            </div>
          </div>
          <div v-if="topLinks.length === 0" class="no-data">
            No data available yet
          </div>
        </div>
      </div>

      <!-- Recent Clicks Table -->
      <div class="recent-clicks-card glass-card">
        <h3>Recent Clicks</h3>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Link</th>
                <th>Source</th>
                <th>Device</th>
                <th>Converted</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="click in recentClicks" :key="click.id">
                <td>{{ formatDateTime(click.clicked_at) }}</td>
                <td>{{ click.link_name }}</td>
                <td>{{ click.referrer_url || 'Direct' }}</td>
                <td>{{ click.device || 'Desktop' }}</td>
                <td>
                  <span class="badge" :class="click.converted ? 'badge-success' : 'badge-secondary'">
                    {{ click.converted ? 'Yes' : 'No' }}
                  </span>
                </td>
              </tr>
              <tr v-if="recentClicks.length === 0">
                <td colspan="5" class="empty-row">No click data available</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import referralService from '@/services/referral'
import AnalyticsChart from '@/components/partner/AnalyticsChart.vue'

const loading = ref(false)
const selectedRange = ref(30)
const baseUrl = window.location.origin
const topLinksSort = ref('clicks')

const dateRanges = [
  { days: 7, label: '7 Days' },
  { days: 14, label: '14 Days' },
  { days: 30, label: '30 Days' },
  { days: 90, label: '90 Days' }
]

const summary = ref({})
const chartData = ref({ labels: [], clicks: [], conversions: [] })
const sourceStats = ref({})
const timelineData = ref([])
const topLinks = ref([])
const recentClicks = ref([])

const loadAllAnalytics = async () => {
  loading.value = true
  try {
    const [summaryRes, chartRes, sourcesRes, timelineRes, topLinksRes, clicksRes] = await Promise.all([
      referralService.getAnalyticsSummary(selectedRange.value),
      referralService.getAnalytics(selectedRange.value),
      referralService.getSourceAnalytics(),
      referralService.getTimelineAnalytics(),
      referralService.getTopLinks(5, topLinksSort.value),
      referralService.getRecentClicksAnalytics(20)
    ])
    
    summary.value = summaryRes
    chartData.value = chartRes.chartData || { labels: [], clicks: [], conversions: [] }
    sourceStats.value = sourcesRes
    timelineData.value = timelineRes
    topLinks.value = topLinksRes
    recentClicks.value = clicksRes
  } catch (error) {
    console.error('Error loading analytics:', error)
  } finally {
    loading.value = false
  }
}

const loadTopLinks = async () => {
  try {
    topLinks.value = await referralService.getTopLinks(5, topLinksSort.value)
  } catch (error) {
    console.error('Error loading top links:', error)
  }
}

const setDateRange = (days) => {
  selectedRange.value = days
  loadAllAnalytics()
}

const updateDateRange = (days) => {
  setDateRange(days)
}

const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

const getTrendClass = (trend) => {
  if (!trend) return ''
  return trend > 0 ? 'trend-up' : 'trend-down'
}

const getTrendIcon = (trend) => {
  if (!trend) return 'fas fa-minus'
  return trend > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'
}

const getSourceIcon = (source) => {
  const icons = {
    direct: 'fas fa-globe',
    facebook: 'fab fa-facebook',
    twitter: 'fab fa-twitter',
    instagram: 'fab fa-instagram',
    linkedin: 'fab fa-linkedin',
    whatsapp: 'fab fa-whatsapp',
    email: 'fas fa-envelope',
    other: 'fas fa-external-link-alt'
  }
  return icons[source] || 'fas fa-link'
}

const formatSourceName = (source) => {
  const names = {
    direct: 'Direct',
    facebook: 'Facebook',
    twitter: 'Twitter',
    instagram: 'Instagram',
    linkedin: 'LinkedIn',
    whatsapp: 'WhatsApp',
    email: 'Email',
    other: 'Other'
  }
  return names[source] || source
}

const getSourcePercentage = (count) => {
  const total = Object.values(sourceStats.value).reduce((a, b) => a + b, 0)
  return total > 0 ? (count / total) * 100 : 0
}

const getTimelineHeight = (clicks) => {
  const max = Math.max(...timelineData.value.map(d => d.clicks), 1)
  return (clicks / max) * 100
}

onMounted(() => {
  loadAllAnalytics()
})
</script>

<style scoped>
.partner-analytics {
  min-height: 100vh;
  background: #f8fafc;
  padding: 2rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-header h1 {
  color: #1e3a8a;
  margin: 0 0 0.25rem;
}

.page-header p {
  color: #666;
  margin: 0;
}

.date-range-selector {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.btn-primary {
  background: #f59e0b;
  color: white;
}

.btn-outline {
  background: white;
  border: 1px solid #e5e7eb;
  color: #333;
}

.btn-outline:hover {
  border-color: #f59e0b;
  color: #f59e0b;
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.summary-icon {
  width: 56px;
  height: 56px;
  background: #e0e7ff;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.summary-icon i {
  font-size: 1.8rem;
  color: #f59e0b;
}

.summary-info {
  flex: 1;
}

.summary-value {
  display: block;
  font-size: 1.8rem;
  font-weight: 700;
  color: #1e3a8a;
}

.summary-label {
  font-size: 0.8rem;
  color: #666;
}

.summary-trend {
  font-size: 0.7rem;
  margin-left: 0.5rem;
}

.trend-up {
  color: #10b981;
}

.trend-down {
  color: #ef4444;
}

/* Charts */
.chart-card, .source-card, .timeline-card, .top-links-card, .recent-clicks-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.chart-header h3 {
  color: #1e3a8a;
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #666;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-color.clicks {
  background: #f59e0b;
}

.legend-color.conversions {
  background: #10b981;
}

/* Two Column Layout */
.two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

/* Source List */
.source-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.source-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.source-name {
  width: 100px;
  font-size: 0.85rem;
  color: #666;
}

.source-name i {
  width: 20px;
  margin-right: 0.5rem;
  color: #f59e0b;
}

.source-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.source-bar-fill {
  height: 100%;
  background: #f59e0b;
  border-radius: 4px;
  transition: width 0.3s;
}

.source-count {
  width: 60px;
  text-align: right;
  font-size: 0.85rem;
  font-weight: 500;
  color: #1e3a8a;
}

/* Timeline Chart */
.timeline-chart {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 150px;
  padding: 0.5rem 0;
}

.timeline-bar-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.timeline-bar {
  width: 100%;
  background: #f59e0b;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s;
  position: relative;
  min-height: 2px;
}

.timeline-value {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.7rem;
  color: #666;
  white-space: nowrap;
}

.timeline-label {
  font-size: 0.65rem;
  color: #999;
  transform: rotate(-45deg);
  white-space: nowrap;
}

/* Top Links */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.card-header h3 {
  color: #1e3a8a;
  margin: 0;
}

.sort-select {
  padding: 0.4rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  cursor: pointer;
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

/* Table */
.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #1e3a8a;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 500;
}

.badge-success {
  background: #d1fae5;
  color: #065f46;
}

.badge-secondary {
  background: #f3f4f6;
  color: #374151;
}

.empty-row {
  text-align: center;
  padding: 2rem;
  color: #999;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 4rem;
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

.no-data {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
}

@media (max-width: 768px) {
  .partner-analytics {
    padding: 1rem;
  }
  
  .two-column {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr 1fr;
  }
  
  .page-header {
    flex-direction: column;
  }
  
  .timeline-label {
    transform: rotate(-60deg);
    font-size: 0.55rem;
  }
  
  .source-name {
    width: 80px;
    font-size: 0.75rem;
  }
}
</style>
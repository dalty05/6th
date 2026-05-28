<template>
  <div class="referral-analytics">
    <div class="header">
      <h2>Referral Analytics</h2>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card">
        <i class="fas fa-mouse-pointer"></i>
        <div class="stat-info">
          <h3>{{ stats.totalClicks }}</h3>
          <p>Total Clicks</p>
        </div>
      </div>
      <div class="stat-card">
        <i class="fas fa-users"></i>
        <div class="stat-info">
          <h3>{{ stats.uniqueClicks }}</h3>
          <p>Unique Visitors</p>
        </div>
      </div>
      <div class="stat-card">
        <i class="fas fa-shopping-cart"></i>
        <div class="stat-info">
          <h3>{{ stats.totalConversions }}</h3>
          <p>Conversions</p>
        </div>
      </div>
      <div class="stat-card">
        <i class="fas fa-chart-line"></i>
        <div class="stat-info">
          <h3>{{ stats.conversionRate }}%</h3>
          <p>Conversion Rate</p>
        </div>
      </div>
    </div>
    
    <div class="top-performers">
      <h3>Top Performing Partners</h3>
      <DataTable 
        :data="topPartners" 
        :columns="partnerColumns" 
        :loading="loading"
      />
    </div>
    
    <div class="coming-soon-notice">
      <i class="fas fa-info-circle"></i>
      <p>Advanced analytics with charts, date range filters, and export capabilities coming soon!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DataTable from './DataTable.vue'
import axios from 'axios'

const stats = ref({
  totalClicks: 0,
  uniqueClicks: 0,
  totalConversions: 0,
  conversionRate: 0
})
const topPartners = ref([])
const loading = ref(false)

const partnerColumns = [
  { key: 'full_name', label: 'Partner', sortable: true },
  { key: 'total_clicks', label: 'Clicks', sortable: true },
  { key: 'total_conversions', label: 'Conversions', sortable: true },
  { key: 'conversion_rate', label: 'Rate', sortable: true }
]

const fetchStats = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/referral/analytics')
    stats.value = response.data.stats || stats.value
    topPartners.value = response.data.topPartners || []
  } catch (error) {
    console.error('Error fetching referral stats:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.referral-analytics {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header h2 {
  color: #1e3a8a;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-card i {
  font-size: 2rem;
  color: #f59e0b;
}

.stat-info h3 {
  font-size: 1.5rem;
  margin: 0;
  color: #1e3a8a;
}

.stat-info p {
  margin: 0;
  color: #666;
  font-size: 0.85rem;
}

.top-performers h3 {
  color: #1e3a8a;
  margin-bottom: 1rem;
}

.coming-soon-notice {
  margin-top: 2rem;
  padding: 1rem;
  background: #fef3c7;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #92400e;
}
</style>
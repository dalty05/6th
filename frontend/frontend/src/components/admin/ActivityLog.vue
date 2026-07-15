<template>
  <div class="activity-log">
    <div class="activity-header">
      <h3><i class="fas fa-history"></i> Recent Activity</h3>
      <div class="activity-filters">
        <select v-model="filters.type" @change="loadActivities" class="filter-select">
          <option value="">All Activities</option>
          <option value="product">Products</option>
          <option value="blog">Blog Posts</option>
          <option value="user">Users</option>
          <option value="partner">Partners</option>
          <option value="referral">Referrals</option>
        </select>
        <select v-model="filters.days" @change="loadActivities" class="filter-select">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="all">All time</option>
        </select>
      </div>
    </div>
    
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading activity...</p>
    </div>
    
    <div v-else-if="activities.length === 0" class="empty-state">
      <i class="fas fa-inbox"></i>
      <p>No activity found</p>
    </div>
    
    <div v-else class="timeline">
      <div v-for="activity in activities" :key="activity.id" class="timeline-item">
        <div class="timeline-icon" :class="activity.action">
          <i :class="getActionIcon(activity.action)"></i>
        </div>
        <div class="timeline-content">
          <div class="activity-title">
            <strong>{{ activity.user_name }}</strong>
            <span>{{ activity.description }}</span>
          </div>
          <div class="activity-meta">
            <span class="activity-time">
              <i class="far fa-clock"></i> {{ formatTime(activity.created_at) }}
            </span>
            <span class="activity-ip">
              <i class="fas fa-network-wired"></i> {{ activity.ip_address }}
            </span>
            <span v-if="activity.details" class="activity-details" @click="showDetails(activity)">
              <i class="fas fa-info-circle"></i> Details
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Activity Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click.self="closeDetailsModal">
      <div class="modal-container glass-card modal-small">
        <div class="modal-header">
          <h2>Activity Details</h2>
          <button @click="closeDetailsModal" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <pre>{{ JSON.stringify(selectedActivity?.details, null, 2) }}</pre>
        </div>
        <div class="modal-actions">
          <button @click="closeDetailsModal" class="btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const activities = ref([])
const loading = ref(false)
const showDetailsModal = ref(false)
const selectedActivity = ref(null)

const filters = ref({
  type: '',
  days: '30'
})

const getActionIcon = (action) => {
  const icons = {
    create: 'fas fa-plus-circle',
    update: 'fas fa-edit',
    delete: 'fas fa-trash-alt',
    login: 'fas fa-sign-in-alt',
    logout: 'fas fa-sign-out-alt',
    approve: 'fas fa-check-circle',
    suspend: 'fas fa-ban',
    regenerate: 'fas fa-sync-alt'
  }
  return icons[action] || 'fas fa-circle'
}

const loadActivities = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/activities', {
      params: {
        type: filters.value.type || undefined,
        days: filters.value.days !== 'all' ? filters.value.days : undefined
      }
    })
    activities.value = response.data
  } finally {
    loading.value = false
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} minutes ago`
  if (hours < 24) return `${hours} hours ago`
  if (days < 7) return `${days} days ago`
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

const showDetails = (activity) => {
  selectedActivity.value = activity
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedActivity.value = null
}

onMounted(() => {
  loadActivities()
})
</script>

<style scoped>
.activity-log {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.activity-header h3 {
  color: #1e3a8a;
  margin: 0;
}

.activity-filters {
  display: flex;
  gap: 0.5rem;
}

.filter-select {
  padding: 0.4rem 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  cursor: pointer;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 3rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #f59e0b;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state i {
  font-size: 3rem;
  color: #cbd5e1;
  margin-bottom: 1rem;
}

.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 7px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e5e7eb;
}

.timeline-item {
  position: relative;
  margin-bottom: 1.5rem;
  display: flex;
  gap: 1rem;
}

.timeline-icon {
  position: absolute;
  left: -2rem;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

.timeline-icon.create {
  background: #d1fae5;
  color: #10b981;
}

.timeline-icon.update {
  background: #dbeafe;
  color: #3b82f6;
}

.timeline-icon.delete {
  background: #fee2e2;
  color: #dc2626;
}

.timeline-icon.login {
  background: #e0e7ff;
  color: #8b5cf6;
}

.timeline-content {
  flex: 1;
  background: #f8fafc;
  padding: 1rem;
  border-radius: 12px;
}

.activity-title {
  margin-bottom: 0.5rem;
}

.activity-title strong {
  color: #1e3a8a;
  margin-right: 0.5rem;
}

.activity-title span {
  color: #666;
  font-size: 0.9rem;
}

.activity-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.7rem;
  color: #999;
}

.activity-meta i {
  margin-right: 0.25rem;
}

.activity-details {
  cursor: pointer;
  color: #f59e0b;
}

.activity-details:hover {
  text-decoration: underline;
}

/* Modal Styles */
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
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-small {
  max-width: 500px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  color: #1e3a8a;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 1.5rem;
}

.modal-body pre {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.8rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn-secondary {
  background: #e5e7eb;
  color: #333;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.glass-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
}

@media (max-width: 768px) {
  .activity-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .activity-meta {
    flex-wrap: wrap;
  }
  
  .timeline {
    padding-left: 1.5rem;
  }
}
</style>
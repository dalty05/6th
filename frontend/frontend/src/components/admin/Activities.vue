<!-- frontend/src/components/admin/Activities.vue -->
<template>
  <div class="activities-container">
    <div class="activities-header">
      <h2><i class="fas fa-history"></i> Activity Log</h2>
      <p class="subtitle">View system activity history</p>
    </div>

    <!-- Filters -->
    <div class="activities-filters">
      <div class="filter-group">
        <label>Limit:</label>
        <select v-model="limit" @change="loadActivities">
          <option value="10">10</option>
          <option value="25">25</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Action:</label>
        <select v-model="filterAction" @change="loadActivities">
          <option value="">All Actions</option>
          <option value="login">Login</option>
          <option value="logout">Logout</option>
          <option value="create">Create</option>
          <option value="update">Update</option>
          <option value="delete">Delete</option>
          <option value="approve">Approve</option>
          <option value="reject">Reject</option>
        </select>
      </div>
      <button @click="loadActivities" class="btn-refresh">
        <i class="fas fa-sync-alt" :class="{ spinning: loading }"></i>
        Refresh
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading activities...</p>
    </div>

    <!-- Activities List -->
    <div v-else-if="activities.length > 0" class="activities-list">
      <div 
        v-for="activity in filteredActivities" 
        :key="activity.id" 
        class="activity-item"
        :class="activity.action"
      >
        <div class="activity-icon">
          <i :class="getActivityIcon(activity.action)"></i>
        </div>
        <div class="activity-content">
          <div class="activity-main">
            <span class="activity-user">{{ activity.user_name || 'System' }}</span>
            <span class="activity-action">{{ activity.action }}</span>
            <span class="activity-resource">{{ activity.resource_type }}</span>
          </div>
          <p class="activity-description" v-if="activity.description">
            {{ activity.description }}
          </p>
          <div class="activity-meta">
            <span class="activity-time">
              <i class="fas fa-clock"></i> {{ formatDate(activity.created_at) }}
            </span>
            <span class="activity-ip" v-if="activity.ip_address">
              <i class="fas fa-network-wired"></i> {{ activity.ip_address }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <i class="fas fa-inbox"></i>
      <h3>No Activities Found</h3>
      <p>There are no activities to display</p>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  name: 'Activities',
  
  data() {
    return {
      activities: [],
      loading: false,
      limit: 10,
      filterAction: '',
    }
  },

  computed: {
    filteredActivities() {
      if (!this.filterAction) return this.activities
      return this.activities.filter(a => a.action === this.filterAction)
    }
  },

  mounted() {
    this.loadActivities()
  },

  methods: {
    async loadActivities() {
      this.loading = true
      try {
        const response = await api.get(`/admin/activities?limit=${this.limit}`)
        this.activities = response.data.activities || []
      } catch (error) {
        if (error.response?.status === 403) {
          alert('You do not have permission to view activities')
        } else {
          alert('Failed to load activities. Please try again.')
        }
      } finally {
        this.loading = false
      }
    },

    getActivityIcon(action) {
      const icons = {
        'login': 'fas fa-sign-in-alt',
        'logout': 'fas fa-sign-out-alt',
        'create': 'fas fa-plus-circle',
        'update': 'fas fa-edit',
        'delete': 'fas fa-trash-alt',
        'approve': 'fas fa-check-circle',
        'reject': 'fas fa-times-circle',
        'view': 'fas fa-eye',
        'upload': 'fas fa-upload',
        'download': 'fas fa-download',
        'export': 'fas fa-file-export',
        'import': 'fas fa-file-import',
      }
      return icons[action] || 'fas fa-circle'
    },

    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      const date = new Date(dateStr)
      return date.toLocaleString('en-KE', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.activities-container {
  padding: 24px;
}

.activities-header {
  margin-bottom: 24px;
}

.activities-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 4px 0;
}

.activities-header h2 i {
  color: #2563eb;
  margin-right: 12px;
}

.activities-header .subtitle {
  color: #64748b;
  margin: 0;
  font-size: 14px;
}

.activities-filters {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 500;
  color: #1a1a2e;
  font-size: 14px;
}

.filter-group select {
  padding: 6px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: #f8fafc;
  transition: all 0.2s;
}

.filter-group select:focus {
  outline: none;
  border-color: #2563eb;
}

.btn-refresh {
  padding: 8px 16px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  transition: all 0.2s;
  margin-left: auto;
}

.btn-refresh:hover {
  background: #1d4ed8;
}

.btn-refresh .spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

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

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  gap: 16px;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  border-left: 4px solid #e2e8f0;
  transition: all 0.2s;
}

.activity-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.activity-item.login {
  border-left-color: #2563eb;
}

.activity-item.logout {
  border-left-color: #94a3b8;
}

.activity-item.create {
  border-left-color: #16a34a;
}

.activity-item.update {
  border-left-color: #f59e0b;
}

.activity-item.delete {
  border-left-color: #dc2626;
}

.activity-item.approve {
  border-left-color: #22c55e;
}

.activity-item.reject {
  border-left-color: #ef4444;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 16px;
}

.activity-item.login .activity-icon {
  background: #dbeafe;
  color: #1e40af;
}

.activity-item.logout .activity-icon {
  background: #f1f5f9;
  color: #64748b;
}

.activity-item.create .activity-icon {
  background: #dcfce7;
  color: #16a34a;
}

.activity-item.update .activity-icon {
  background: #fef3c7;
  color: #92400e;
}

.activity-item.delete .activity-icon {
  background: #fee2e2;
  color: #dc2626;
}

.activity-item.approve .activity-icon {
  background: #dcfce7;
  color: #16a34a;
}

.activity-item.reject .activity-icon {
  background: #fee2e2;
  color: #dc2626;
}

.activity-content {
  flex: 1;
}

.activity-main {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

.activity-user {
  font-weight: 600;
  color: #1a1a2e;
}

.activity-action {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

.activity-item.login .activity-action {
  background: #dbeafe;
  color: #1e40af;
}

.activity-item.logout .activity-action {
  background: #f1f5f9;
  color: #64748b;
}

.activity-item.create .activity-action {
  background: #dcfce7;
  color: #16a34a;
}

.activity-item.update .activity-action {
  background: #fef3c7;
  color: #92400e;
}

.activity-item.delete .activity-action {
  background: #fee2e2;
  color: #dc2626;
}

.activity-item.approve .activity-action {
  background: #dcfce7;
  color: #16a34a;
}

.activity-item.reject .activity-action {
  background: #fee2e2;
  color: #dc2626;
}

.activity-resource {
  font-size: 13px;
  color: #64748b;
  font-family: monospace;
  background: #f1f5f9;
  padding: 1px 8px;
  border-radius: 4px;
}

.activity-description {
  margin: 4px 0 8px 0;
  color: #1a1a2e;
  font-size: 14px;
}

.activity-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #94a3b8;
}

.activity-meta i {
  margin-right: 4px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.empty-state p {
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .activities-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn-refresh {
    margin-left: 0;
    justify-content: center;
  }
  
  .activity-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .activity-meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
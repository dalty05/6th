<template>
  <div class="newsletter-management">
    <!-- Header -->
    <div class="management-header">
      <div class="header-left">
        <h1>Newsletter Management</h1>
        <p>Manage subscribers and send email campaigns</p>
      </div>
      <div class="header-actions">
        <button @click="exportSubscribers" class="btn btn-outline">
          <i class="fas fa-download"></i> Export CSV
        </button>
        <button @click="openSendModal" class="btn btn-primary">
          <i class="fas fa-paper-plane"></i> Send Newsletter
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <h3>{{ stats.total || 0 }}</h3>
          <p>Total Subscribers</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green"><i class="fas fa-user-check"></i></div>
        <div class="stat-info">
          <h3>{{ stats.active || 0 }}</h3>
          <p>Active Subscribers</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange"><i class="fas fa-user-clock"></i></div>
        <div class="stat-info">
          <h3>{{ stats.inactive || 0 }}</h3>
          <p>Inactive</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple"><i class="fas fa-calendar-week"></i></div>
        <div class="stat-info">
          <h3>{{ stats.new_last_30_days || 0 }}</h3>
          <p>New (30 days)</p>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search by name or email..."
          @input="loadSubscribers"
        >
      </div>
      <select v-model="statusFilter" @change="loadSubscribers" class="filter-select">
        <option value="all">All Subscribers</option>
        <option value="active">Active Only</option>
        <option value="inactive">Inactive Only</option>
      </select>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading subscribers...</p>
    </div>

    <!-- Subscribers Table -->
    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
            <th>Subscribed Date</th>
            <th>Last Sent</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="subscriber in subscribers" :key="subscriber.id">
            <td>{{ subscriber.name || '-' }}</td>
            <td>{{ subscriber.email }}</td>
            <td>
              <span :class="['status-badge', subscriber.is_active ? 'active' : 'inactive']">
                {{ subscriber.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ formatDate(subscriber.subscribed_at) }}</td>
            <td>{{ formatDate(subscriber.last_sent) || 'Never' }}</td>
            <td class="actions-cell">
              <button 
                v-if="subscriber.is_active" 
                @click="toggleStatus(subscriber.id)" 
                class="action-btn suspend" 
                title="Deactivate"
              >
                <i class="fas fa-ban"></i>
              </button>
              <button 
                v-if="!subscriber.is_active" 
                @click="toggleStatus(subscriber.id)" 
                class="action-btn activate" 
                title="Activate"
              >
                <i class="fas fa-play-circle"></i>
              </button>
              <button 
                v-if="isSuperAdmin" 
                @click="deleteSubscriber(subscriber.id)" 
                class="action-btn delete" 
                title="Delete"
              >
                <i class="fas fa-trash-alt"></i>
              </button>
            </td>
          </tr>
          <tr v-if="subscribers.length === 0">
            <td colspan="6" class="empty-row">No subscribers found</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="pagination.total_pages > 1">
      <button @click="prevPage" :disabled="pagination.current_page === 1" class="page-btn">
        Previous
      </button>
      <span class="page-info">Page {{ pagination.current_page }} of {{ pagination.total_pages }}</span>
      <button @click="nextPage" :disabled="!pagination.has_next" class="page-btn">
        Next
      </button>
    </div>

    <!-- Send Newsletter Modal -->
    <div class="modal-overlay" v-if="showSendModal" @click.self="closeSendModal">
      <div class="modal-container large">
        <div class="modal-header">
          <h2>Send Newsletter</h2>
          <button class="close-btn" @click="closeSendModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="stats-info">
            <div class="info-box">
              <i class="fas fa-users"></i>
              <span>{{ stats.active }} active subscribers will receive this email</span>
            </div>
          </div>
          
          <form @submit.prevent="sendNewsletter">
            <div class="form-group">
              <label>Subject *</label>
              <input type="text" v-model="newsletterForm.subject" required placeholder="Enter email subject">
            </div>
            
            <div class="form-group">
              <label>Content *</label>
              <textarea v-model="newsletterForm.content" rows="8" required placeholder="Write your newsletter content here..."></textarea>
            </div>
            
            <div class="form-group checkbox">
              <label>
                <input type="checkbox" v-model="newsletterForm.is_test">
                Send test email first
              </label>
            </div>
            
            <div class="form-group" v-if="newsletterForm.is_test">
              <label>Test Email Address</label>
              <input type="email" v-model="newsletterForm.test_email" placeholder="Enter email for testing">
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeSendModal" class="btn-cancel">Cancel</button>
              <button type="submit" class="btn-send" :disabled="sending">
                <i v-if="sending" class="fas fa-spinner fa-spin"></i>
                {{ newsletterForm.is_test ? 'Send Test' : (sending ? 'Sending...' : 'Send Newsletter') }}
              </button>
            </div>
          </form>
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
import api from '@/services/api'
import authService from '@/services/auth'

// State
const subscribers = ref([])
const loading = ref(false)
const sending = ref(false)
const showSendModal = ref(false)
const searchQuery = ref('')
const statusFilter = ref('all')

const stats = ref({
  total: 0,
  active: 0,
  inactive: 0,
  new_last_30_days: 0
})

const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_items: 0,
  has_next: false,
  has_prev: false
})

const newsletterForm = ref({
  subject: '',
  content: '',
  is_test: false,
  test_email: ''
})

const notification = ref({
  show: false,
  message: '',
  type: 'success',
  icon: 'fas fa-check-circle'
})

// Current user
const currentUser = authService.getUser()
const isSuperAdmin = computed(() => currentUser?.role === 'super_admin')

// Methods
const showNotification = (message, type = 'success') => {
  notification.value = { show: true, message, type, icon: type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle' }
  setTimeout(() => notification.value.show = false, 3000)
}

const loadStats = async () => {
  try {
    const response = await api.get('/admin/newsletter/subscribers/stats')
    stats.value = response.data || { total: 0, active: 0, inactive: 0, new_last_30_days: 0 }
  } catch (error) {
    
    
    stats.value = { total: 0, active: 0, inactive: 0, new_last_30_days: 0 }
  }
}

const loadSubscribers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/newsletter/subscribers', {
      params: {
        page: pagination.value.current_page,
        per_page: 20,
        search: searchQuery.value || '',
        status: statusFilter.value || 'all'
      }
    })
    subscribers.value = response.data.data || []
    pagination.value = response.data.pagination || {
      current_page: 1,
      total_pages: 1,
      total_items: 0,
      has_next: false,
      has_prev: false
    }
  } catch (error) {
    subscribers.value = []
    showNotification('Failed to load subscribers', 'error')
  } finally {
    loading.value = false
  }
}

const toggleStatus = async (id) => {
  try {
    await api.put(`/admin/newsletter/subscribers/${id}/toggle`)
    showNotification('Status updated')
    await loadSubscribers()
    await loadStats()
  } catch (error) {
    showNotification('Failed to update status', 'error')
  }
}

const deleteSubscriber = async (id) => {
  if (confirm('Delete this subscriber permanently?')) {
    try {
      await api.delete(`/admin/newsletter/subscribers/${id}`)
      showNotification('Subscriber deleted')
      await loadSubscribers()
      await loadStats()
    } catch (error) {
      showNotification('Failed to delete', 'error')
    }
  }
}

const exportSubscribers = async () => {
  try {
    const response = await api.get('/admin/newsletter/export')
    const csvData = response.data.csv_content || ''
    const blob = new Blob([csvData], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = response.data.filename || 'subscribers.csv'
    a.click()
    URL.revokeObjectURL(url)
    showNotification('Export complete')
  } catch (error) {
    showNotification('Export failed', 'error')
  }
}

const openSendModal = () => {
  newsletterForm.value = {
    subject: '',
    content: '',
    is_test: false,
    test_email: currentUser?.email || ''
  }
  showSendModal.value = true
}

const closeSendModal = () => {
  showSendModal.value = false
}

const sendNewsletter = async () => {
  if (!newsletterForm.value.subject || !newsletterForm.value.content) {
    showNotification('Subject and content are required', 'error')
    return
  }
  
  if (newsletterForm.value.is_test && !newsletterForm.value.test_email) {
    showNotification('Test email address is required', 'error')
    return
  }
  
  sending.value = true
  try {
    await api.post('/admin/newsletter/send', newsletterForm.value)
    showNotification(newsletterForm.value.is_test ? 'Test email sent' : 'Newsletter sent successfully')
    closeSendModal()
    await loadStats()
  } catch (error) {
    showNotification(error.response?.data?.error || 'Failed to send', 'error')
  } finally {
    sending.value = false
  }
}

const prevPage = () => {
  if (pagination.value.current_page > 1) {
    pagination.value.current_page--
    loadSubscribers()
  }
}

const nextPage = () => {
  if (pagination.value.has_next) {
    pagination.value.current_page++
    loadSubscribers()
  }
}

const formatDate = (dateString) => {
  if (!dateString) return null
  try {
    return new Date(dateString).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    })
  } catch {
    return null
  }
}

// Lifecycle
onMounted(() => {
  loadStats()
  loadSubscribers()
})
</script>

<style scoped>
.newsletter-management {
  padding: 1rem;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h1 {
  color: #1e3a8a;
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
}

.header-left p {
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid #e5e7eb;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.blue { background: #e0e7ff; color: #1e3a8a; }
.stat-icon.green { background: #d1fae5; color: #065f46; }
.stat-icon.orange { background: #fed7aa; color: #9a3412; }
.stat-icon.purple { background: #e0e7ff; color: #1e3a8a; }

.stat-icon i { font-size: 1.25rem; }

.stat-info h3 { font-size: 1.5rem; margin: 0; color: #1e3a8a; }
.stat-info p { margin: 0; font-size: 0.75rem; color: #6b7280; }

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  position: relative;
  min-width: 250px;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.search-box input {
  width: 100%;
  padding: 0.6rem 0.75rem 0.6rem 2.25rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.filter-select {
  padding: 0.6rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
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

.table-container {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.data-table th, .data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #1e3a8a;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
}

.status-badge.active { background: #d1fae5; color: #065f46; }
.status-badge.inactive { background: #fee2e2; color: #991b1b; }

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.action-btn.suspend { color: #f59e0b; }
.action-btn.activate { color: #10b981; }
.action-btn.delete { color: #ef4444; }

.action-btn:hover {
  background: #f1f5f9;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.page-btn {
  background: white;
  border: 1px solid #e5e7eb;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
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
  transition: all 0.2s;
}

.btn-outline {
  background: white;
  border: 1px solid #e5e7eb;
}

.btn-outline:hover {
  border-color: #f59e0b;
  color: #f59e0b;
}

.btn-primary {
  background: #1e3a8a;
  color: white;
}

.btn-primary:hover {
  background: #f59e0b;
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
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
}

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

.stats-info { margin-bottom: 1rem; }

.info-box {
  background: #e0e7ff;
  padding: 0.75rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #1e3a8a;
  font-size: 0.85rem;
}

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.25rem; font-weight: 500; font-size: 0.8rem; }
.form-group input, .form-group textarea { width: 100%; padding: 0.6rem; border: 1px solid #e5e7eb; border-radius: 8px; }

.checkbox { display: flex; align-items: center; }
.checkbox label { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; }

.form-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem; }
.btn-cancel { background: #e5e7eb; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }
.btn-send { background: #1e3a8a; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }

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

.empty-row { text-align: center; padding: 2rem; color: #9ca3af; }

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filters-bar { flex-direction: column; }
  .management-header { flex-direction: column; align-items: flex-start; }
  .data-table { font-size: 0.75rem; }
  .data-table th, .data-table td { padding: 0.5rem; }
}
</style>
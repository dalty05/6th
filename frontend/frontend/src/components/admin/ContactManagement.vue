<template>
  <div class="contact-management">
    <div class="header">
      <h2>Contact Messages</h2>
      <div class="stats-badges">
        <span class="stat-badge unread">
          <i class="fas fa-envelope"></i> {{ stats.unread || 0 }} Unread
        </span>
        <span class="stat-badge total">
          <i class="fas fa-inbox"></i> {{ stats.total || 0 }} Total
        </span>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input type="text" v-model="filters.search" placeholder="Search messages..." @input="debouncedSearch">
      </div>
      <select v-model="filters.status" @change="loadMessages" class="filter-select">
        <option value="">All Status</option>
        <option value="unread">Unread</option>
        <option value="read">Read</option>
        <option value="replied">Replied</option>
        <option value="archived">Archived</option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading messages...</p>
    </div>

    <!-- Messages Table -->
    <div v-else-if="messages.length === 0" class="empty-state">
      <i class="fas fa-inbox"></i>
      <h3>No Messages</h3>
      <p>No contact messages found</p>
    </div>

    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Status</th>
            <th>From</th>
            <th>Subject</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="message in paginatedMessages" :key="message.id" :class="{ unread: message.status === 'unread' }">
            <td class="status-cell">
              <span class="status-badge" :class="getStatusClass(message.status)">
                <i :class="getStatusIcon(message.status)"></i>
                {{ formatStatus(message.status) }}
              </span>
            </td>
            <td class="from-cell">
              <strong>{{ message.name }}</strong>
              <small>{{ message.email }}</small>
            </td>
            <td class="subject-cell">{{ message.subject }}</td>
            <td class="date-cell">{{ formatDate(message.created_at) }}</td>
            <td class="actions-cell">
              <button @click="viewMessage(message)" class="btn-view" title="View Details">
                <i class="fas fa-eye"></i>
              </button>
              <button @click="openReplyModal(message)" class="btn-reply" title="Reply">
                <i class="fas fa-reply"></i>
              </button>
              <button @click="deleteMessage(message.id)" class="btn-delete" title="Delete">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="pagination">
      <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1" class="pagination-btn">
        <i class="fas fa-chevron-left"></i> Previous
      </button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages" class="pagination-btn">
        Next <i class="fas fa-chevron-right"></i>
      </button>
    </div>

    <!-- View Message Modal -->
    <div v-if="showViewModal" class="modal-overlay" @click.self="closeViewModal">
      <div class="modal-container modal-medium">
        <div class="modal-header">
          <h2>Message from {{ selectedMessage?.name }}</h2>
          <button @click="closeViewModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="message-details">
            <div class="detail-row">
              <strong>From:</strong> {{ selectedMessage?.name }} ({{ selectedMessage?.email }})
            </div>
            <div class="detail-row">
              <strong>Subject:</strong> {{ selectedMessage?.subject }}
            </div>
            <div class="detail-row">
              <strong>Date:</strong> {{ formatFullDate(selectedMessage?.created_at) }}
            </div>
            <div class="detail-row">
              <strong>Status:</strong>
              <span class="status-badge" :class="getStatusClass(selectedMessage?.status)">
                {{ formatStatus(selectedMessage?.status) }}
              </span>
            </div>
            <div class="message-content">
              <strong>Message:</strong>
              <p>{{ selectedMessage?.message }}</p>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="markAsRead" class="btn btn-primary" v-if="selectedMessage?.status === 'unread'">
            Mark as Read
          </button>
          <button @click="openReplyModal(selectedMessage)" class="btn btn-primary">
            <i class="fas fa-reply"></i> Reply
          </button>
          <button @click="closeViewModal" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>

    <!-- Reply Modal -->
    <div v-if="showReplyModal" class="modal-overlay" @click.self="closeReplyModal">
      <div class="modal-container modal-medium">
        <div class="modal-header">
          <h2>Reply to {{ replyingTo?.name }}</h2>
          <button @click="closeReplyModal" class="close-btn">×</button>
        </div>
        <form @submit.prevent="sendReply" class="modal-form">
          <div class="form-group">
            <label class="form-label">To:</label>
            <input type="email" :value="replyingTo?.email" class="form-input" disabled>
          </div>
          <div class="form-group">
            <label class="form-label">Subject:</label>
            <input type="text" :value="`Re: ${replyingTo?.subject}`" class="form-input" disabled>
          </div>
          <div class="form-group">
            <label class="form-label">Reply Message:</label>
            <textarea v-model="replyMessageText" class="form-textarea" rows="6" required placeholder="Type your reply here..."></textarea>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn btn-primary" :disabled="sendingReply">
              <i v-if="sendingReply" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-paper-plane"></i>
              {{ sendingReply ? 'Sending...' : 'Send Reply' }}
            </button>
            <button type="button" @click="closeReplyModal" class="btn btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import { toast } from 'vue3-toastify'
import api from '@/services/api'

// State
const messages = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const showViewModal = ref(false)
const showReplyModal = ref(false)
const selectedMessage = ref(null)
const replyingTo = ref(null)
const replyMessageText = ref('')
const sendingReply = ref(false)

const filters = ref({
  search: '',
  status: ''
})

const stats = ref({
  total: 0,
  unread: 0
})

// Computed
const filteredMessages = computed(() => {
  let result = [...messages.value]
  
  if (filters.value.status) {
    result = result.filter(m => m.status === filters.value.status)
  }
  
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(m => 
      m.name.toLowerCase().includes(search) ||
      m.email.toLowerCase().includes(search) ||
      m.subject.toLowerCase().includes(search) ||
      m.message.toLowerCase().includes(search)
    )
  }
  
  return result
})

const totalPages = computed(() => Math.ceil(filteredMessages.value.length / pageSize.value))
const paginatedMessages = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredMessages.value.slice(start, start + pageSize.value)
})

// Methods
const loadStats = async () => {
  try {
    const response = await api.get('/admin/contacts/stats')
    stats.value = response.data
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const loadMessages = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/contacts')
    messages.value = response.data
    await loadStats()
  } catch (error) {
    console.error('Error loading messages:', error)
    toast.error('Failed to load messages')
  } finally {
    loading.value = false
  }
}

const viewMessage = (message) => {
  selectedMessage.value = message
  showViewModal.value = true
}

const markAsRead = async () => {
  try {
    await api.put(`/admin/contacts/${selectedMessage.value.id}/status`, { status: 'read' })
    selectedMessage.value.status = 'read'
    await loadMessages()
    toast.success('Message marked as read')
  } catch (error) {
    console.error('Error marking as read:', error)
    toast.error('Failed to update status')
  }
}

const openReplyModal = (message) => {
  replyingTo.value = message
  replyMessageText.value = ''
  showViewModal.value = false
  showReplyModal.value = true
}

const sendReply = async () => {
  if (!replyMessageText.value.trim()) {
    toast.error('Please enter a reply message')
    return
  }
  
  sendingReply.value = true
  try {
    await api.post(`/admin/contacts/${replyingTo.value.id}/reply`, {
      reply_message: replyMessageText.value
    })
    toast.success('Reply sent successfully')
    closeReplyModal()
    await loadMessages()
  } catch (error) {
    console.error('Error sending reply:', error)
    toast.error('Failed to send reply')
  } finally {
    sendingReply.value = false
  }
}

const deleteMessage = async (id) => {
  if (confirm('Delete this message?')) {
    try {
      await api.delete(`/admin/contacts/${id}`)
      toast.success('Message deleted')
      await loadMessages()
    } catch (error) {
      console.error('Error deleting message:', error)
      toast.error('Failed to delete message')
    }
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const getStatusClass = (status) => {
  const classes = {
    unread: 'status-unread',
    read: 'status-read',
    replied: 'status-replied',
    archived: 'status-archived'
  }
  return classes[status] || 'status-unread'
}

const getStatusIcon = (status) => {
  const icons = {
    unread: 'fas fa-circle',
    read: 'fas fa-check-circle',
    replied: 'fas fa-reply-all',
    archived: 'fas fa-archive'
  }
  return icons[status] || 'fas fa-envelope'
}

const formatStatus = (status) => {
  const statuses = {
    unread: 'Unread',
    read: 'Read',
    replied: 'Replied',
    archived: 'Archived'
  }
  return statuses[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const formatFullDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const debouncedSearch = useDebounceFn(() => {
  currentPage.value = 1
}, 300)

const closeViewModal = () => {
  showViewModal.value = false
  selectedMessage.value = null
}

const closeReplyModal = () => {
  showReplyModal.value = false
  replyingTo.value = null
  replyMessageText.value = ''
}

onMounted(() => {
  loadMessages()
})
</script>

<style scoped>
.contact-management {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header h2 {
  color: #1e3a8a;
  margin: 0;
}

.stats-badges {
  display: flex;
  gap: 0.75rem;
}

.stat-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-badge.unread {
  background: #fee2e2;
  color: #991b1b;
}

.stat-badge.total {
  background: #e0e7ff;
  color: #1e40af;
}

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  flex: 1;
  min-width: 200px;
}

.search-box input {
  border: none;
  background: none;
  outline: none;
  width: 100%;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
}

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

.data-table tr.unread {
  background: #fef3c7;
}

.from-cell {
  display: flex;
  flex-direction: column;
}

.from-cell small {
  font-size: 0.7rem;
  color: #666;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 500;
}

.status-unread {
  background: #fee2e2;
  color: #991b1b;
}

.status-read {
  background: #d1fae5;
  color: #065f46;
}

.status-replied {
  background: #dbeafe;
  color: #1e40af;
}

.status-archived {
  background: #f3f4f6;
  color: #374151;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.btn-view, .btn-reply, .btn-delete {
  background: none;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn-view {
  background: #3b82f6;
  color: white;
}

.btn-reply {
  background: #10b981;
  color: white;
}

.btn-delete {
  background: #ef4444;
  color: white;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.pagination-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-medium {
  max-width: 550px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  color: #1e3a8a;
  margin: 0;
  font-size: 1.2rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.modal-body, .modal-form {
  padding: 1.5rem;
}

.detail-row {
  margin-bottom: 0.75rem;
}

.message-content {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.message-content p {
  margin-top: 0.5rem;
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  white-space: pre-wrap;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: #f59e0b;
  color: white;
}

.btn-secondary {
  background: #e5e7eb;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}
</style>
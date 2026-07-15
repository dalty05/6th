<template>
  <div class="partner-management">
    <!-- Header -->
    <div class="management-header">
      <div class="header-left">
        <h1>Partner Management</h1>
        <p>Manage marketing partners, track performance, and monitor referral activity</p>
      </div>
      <button @click="openCreateModal" class="btn-create">
        <i class="fas fa-plus"></i> Add Partner
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <h3>{{ partners.length }}</h3>
          <p>Total Partners</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green"><i class="fas fa-user-check"></i></div>
        <div class="stat-info">
          <h3>{{ activePartners }}</h3>
          <p>Active Partners</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange"><i class="fas fa-link"></i></div>
        <div class="stat-info">
          <h3>{{ totalReferralLinks }}</h3>
          <p>Referral Links</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple"><i class="fas fa-mouse-pointer"></i></div>
        <div class="stat-info">
          <h3>{{ formatNumber(totalReferralClicks) }}</h3>
          <p>Total Clicks</p>
        </div>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="filters-bar">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search partners by name or email..."
          @input="currentPage = 1"
        >
      </div>
      <select v-model="statusFilter" class="filter-select" @change="currentPage = 1">
        <option value="all">All Status</option>
        <option value="active">Active Only</option>
        <option value="inactive">Inactive Only</option>
      </select>
      <select v-model="sortBy" class="filter-select" @change="currentPage = 1">
        <option value="clicks">Sort by Clicks</option>
        <option value="links">Sort by Links</option>
        <option value="newest">Sort by Newest</option>
        <option value="oldest">Sort by Oldest</option>
      </select>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading partners...</p>
    </div>

    <!-- Partners Table -->
    <div v-else class="table-container">
      <table class="partners-table">
        <thead>
          <tr>
            <th>Partner</th>
            <th>Contact</th>
            <th>Status</th>
            <th>Referral Code</th>
            <th>Links</th>
            <th>Clicks</th>
            <th>Unique</th>
            <th>Joined</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="partner in paginatedPartners" :key="partner.id">
            <td class="partner-cell">
              <div class="partner-avatar">
                <i class="fas fa-user-circle"></i>
                <strong>{{ partner.full_name }}</strong>
              </div>
            </td>
            <td class="contact-cell">
              <div>{{ partner.email }}</div>
            </td>
            <td>
              <span :class="['status-badge', partner.is_active ? 'active' : 'inactive']">
                {{ partner.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <div class="referral-code-cell" v-if="partner.referral_code">
                <code>{{ partner.referral_code }}</code>
                <button @click="copyReferralCode(partner.referral_code)" class="copy-btn" title="Copy code">
                  <i class="fas fa-copy"></i>
                </button>
              </div>
              <span v-else class="no-code">Not generated</span>
            </td>
            <td class="number-cell">{{ partner.link_count || 0 }}</td>
            <td class="number-cell">{{ formatNumber(partner.total_clicks || 0) }}</td>
            <td class="number-cell">{{ formatNumber(partner.unique_clicks || 0) }}</td>
            <td>{{ formatDate(partner.created_at) }}</td>
            <td class="actions-cell">
              <div class="action-buttons">
                <button @click="viewPartnerDetails(partner)" class="action-icon view" title="View Details">
                  <i class="fas fa-eye"></i>
                </button>
                <button @click="editPartner(partner)" class="action-icon edit" title="Edit">
                  <i class="fas fa-edit"></i>
                </button>
                <button v-if="partner.is_active" @click="openSuspendModal(partner)" class="action-icon suspend" title="Suspend">
                  <i class="fas fa-ban"></i>
                </button>
                <button v-if="!partner.is_active" @click="activatePartner(partner.id)" class="action-icon activate" title="Activate">
                  <i class="fas fa-play-circle"></i>
                </button>
                <button @click="resetPartnerPassword(partner.id)" class="action-icon reset" title="Reset Password">
                  <i class="fas fa-key"></i>
                </button>
                <button v-if="partner.id !== currentUserId" @click="deletePartner(partner.id)" class="action-icon delete" title="Delete">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredPartners.length === 0">
            <td colspan="9" class="empty-row">No partners found</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="filteredPartners.length > 0">
      <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">
        <i class="fas fa-chevron-left"></i> Previous
      </button>
      <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">
        Next <i class="fas fa-chevron-right"></i>
      </button>
    </div>

    <!-- Create/Edit Partner Modal -->
    <div class="modal-overlay" v-if="showModal" @click.self="closeModal">
      <div class="modal-container">
        <div class="modal-header">
          <h2>{{ editingPartner ? 'Edit Partner' : 'Add New Partner' }}</h2>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <form @submit.prevent="savePartner" class="partner-form">
          <div class="form-group">
            <label>Full Name *</label>
            <input type="text" v-model="form.full_name" required>
          </div>
          <div class="form-group">
            <label>Email *</label>
            <input type="email" v-model="form.email" required :disabled="!!editingPartner">
          </div>
          <div class="checkbox-group">
            <label class="checkbox">
              <input type="checkbox" v-model="form.is_active"> Active
            </label>
          </div>
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-cancel">Cancel</button>
            <button type="submit" class="btn-submit">{{ editingPartner ? 'Update' : 'Create Partner' }}</button>
          </div>
        </form>
        <div v-if="newPartnerPassword" class="password-info">
          <hr>
          <h4>Partner Created Successfully!</h4>
          <p><strong>Temporary Password:</strong> <code>{{ newPartnerPassword }}</code></p>
          <p class="warning">Please share this password with the partner. It will not be shown again.</p>
        </div>
      </div>
    </div>

    <!-- View Details Modal -->
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
              <span class="detail-label">Status:</span>
              <span :class="['status-badge', selectedPartner.is_active ? 'active' : 'inactive']">
                {{ selectedPartner.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Joined:</span>
              <span class="detail-value">{{ formatDate(selectedPartner.created_at) }}</span>
            </div>
          </div>

          <div class="detail-section">
            <h4>Referral Statistics</h4>
            <div class="detail-row">
              <span class="detail-label">Referral Code:</span>
              <code class="referral-code">{{ selectedPartner.referral_code || 'Not generated' }}</code>
            </div>
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
                  <span><i class="fas fa-mouse-pointer"></i> {{ formatNumber(link.total_clicks || 0) }} clicks</span>
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

    <!-- Suspend Reason Modal -->
    <div class="modal-overlay" v-if="showSuspendModal" @click.self="closeSuspendModal">
      <div class="modal-container small">
        <div class="modal-header">
          <h2>Suspend Partner</h2>
          <button class="close-btn" @click="closeSuspendModal">&times;</button>
        </div>
        <div class="modal-body">
          <p>You are about to suspend <strong>{{ suspendPartnerData?.full_name }}</strong></p>
          <div class="form-group">
            <label>Reason for suspension *</label>
            <textarea v-model="suspendReason" rows="4" placeholder="Please provide a reason for suspending this partner..."></textarea>
          </div>
          <div class="form-actions">
            <button @click="closeSuspendModal" class="btn-cancel">Cancel</button>
            <button @click="confirmSuspend" class="btn-danger" :disabled="!suspendReason.trim()">
              Confirm Suspension
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Notification Toast -->
    <div v-if="notification.show" :class="['notification', notification.type]" @click="notification.show = false">
      <i :class="notification.icon"></i>
      <span>{{ notification.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { toast } from 'vue3-toastify'
import api from '@/services/api'
import authService from '@/services/auth'

// State
const partners = ref([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('all')
const sortBy = ref('clicks')
const currentPage = ref(1)
const itemsPerPage = 15

// Modals
const showModal = ref(false)
const showDetailsModal = ref(false)
const showSuspendModal = ref(false)
const editingPartner = ref(null)
const selectedPartner = ref(null)
const suspendPartnerData = ref(null)
const suspendReason = ref('')
const newPartnerPassword = ref('')

// Form data
const form = ref({
  full_name: '',
  email: '',
  is_active: true
})

// Current user
const currentUser = authService.getUser()
const currentUserId = computed(() => currentUser?.id)

// Notification
const notification = ref({
  show: false,
  message: '',
  type: 'success',
  icon: 'fas fa-check-circle'
})

const showNotification = (message, type = 'success') => {
  notification.value = { show: true, message, type, icon: type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle' }
  setTimeout(() => notification.value.show = false, 3000)
}

// Computed
const activePartners = computed(() => partners.value.filter(p => p.is_active).length)
const totalReferralLinks = computed(() => partners.value.reduce((sum, p) => sum + (p.link_count || 0), 0))
const totalReferralClicks = computed(() => partners.value.reduce((sum, p) => sum + (p.total_clicks || 0), 0))

const filteredPartners = computed(() => {
  let filtered = [...partners.value]
  
  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p => 
      p.full_name.toLowerCase().includes(query) || 
      p.email.toLowerCase().includes(query)
    )
  }
  
  // Status filter
  if (statusFilter.value === 'active') {
    filtered = filtered.filter(p => p.is_active === true)
  } else if (statusFilter.value === 'inactive') {
    filtered = filtered.filter(p => p.is_active === false)
  }
  
  // Sort
  if (sortBy.value === 'clicks') {
    filtered.sort((a, b) => (b.total_clicks || 0) - (a.total_clicks || 0))
  } else if (sortBy.value === 'links') {
    filtered.sort((a, b) => (b.link_count || 0) - (a.link_count || 0))
  } else if (sortBy.value === 'newest') {
    filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } else if (sortBy.value === 'oldest') {
    filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  }
  
  return filtered
})

const totalPages = computed(() => Math.ceil(filteredPartners.value.length / itemsPerPage))
const paginatedPartners = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredPartners.value.slice(start, start + itemsPerPage)
})

// Methods
const loadPartners = async () => {
  loading.value = true
  try {
    // Get ALL users first, then filter by role 'partner'
    const response = await api.get('/admin/users')
    const allUsers = response.data
    
    // Filter to only show partners
    const partnersData = allUsers.filter(user => user.role === 'partner')
    
    // Get additional stats for each partner
    for (const partner of partnersData) {
      try {
        const statsRes = await api.get(`/admin/referral/partner/${partner.id}/stats`)
        partner.link_count = statsRes.data.total_links || 0
        partner.total_clicks = statsRes.data.total_clicks || 0
        partner.unique_clicks = statsRes.data.total_unique_clicks || 0
        partner.referral_links = statsRes.data.links || []
      } catch (e) {
        partner.link_count = 0
        partner.total_clicks = 0
        partner.unique_clicks = 0
        partner.referral_links = []
      }
    }
    
    partners.value = partnersData
  } catch (error) {
    showNotification('Failed to load partners', 'error')
  } finally {
    loading.value = false
  }
}

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = 'all'
  sortBy.value = 'clicks'
  currentPage.value = 1
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const openCreateModal = () => {
  editingPartner.value = null
  newPartnerPassword.value = ''
  form.value = { full_name: '', email: '', is_active: true }
  showModal.value = true
}

const editPartner = (partner) => {
  editingPartner.value = partner
  form.value = {
    full_name: partner.full_name,
    email: partner.email,
    is_active: partner.is_active
  }
  showModal.value = true
}

const viewPartnerDetails = (partner) => {
  selectedPartner.value = partner
  showDetailsModal.value = true
}

const savePartner = async () => {
  try {
    if (editingPartner.value) {
      // Update existing partner
      await api.put(`/admin/users/${editingPartner.value.id}`, {
        full_name: form.value.full_name,
        role: 'partner',
        is_active: form.value.is_active
      })
      showNotification('Partner updated successfully')
    } else {
      // Create new partner
      const response = await api.post('/admin/users', {
        full_name: form.value.full_name,
        email: form.value.email,
        role: 'partner',
        is_active: form.value.is_active,
        is_approved: true
      })
      newPartnerPassword.value = response.data.user?.temporary_password
      showNotification('Partner created successfully')
    }
    closeModal()
    await loadPartners()
  } catch (error) {
    showNotification(error.response?.data?.error || 'Failed to save partner', 'error')
  }
}

const openSuspendModal = (partner) => {
  suspendPartnerData.value = partner
  suspendReason.value = ''
  showSuspendModal.value = true
}

const confirmSuspend = async () => {
  if (!suspendReason.value.trim()) {
    showNotification('Please provide a reason for suspension', 'error')
    return
  }
  
  try {
    await api.post(`/admin/users/${suspendPartnerData.value.id}/suspend`, {
      reason: suspendReason.value
    })
    showNotification('Partner suspended successfully')
    closeSuspendModal()
    await loadPartners()
  } catch (error) {
    showNotification('Failed to suspend partner', 'error')
  }
}

const activatePartner = async (userId) => {
  try {
    await api.post(`/admin/users/${userId}/activate`)
    showNotification('Partner activated successfully')
    await loadPartners()
  } catch (error) {
    showNotification('Failed to activate partner', 'error')
  }
}

const resetPartnerPassword = async (userId) => {
  if (confirm('Reset password for this partner? A new password will be emailed to them.')) {
    try {
      await api.post(`/admin/users/${userId}/reset-password`)
      showNotification('Password reset email sent to partner')
    } catch (error) {
      showNotification('Failed to reset password', 'error')
    }
  }
}

const deletePartner = async (userId) => {
  if (confirm('⚠️ WARNING: This will permanently delete this partner and all their data. This action cannot be undone. Are you sure?')) {
    try {
      await api.delete(`/admin/users/${userId}`)
      showNotification('Partner deleted successfully')
      await loadPartners()
    } catch (error) {
      showNotification('Failed to delete partner', 'error')
    }
  }
}

const copyReferralCode = (code) => {
  navigator.clipboard.writeText(code)
  showNotification('Referral code copied to clipboard')
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

const closeModal = () => {
  showModal.value = false
  editingPartner.value = null
  newPartnerPassword.value = ''
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedPartner.value = null
}

const closeSuspendModal = () => {
  showSuspendModal.value = false
  suspendPartnerData.value = null
  suspendReason.value = ''
}

onMounted(() => {
  loadPartners()
})
</script>

<style scoped>
.partner-management {
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
  font-size: 1.5rem;
  color: #1e3a8a;
  margin: 0 0 0.25rem;
}

.header-left p {
  color: #6b7280;
  margin: 0;
  font-size: 0.85rem;
}

.btn-create {
  background: #1e3a8a;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-create:hover {
  background: #f59e0b;
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
  font-size: 0.85rem;
}

.filter-select {
  padding: 0.6rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 0.85rem;
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

/* Table Styles */
.table-container {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow-x: auto;
}

.partners-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.partners-table th {
  text-align: left;
  padding: 1rem;
  background: #f8fafc;
  font-weight: 600;
  color: #1e3a8a;
  border-bottom: 1px solid #e5e7eb;
}

.partners-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.partners-table tr:hover {
  background: #f8fafc;
}

.partner-cell .partner-avatar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.partner-avatar i {
  font-size: 1.5rem;
  color: #9ca3af;
}

.partner-avatar strong {
  color: #1e3a8a;
}

.contact-cell div {
  display: flex;
  flex-direction: column;
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

.referral-code-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.referral-code-cell code {
  font-family: monospace;
  background: #f1f5f9;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
}

.no-code {
  color: #9ca3af;
  font-style: italic;
  font-size: 0.75rem;
}

.number-cell {
  font-weight: 500;
  text-align: center;
}

.copy-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #f59e0b;
  transition: color 0.2s;
  padding: 0.25rem;
}

.copy-btn:hover {
  color: #d97706;
}

.actions-cell {
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.35rem;
  border-radius: 6px;
  transition: all 0.2s;
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.action-icon.view { color: #3b82f6; }
.action-icon.edit { color: #f59e0b; }
.action-icon.suspend { color: #8b5cf6; }
.action-icon.activate { color: #10b981; }
.action-icon.reset { color: #6b7280; }
.action-icon.delete { color: #ef4444; }

.action-icon:hover {
  background: #f1f5f9;
  transform: scale(1.05);
}

.empty-row {
  text-align: center;
  padding: 3rem;
  color: #9ca3af;
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
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #1e3a8a;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-container.large { max-width: 700px; }
.modal-container.small { max-width: 450px; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 { margin: 0; color: #1e3a8a; font-size: 1.25rem; }

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #9ca3af;
}

.close-btn:hover {
  color: #ef4444;
}

.partner-form, .modal-body { padding: 1.25rem; }

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; margin-bottom: 0.25rem; font-weight: 500; font-size: 0.8rem; color: #374151; }
.form-group input, .form-group textarea { width: 100%; padding: 0.6rem; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 0.85rem; }

.checkbox-group { margin-bottom: 1rem; }
.checkbox { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-size: 0.85rem; }

.form-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1rem; }
.btn-cancel { background: #e5e7eb; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }
.btn-submit { background: #1e3a8a; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }
.btn-danger { background: #dc2626; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }
.btn-secondary { background: #e5e7eb; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; }

.modal-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
}

.detail-section { margin-bottom: 1.5rem; }
.detail-section h4 { color: #1e3a8a; margin: 0 0 0.75rem; font-size: 0.9rem; }
.detail-row { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9; }
.detail-label { font-weight: 500; color: #6b7280; }
.detail-value { color: #374151; }

.referral-code { font-family: monospace; background: #f1f5f9; padding: 0.2rem 0.5rem; border-radius: 4px; }

.links-list { display: flex; flex-direction: column; gap: 0.5rem; }
.link-item { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: #f8fafc; border-radius: 8px; }

.password-info { padding: 1rem; background: #f0fdf4; border-top: 1px solid #e5e7eb; }
.password-info code { background: white; padding: 0.2rem 0.5rem; border-radius: 4px; }
.warning { color: #f59e0b; font-size: 0.75rem; margin-top: 0.5rem; }

/* Notification */
.notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 1000;
  animation: slideIn 0.3s ease;
  cursor: pointer;
}

.notification.success { background: #10b981; color: white; }
.notification.error { background: #ef4444; color: white; }

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

/* Responsive */
@media (max-width: 1024px) {
  .partners-table {
    font-size: 0.75rem;
  }
  
  .partners-table th,
  .partners-table td {
    padding: 0.5rem;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filters-bar {
    flex-direction: column;
  }
  
  .table-container {
    overflow-x: scroll;
  }
  
  .partners-table {
    min-width: 800px;
  }
}
</style>